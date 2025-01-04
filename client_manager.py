# client_manager.py

import asyncio
import importlib
from typing import Optional, Dict, Any, Tuple

from pyrogram import Client, enums
from pyrogram.errors import (
    FloodWait
)

from config.settings import ClientConfig
from utils.error_handler import EnhancedErrorHandler
from utils.logger import get_logger
from utils.message_formatter import MessageFormatter
from utils.session_manager import SessionManager, SessionType


class ClientManager:
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    def __init__(self, config: ClientConfig):
        """
        Initialize the client manager with extended capabilities.

        Args:
            config: Client configuration.
        """
        self.config = config
        self.logger = get_logger(f"{config.type}_{config.session_name}")
        self.client: Optional[Client] = None
        self.scheduler = None
        self._retry_count = 0
        self._is_stopping = False

        # Additional managers will be initialized after creating the client
        self.error_handler: Optional[EnhancedErrorHandler] = None
        self.session_manager: Optional[SessionManager] = None
        self.message_formatter: Optional[MessageFormatter] = None

    def _build_client_config(self) -> Dict[str, Any]:
        """Build the configuration for the Pyrogram client."""
        config = {
            "name": self.config.session_name,
            "api_id": self.config.api_id,
            "api_hash": self.config.api_hash,
            "app_version": self.config.app_version,
            "device_model": self.config.device_model,
            "system_version": self.config.system_version,
            "lang_code": self.config.lang_code,
            "ipv6": self.config.ipv6,
            "proxy": self.config.proxy,
            "test_mode": self.config.test_mode,
            "bot_token": self.config.bot_token,
            "session_string": self.config.session_string,
            "in_memory": self.config.in_memory,
            "phone_number": self.config.phone_number,
            "phone_code": self.config.phone_code,
            "password": self.config.password,
            "workers": self.config.workers,
            "workdir": self.config.workdir,
            "parse_mode": (
                enums.ParseMode.HTML
                if self.config.parse_mode.upper() == "HTML"
                else enums.ParseMode.DEFAULT
            ),
            "no_updates": self.config.no_updates,
            "takeout": self.config.takeout,
            "sleep_threshold": self.config.sleep_threshold,
            "hide_password": self.config.hide_password,
            "max_concurrent_transmissions": self.config.max_concurrent_transmissions,
        }

        if self.config.plugins.enabled:
            config["plugins"] = {
                "root": self.config.plugins.root,
                "include": self.config.plugins.include,
                "exclude": self.config.plugins.exclude,
            }

        return config

    async def _init_client(self) -> Client:
        """Initialize the client and all additional managers."""
        try:
            # Create the client
            client_config = self._build_client_config()
            self.client = Client(**client_config)

            # Initialize additional managers
            self.error_handler = EnhancedErrorHandler(
                self.client,
                f"ErrorHandler_{self.config.session_name}",
                self.config.sleep_threshold
            )

            self.session_manager = SessionManager(
                self.client,
                SessionType.MEMORY if self.config.in_memory else SessionType.FILE
            )

            self.message_formatter = MessageFormatter(self.client)

            # Initialize the session
            if not await self.session_manager.initialize_session():
                raise Exception("Failed to initialize session")

            return self.client

        except Exception as e:
            self.logger.error(f"Failed to initialize client: {e}")
            raise

    async def _handle_error(self, error: Exception) -> Tuple[bool, int]:
        """Handle errors using EnhancedErrorHandler."""
        if self.error_handler:
            return await self.error_handler.handle_error(error)
        # Fallback to basic handling if error_handler is not initialized
        self.logger.error(f"Error handler not initialized, using basic error handling: {error}")
        if isinstance(error, FloodWait):
            return True, error.value
        return True, self.RETRY_DELAY

    async def start(self):
        """Start the client with error handling and retries."""
        while not self._is_stopping and self._retry_count < self.MAX_RETRIES:
            try:
                if not self.client:
                    self.client = await self._init_client()

                if not self.client.is_connected:
                    await self.client.start()

                me = await self.client.get_me()
                self.logger.info(
                    f"Started as {me.first_name or '???'} "
                    f"(ID: {me.id}, Type: {self.config.type})"
                )

                self.scheduler = await self._init_scheduler()
                if self.scheduler:
                    self.logger.info("Scheduler initialized")

                self._retry_count = 0
                return True

            except Exception as e:
                should_retry, delay = await self._handle_error(e)
                if not should_retry:
                    return False

                if not self._is_stopping:
                    await asyncio.sleep(delay)
                    self._retry_count += 1

        if not self._is_stopping:
            self.logger.error(f"Failed to start after {self.MAX_RETRIES} attempts")
        return False

    async def _init_scheduler(self):
        """Initialize the scheduler for periodic tasks."""
        if not self.config.periodic_tasks.enabled:
            return None

        try:
            module = importlib.import_module(self.config.periodic_tasks.schedule_module)
            schedule_function = getattr(module, self.config.periodic_tasks.schedule_function)

            return schedule_function(
                self.client,
                self.config.periodic_tasks.tasks
            )
        except Exception as e:
            self.logger.error(f"Scheduler initialization failed: {e}")
            return None

    async def stop(self):
        """Gracefully shutdown the client and all components."""
        self._is_stopping = True
        try:
            if self.scheduler:
                self.logger.info("Stopping scheduler...")
                try:
                    self.scheduler.shutdown(wait=True)
                    self.logger.info("Scheduler stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping scheduler: {e}")

            if self.client and self.client.is_connected:
                self.logger.info("Stopping client...")
                try:
                    await self.client.stop()
                    self.logger.info("Client stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping client: {e}")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.client = None
            self.scheduler = None
            self.error_handler = None
            self.session_manager = None
            self.message_formatter = None
            self._is_stopping = False

    def get_formatter(self) -> Optional[MessageFormatter]:
        """Get the message formatter."""
        return self.message_formatter
