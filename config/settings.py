# config/settings.py

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class PluginConfig:
    enabled: bool
    root: str
    include: List[str]
    exclude: List[str]


@dataclass
class PeriodicTasksConfig:
    enabled: bool
    schedule_module: str
    schedule_function: str
    tasks: List[str]


@dataclass
class SessionConfig:
    type: str  # file/memory/string
    string: Optional[str]
    workdir: str
    in_memory: bool


@dataclass
class ErrorHandlerConfig:
    sleep_threshold: int
    max_retries: int
    retry_delay: int


@dataclass
class ClientConfig:
    # Main parameters
    session_name: str
    type: str
    api_id: int
    api_hash: str

    # Client information
    app_version: str
    device_model: str
    system_version: str
    lang_code: str

    # Network settings
    ipv6: bool
    proxy: Optional[Dict[str, Any]]
    test_mode: bool

    # Authentication
    bot_token: Optional[str]
    session_string: Optional[str]
    phone_number: Optional[str]
    phone_code: Optional[str]
    password: Optional[str]

    # Performance parameters
    workers: int
    sleep_threshold: int
    max_concurrent_transmissions: int

    # Message settings
    parse_mode: str

    # Additional flags
    no_updates: bool
    takeout: bool
    hide_password: bool

    # Component configurations
    workdir: str
    in_memory: bool
    plugins: PluginConfig
    periodic_tasks: PeriodicTasksConfig
    session: SessionConfig
    error_handler: ErrorHandlerConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientConfig':
        # Plugin configuration
        plugins_data = data.get('plugins', {})
        plugins = PluginConfig(
            enabled=plugins_data.get('enabled', False),
            root=plugins_data.get('root', ''),
            include=plugins_data.get('include', []),
            exclude=plugins_data.get('exclude', [])
        )

        # Periodic tasks configuration
        periodic_tasks_data = data.get('periodic_tasks', {})
        periodic_tasks = PeriodicTasksConfig(
            enabled=periodic_tasks_data.get('enabled', False),
            schedule_module=periodic_tasks_data.get('schedule_module', ''),
            schedule_function=periodic_tasks_data.get('schedule_function', ''),
            tasks=periodic_tasks_data.get('tasks', [])
        )

        # Session configuration
        session = SessionConfig(
            type=data.get('session_type', 'file'),
            string=data.get('session_string'),
            workdir=data.get('workdir', 'sessions'),
            in_memory=data.get('in_memory', False)
        )

        # Error handler configuration
        error_handler = ErrorHandlerConfig(
            sleep_threshold=data.get('sleep_threshold', 10),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 5)
        )

        return cls(
            session_name=data['session_name'],
            type=data['type'],
            api_id=int(data['api_id']),
            api_hash=data['api_hash'],
            app_version=data.get('app_version', 'Pyrogram x.y.z'),
            device_model=data.get('device_model', 'Unknown'),
            system_version=data.get('system_version', 'Unknown'),
            lang_code=data.get('lang_code', 'en'),
            ipv6=data.get('ipv6', False),
            proxy=data.get('proxy'),
            test_mode=data.get('test_mode', False),
            bot_token=data.get('bot_token'),
            session_string=data.get('session_string'),
            phone_number=data.get('phone_number'),
            phone_code=data.get('phone_code'),
            password=data.get('password'),
            workers=data.get('workers', 4),
            workdir=data.get('workdir', 'sessions'),
            parse_mode=data.get('parse_mode', 'HTML'),
            no_updates=data.get('no_updates', False),
            takeout=data.get('takeout', False),
            sleep_threshold=data.get('sleep_threshold', 10),
            hide_password=data.get('hide_password', True),
            max_concurrent_transmissions=data.get('max_concurrent_transmissions', 1),
            in_memory=data.get('in_memory', False),
            plugins=plugins,
            periodic_tasks=periodic_tasks,
            session=session,
            error_handler=error_handler
        )


class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
        self._clients = self._parse_clients()

    def _load_config(self) -> Dict[str, Any]:
        path_obj = Path(self.config_path)
        if not path_obj.is_file():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(path_obj, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _parse_clients(self) -> List[ClientConfig]:
        return [ClientConfig.from_dict(client) for client in self._config.get("clients", [])]

    def reload(self):
        """Reload the configuration."""
        self._config = self._load_config()
        self._clients = self._parse_clients()

    @property
    def clients(self) -> List[ClientConfig]:
        """Get the list of client configurations."""
        return self._clients
