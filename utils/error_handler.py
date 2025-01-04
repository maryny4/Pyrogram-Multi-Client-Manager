from datetime import datetime
from typing import Dict, Any, Tuple

from pyrogram import Client
from pyrogram.errors import (
    FloodWait, BadRequest, Unauthorized, Forbidden,
    NotAcceptable, InternalServerError
)
from pyrogram.raw import functions

from utils.logger import get_logger


class EnhancedErrorHandler:
    def __init__(self, client: Client, logger_name: str, sleep_threshold: int = 10):
        """
        Extended error handler with MTProto support.

        Args:
            client: Instance of Pyrogram client.
            logger_name: Name for the logger.
            sleep_threshold: Threshold for automatic FloodWait handling.
        """
        self.client = client
        self.logger = get_logger(logger_name)
        self.sleep_threshold = sleep_threshold
        self.error_stats = {
            'flood_wait_counts': 0,
            'last_flood_wait': None,
            'total_errors': 0,
            'error_types': {},
            'client_info': {
                'session_name': client.name,
                'type': 'bot' if client.bot_token else 'user',
                'device_model': client.device_model,
                'app_version': client.app_version,
                'system_version': client.system_version
            }
        }

    def _update_stats(self, error: Exception) -> None:
        """Update error statistics."""
        self.error_stats['total_errors'] += 1
        error_type = type(error).__name__
        self.error_stats['error_types'][error_type] = self.error_stats['error_types'].get(error_type, 0) + 1

    async def handle_error(self, error: Exception) -> Tuple[bool, int]:
        """
        Handle errors using MTProto API.

        Args:
            error: Exception object.

        Returns:
            tuple: (should_retry, delay_in_seconds)
        """
        self._update_stats(error)

        # Check client type for specific error handling
        is_bot = bool(self.client.bot_token)

        if isinstance(error, FloodWait):
            self.error_stats['flood_wait_counts'] += 1
            self.error_stats['last_flood_wait'] = datetime.now()

            # If value is below threshold, handle automatically
            if error.value <= self.sleep_threshold:
                self.logger.warning(
                    f"FloodWait below threshold ({error.value}s <= {self.sleep_threshold}s), "
                    f"handling automatically. Total flood waits: {self.error_stats['flood_wait_counts']}"
                )
            else:
                self.logger.error(
                    f"FloodWait above threshold ({error.value}s > {self.sleep_threshold}s), "
                    f"manual intervention may be required. Total flood waits: {self.error_stats['flood_wait_counts']}"
                )
            return True, error.value

        if isinstance(error, BadRequest):
            try:
                error_info = await self.client.invoke(functions.help.GetConfig())
                self.logger.error(
                    f"BadRequest error for {self.client.name} ({self.error_stats['client_info']['type']}). "
                    f"DC: {error_info.dc_id}, This DC: {error_info.this_dc}. Error: {str(error)}"
                )
            except Exception as e:
                self.logger.error(f"Failed to get error details: {e}")
            return False, 0

        if isinstance(error, Unauthorized):
            try:
                if is_bot:
                    self.logger.error(f"Bot token validation failed for {self.client.name}")
                else:
                    auth_status = await self.client.invoke(functions.auth.LogOut())
                    self.logger.error(
                        f"Authorization failed for user {self.client.name}. Status: {auth_status}"
                    )
            except Exception as e:
                self.logger.error(f"Failed to check auth status: {e}")
            return False, 0

        if isinstance(error, (Forbidden, NotAcceptable)):
            self.logger.error(
                f"Permission error for {self.client.name} "
                f"({self.error_stats['client_info']['type']}): {error}"
            )
            return False, 0

        if isinstance(error, InternalServerError):
            try:
                server_status = await self.client.invoke(functions.help.GetNearestDc())
                self.logger.error(
                    f"Internal server error for {self.client.name}. "
                    f"Nearest DC: {server_status.nearest_dc}, "
                    f"Current DC: {server_status.this_dc}"
                )
            except Exception as e:
                self.logger.error(f"Failed to get server status: {e}")
            return True, 5

        self.logger.error(
            f"Unhandled error type {type(error).__name__} for {self.client.name}: {str(error)}"
        )
        return True, 3

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.copy()
