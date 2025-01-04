# main.py

# !/usr/bin/env python3
import asyncio
import signal
from pathlib import Path
from typing import Dict, Optional

import uvloop

from client_manager import ClientManager
from config.settings import Config, ClientConfig
from utils.logger import get_logger


class PyrogramMultiClient:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the multi-client manager.

        Args:
            config_path: Path to the configuration file.
        """
        self.config = Config(config_path)
        self.managers: Dict[str, ClientManager] = {}
        self.main_logger = get_logger("PyrogramMultiClient")
        self.shutdown_event = asyncio.Event()

        # Set uvloop for improved performance
        uvloop.install()

        # Create necessary directories
        for directory in ["sessions", "logs"]:
            Path(directory).mkdir(exist_ok=True)

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._shutdown(s))
            )

    async def _shutdown(self, sig: Optional[signal.Signals] = None):
        """
        Gracefully shutdown all clients.

        Args:
            sig: Signal that triggered the shutdown.
        """
        if sig:
            self.main_logger.info(f"Received exit signal {sig.name}...")

        await self.stop_all()
        self.shutdown_event.set()

    async def _start_manager(self, client_config: ClientConfig) -> bool:
        """
        Start an individual client manager.

        Args:
            client_config: Client configuration.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Create the manager
            manager = ClientManager(client_config)
            success = await manager.start()

            if success:
                # Save the manager and its formatter
                self.managers[client_config.session_name] = manager
                formatter = manager.get_formatter()

                if formatter:
                    # Use formatter for system message
                    start_message = formatter.format_system_message(
                        f"Successfully started {client_config.type} client"
                    )
                    self.main_logger.info(start_message)
                else:
                    self.main_logger.info(
                        f"Successfully started {client_config.type} client: {client_config.session_name}"
                    )
            else:
                self.main_logger.error(
                    f"Failed to start {client_config.type} client: {client_config.session_name}"
                )

            return success

        except Exception as e:
            self.main_logger.error(
                f"Error starting {client_config.type} client {client_config.session_name}: {e}"
            )
            return False

    async def start_all(self):
        """Start all clients in parallel."""
        self.main_logger.info("Starting all clients...")

        # Group clients by type for logging
        clients_by_type = {
            "user": [],
            "bot": []
        }

        for client_config in self.config.clients:
            clients_by_type[client_config.type].append(client_config)

        # Start clients in parallel
        tasks = []
        for client_type, configs in clients_by_type.items():
            self.main_logger.info(f"Starting {len(configs)} {client_type} client(s)...")
            for config in configs:
                task = asyncio.create_task(
                    self._start_manager(config),
                    name=f"start_{config.session_name}"
                )
                tasks.append((config, task))

        # Await all tasks
        failed = 0
        for config, task in tasks:
            try:
                success = await task
                if not success:
                    failed += 1
            except Exception as e:
                self.main_logger.error(
                    f"Unexpected error starting {config.session_name}: {e}"
                )
                failed += 1

        total = len(tasks)
        success = total - failed
        self.main_logger.info(
            f"Client startup completed. Success: {success}/{total}"
        )

        if failed:
            self.main_logger.warning(
                f"{failed} client(s) failed to start"
            )

    async def stop_all(self):
        """Gracefully shutdown all clients."""
        if not self.managers:
            return

        self.main_logger.info("Shutting down all clients...")

        stop_tasks = []
        for name, manager in self.managers.items():
            task = asyncio.create_task(
                manager.stop(),
                name=f"stop_{name}"
            )
            stop_tasks.append((name, task))

        for name, task in stop_tasks:
            try:
                await task
                self.main_logger.info(f"Client {name} stopped successfully")
            except Exception as e:
                self.main_logger.error(f"Error stopping {name}: {e}")

        self.managers.clear()
        self.main_logger.info("All clients stopped")

    async def run(self):
        """Main method to start all clients."""
        try:
            # Start all clients
            await self.start_all()

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.main_logger.error(f"Critical error: {e}")
        finally:
            # Attempt to gracefully stop all clients
            await self.stop_all()

    def get_manager(self, session_name: str) -> Optional[ClientManager]:
        """
        Get the client manager by session name.

        Args:
            session_name: Session name.

        Returns:
            Optional[ClientManager]: Client manager or None.
        """
        return self.managers.get(session_name)


async def main():
    """Entry point of the application."""
    manager = PyrogramMultiClient("config.yaml")
    try:
        await manager.run()
    except KeyboardInterrupt:
        manager.main_logger.info("Received keyboard interrupt")
    except Exception as e:
        manager.main_logger.error(f"Critical error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
