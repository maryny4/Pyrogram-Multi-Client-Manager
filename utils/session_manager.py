from enum import Enum
from typing import Optional, Dict, Any

from pyrogram import Client

from utils.logger import get_logger


class SessionType(Enum):
    FILE = "file"
    MEMORY = "memory"
    STRING = "string"


class SessionManager:
    def __init__(self, client: Client, session_type: SessionType = SessionType.FILE):
        """
        Pyrogram session manager.

        Args:
            client: Instance of Pyrogram client.
            session_type: Type of session (file/memory/string).
        """
        self.client = client
        self.session_type = session_type
        self.logger = get_logger(f"SessionManager_{client.name}")
        self.session_string: Optional[str] = None

        # Save important client parameters
        self._client_config = {
            'name': client.name,
            'type': 'bot' if client.bot_token else 'user',
            'workdir': getattr(client, 'workdir', 'sessions'),
            'test_mode': getattr(client, 'test_mode', False),
            'device_model': client.device_model,
            'system_version': client.system_version,
            'app_version': client.app_version,
            'lang_code': client.lang_code,
            'ipv6': getattr(client, 'ipv6', False),
            'in_memory': getattr(client, 'in_memory', False)
        }

    async def initialize_session(self) -> bool:
        """
        Initialize the session based on the type.

        Returns:
            bool: Success of initialization.
        """
        try:
            if self.session_type == SessionType.MEMORY:
                self.client.in_memory = True
                self.logger.info(f"Initialized in-memory session for {self._get_client_info()}")
                return True

            elif self.session_type == SessionType.STRING:
                if not self.session_string:
                    self.session_string = await self.export_session()
                    if self.session_string:
                        self.logger.info(f"Session string exported for {self._get_client_info()}")
                        return True
                    return False
                return True

            elif self.session_type == SessionType.FILE:
                file_path = f"{self._client_config['workdir']}/{self.client.name}.session"
                self.logger.info(f"Using file-based session: {file_path} for {self._get_client_info()}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to initialize session for {self._get_client_info()}: {e}")
            return False

    async def export_session(self) -> Optional[str]:
        """
        Export the session to a string.

        Returns:
            Optional[str]: Session string or None on error.
        """
        try:
            if not self.client.is_connected:
                await self.client.start()

            session_string = await self.client.export_session_string()
            self.logger.info(f"Session exported successfully for {self._get_client_info()}")
            self.session_string = session_string
            return session_string

        except Exception as e:
            self.logger.error(f"Failed to export session for {self._get_client_info()}: {e}")
            return None

    async def import_session(self, session_string: str) -> bool:
        """
        Import the session from a string.

        Args:
            session_string: Session string to import.

        Returns:
            bool: Success of import.
        """
        try:
            if self.client.is_connected:
                await self.client.stop()

            # Check client type (bot/user) and set appropriate parameters
            self.client.session_string = session_string
            self.session_string = session_string

            # Verify connection
            await self.client.start()
            self.logger.info(f"Session imported and verified for {self._get_client_info()}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import session for {self._get_client_info()}: {e}")
            return False
        finally:
            if self.client.is_connected:
                await self.client.stop()

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.

        Returns:
            Dict[str, Any]: Session information.
        """
        return {
            "type": self.session_type.value,
            "client_info": self._client_config,
            "has_session_string": bool(self.session_string),
            "is_connected": self.client.is_connected,
            "workdir": self._client_config['workdir'],
            "test_mode": self._client_config['test_mode']
        }

    def _get_client_info(self) -> str:
        """Get client information for logs."""
        return (
            f"client {self.client.name} "
            f"({self._client_config['type']}, "
            f"app: {self._client_config['app_version']}, "
            f"device: {self._client_config['device_model']})"
        )
