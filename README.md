Certainly! Below is the fully translated and properly edited `README.md` for your **Pyrogram Multi-Client Manager** project. The configuration file (`config.yaml`) within the README has been updated with English comments and placeholder values for sensitive information.

---

# Pyrogram Multi-Client Manager

![Pyrogram](https://img.shields.io/badge/Pyrogram-v2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Pyrogram Multi-Client Manager is a robust and flexible Python framework designed to manage multiple Pyrogram clients (both user and bot types) simultaneously. It offers advanced features such as plugin management, periodic task scheduling, comprehensive error handling, and detailed logging, making it ideal for building scalable Telegram bots and user clients.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Configuration File Structure](#configuration-file-structure)
  - [Client Configuration](#client-configuration)
  - [Plugin Configuration](#plugin-configuration)
  - [Periodic Tasks Configuration](#periodic-tasks-configuration)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Graceful Shutdown](#graceful-shutdown)
- [How It Works](#how-it-works)
  - [Core Components](#core-components)
    - [main.py](#mainpy)
    - [client_manager.py](#client_managerpy)
    - [Plugins](#plugins)
    - [Utilities](#utilities)
- [Plugin System](#plugin-system)
  - [Creating a Plugin](#creating-a-plugin)
  - [Plugin Structure](#plugin-structure)
- [Logging](#logging)
  - [Log Files](#log-files)
  - [Console Output](#console-output)
- [Error Handling](#error-handling)
  - [EnhancedErrorHandler](#enhancederrorhandler)
- [Session Management](#session-management)
  - [Session Types](#session-types)
  - [SessionManager](#sessionmanager)
- [Connecting Clients](#connecting-clients)
  - [Obtaining Telegram API Credentials](#obtaining-telegram-api-credentials)
  - [Adding a New Client](#adding-a-new-client)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-Client Support**: Manage multiple Telegram clients (users and bots) concurrently.
- **Plugin Architecture**: Easily extend functionality with bot and user plugins.
- **Periodic Tasks**: Schedule recurring tasks using APScheduler.
- **Advanced Error Handling**: Enhanced error management with MTProto support.
- **Comprehensive Logging**: Colored and categorized logging for different client types.
- **Flexible Session Management**: Supports file-based, in-memory, and string-based sessions.
- **Graceful Shutdown**: Handles system signals for orderly termination of clients.

## Installation

### Prerequisites

- **Python**: Version 3.8 or higher.
- **Telegram API Credentials**: You need `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org/).

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/maryny4/Pyrogram-Multi-Client-Manager.git
   cd Pyrogram-Multi-Client-Manager
   ```

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

All configurations are managed through the `config.yaml` file located in the project root. This file defines client settings, plugins, periodic tasks, and other essential parameters.

### Configuration File Structure

```yaml
clients:
  # -------------------------------
  # 1) user1
  # -------------------------------
  - session_name: "user1"
    type: "user"
    api_id: YOUR_API_ID
    api_hash: "YOUR_API_HASH"
    app_version: "User1App 1.2.3"
    device_model: "User1Device"
    system_version: "User1OS 1.0"
    lang_code: "en"
    ipv6: false
    proxy: null
    test_mode: false
    bot_token: null
    session_string: null
    in_memory: false
    phone_number: "+1234567890"
    phone_code: ""
    password: ""
    workers: 3
    workdir: "sessions"
    parse_mode: "HTML"
    no_updates: false
    takeout: false
    sleep_threshold: 10
    hide_password: false
    max_concurrent_transmissions: 1

    # Session Configuration
    session:
      type: "file"
      string: null
      workdir: "sessions"
      in_memory: false

    # Error Handler Configuration
    error_handler:
      sleep_threshold: 10
      max_retries: 3
      retry_delay: 5

    plugins:
      enabled: true
      root: "plugins/user_plugins/user1"
      include: ["user_commands", "user_periodic"]
      exclude: []

    periodic_tasks:
      enabled: true
      schedule_module: "plugins.user_plugins.user1.user_periodic"
      schedule_function: "schedule_user1_tasks"
      tasks:
        - user1_task_send

  # -------------------------------
  # 2) user2
  # -------------------------------
  - session_name: "user2"
    type: "user"
    api_id: YOUR_API_ID
    api_hash: "YOUR_API_HASH"
    app_version: "User2App 2.1"
    device_model: "User2Device"
    system_version: "User2OS 2.0"
    lang_code: "ru"
    ipv6: false
    proxy: null
    test_mode: false
    bot_token: null
    session_string: null
    in_memory: false
    phone_number: "+1234567890"
    phone_code: ""
    password: "YOUR_PASSWORD"
    workers: 2
    workdir: "sessions"
    parse_mode: "HTML"
    no_updates: false
    takeout: false
    sleep_threshold: 15
    hide_password: false
    max_concurrent_transmissions: 1

    session:
      type: "file"
      string: null
      workdir: "sessions"
      in_memory: false

    error_handler:
      sleep_threshold: 15
      max_retries: 3
      retry_delay: 5

    plugins:
      enabled: true
      root: "plugins/user_plugins/user2"
      include: ["user_commands", "user_periodic"]
      exclude: []

    periodic_tasks:
      enabled: true
      schedule_module: "plugins.user_plugins.user2.user_periodic"
      schedule_function: "schedule_user2_tasks"
      tasks:
        - user2_task_notify

  # -------------------------------
  # 3) bot1
  # -------------------------------
  - session_name: "bot1"
    type: "bot"
    api_id: YOUR_API_ID
    api_hash: "YOUR_API_HASH"
    app_version: "Bot1App 3.3.3"
    device_model: "Bot1Device"
    system_version: "Bot1OS 3.0"
    lang_code: "en"
    ipv6: false
    proxy: null
    test_mode: false
    bot_token: "YOUR_BOT_TOKEN"
    session_string: null
    in_memory: false
    phone_number: null
    phone_code: null
    password: null
    workers: 2
    workdir: "sessions"
    parse_mode: "HTML"
    no_updates: false
    takeout: false
    sleep_threshold: 5
    hide_password: false
    max_concurrent_transmissions: 2

    session:
      type: "file"
      string: null
      workdir: "sessions"
      in_memory: false

    error_handler:
      sleep_threshold: 5
      max_retries: 3
      retry_delay: 3

    plugins:
      enabled: true
      root: "plugins/bot_plugins/bot1"
      include: ["bot_commands", "bot_periodic"]
      exclude: []

    periodic_tasks:
      enabled: true
      schedule_module: "plugins.bot_plugins.bot1.bot_periodic"
      schedule_function: "schedule_bot1_tasks"
      tasks:
        - bot1_task_send

  # -------------------------------
  # 4) bot2
  # -------------------------------
  - session_name: "bot2"
    type: "bot"
    api_id: YOUR_API_ID
    api_hash: "YOUR_API_HASH"
    app_version: "Bot2App 4.4.4"
    device_model: "Bot2Device"
    system_version: "Bot2OS 4.0"
    lang_code: "en"
    ipv6: false
    proxy: null
    test_mode: false
    bot_token: "YOUR_BOT_TOKEN"
    session_string: null
    in_memory: false
    phone_number: null
    phone_code: null
    password: null
    workers: 2
    workdir: "sessions"
    parse_mode: "HTML"
    no_updates: false
    takeout: false
    sleep_threshold: 5
    hide_password: false
    max_concurrent_transmissions: 2

    session:
      type: "file"
      string: null
      workdir: "sessions"
      in_memory: false

    error_handler:
      sleep_threshold: 5
      max_retries: 3
      retry_delay: 3

    plugins:
      enabled: true
      root: "plugins/bot_plugins/bot2"
      include: ["bot_commands", "bot_periodic"]
      exclude: []

    periodic_tasks:
      enabled: true
      schedule_module: "plugins.bot_plugins.bot2.bot_periodic"
      schedule_function: "schedule_bot2_tasks"
      tasks:
        - bot2_task_send
```

### Client Configuration

Each client configuration includes the following sections:

- **session_name**: Unique name for the session.
- **type**: `user` or `bot`.
- **api_id & api_hash**: Telegram API credentials obtained from [my.telegram.org](https://my.telegram.org/).
- **app_version, device_model, system_version, lang_code**: Client-specific information.
- **ipv6**: Enable IPv6 support.
- **proxy**: Proxy settings (if any).
- **test_mode**: Enable test mode for the client.
- **bot_token**: Telegram bot token (required if `type` is `bot`).
- **session_string**: Session string for string-based sessions.
- **phone_number, phone_code, password**: Authentication details for user clients.
- **workers**: Number of worker threads.
- **sleep_threshold**: Threshold for sleep in error handling.
- **max_concurrent_transmissions**: Maximum concurrent transmissions.
- **parse_mode**: Message parse mode (`HTML` or `Markdown`).
- **no_updates, takeout, hide_password**: Additional flags.
- **workdir**: Directory for storing session files.
- **in_memory**: Use in-memory session.
- **plugins**: Plugin management settings.
- **periodic_tasks**: Periodic task scheduling settings.

### Plugin Configuration

```yaml
plugins:
  enabled: true
  root: "plugins/user_plugins"  # Directory where plugins are located
  include:
    - "user1"
    - "user2"
  exclude:
    - "excluded_plugin"
```

- **enabled**: Enable or disable the plugin system.
- **root**: Root directory for plugins.
- **include**: List of plugins to include.
- **exclude**: List of plugins to exclude.

### Periodic Tasks Configuration

```yaml
periodic_tasks:
  enabled: true
  schedule_module: "plugins.user_plugins.user1.user_periodic"
  schedule_function: "schedule_user1_tasks"
  tasks:
    - user1_task_send
```

- **enabled**: Enable or disable periodic tasks.
- **schedule_module**: Python module where the scheduler function is defined.
- **schedule_function**: Function to set up the scheduler.
- **tasks**: List of tasks to schedule.

## Usage

### Running the Application

After configuring `config.yaml`, start the application using:

```bash
python main.py
```

The application will:

1. **Initialize Clients**: Create and start all configured Telegram clients (users and bots).
2. **Load Plugins**: Dynamically load and initialize all included plugins.
3. **Start Periodic Tasks**: Schedule and run all defined periodic tasks using APScheduler.
4. **Handle Errors**: Monitor and manage errors with retry mechanisms.
5. **Log Activities**: Output logs to both console and dedicated log files.

### Graceful Shutdown

The application listens for system signals (`SIGINT`, `SIGTERM`) to gracefully shutdown all clients and tasks. You can terminate the application using:

- **Keyboard Interrupt**: Press `Ctrl+C`.
- **Sending Signals**: Use command-line tools to send `SIGINT` or `SIGTERM`.

Upon receiving a shutdown signal, the application will:

1. **Stop Periodic Tasks**: Shutdown all APScheduler schedulers.
2. **Stop Clients**: Gracefully stop all Pyrogram clients.
3. **Clean Up**: Clear all managers and reset internal states.

## How It Works

Pyrogram Multi-Client Manager is structured into several core components that interact seamlessly to provide a cohesive multi-client environment.

### Core Components

#### main.py

- **Entry Point**: Initializes the `PyrogramMultiClient` manager with the configuration file.
- **Event Loop**: Sets up the asynchronous event loop using `uvloop` for enhanced performance.
- **Signal Handlers**: Listens for system signals to initiate graceful shutdown.
- **Run Method**: Starts all clients and waits for shutdown events.

#### client_manager.py

- **ClientManager Class**: Manages individual Pyrogram clients.
  - **Initialization**: Builds client configurations, initializes additional managers (error handler, session manager, message formatter).
  - **Start Method**: Connects the client, initializes schedulers, and handles retries on failures.
  - **Stop Method**: Gracefully disconnects the client and stops schedulers.
  - **Error Handling**: Delegates error processing to `EnhancedErrorHandler`.
  - **Scheduler Initialization**: Dynamically loads and starts periodic tasks based on configuration.

#### Plugins

- **Directory Structure**:
  
  ```
  plugins/
  ├── bot_plugins/
  │   ├── bot1/
  │   │   ├── __init__.py
  │   │   ├── bot_commands.py
  │   │   └── bot_periodic.py
  │   └── bot2/
  │       ├── __init__.py
  │       ├── bot_commands.py
  │       └── bot_periodic.py
  └── user_plugins/
      ├── user1/
      │   ├── __init__.py
      │   ├── user_commands.py
      │   └── user_periodic.py
      └── user2/
          ├── __init__.py
          ├── user_commands.py
          └── user_periodic.py
  ```

- **Bot Plugins**: Handle bot-specific commands and tasks.
- **User Plugins**: Manage user-specific interactions and periodic updates.
- **Dynamic Loading**: The `ClientManager` dynamically imports and initializes plugins based on configuration.

#### Utilities

- **Error Handler (`error_handler.py`)**: Manages and categorizes errors, implementing retry logic for recoverable errors.
- **Logger (`logger.py`)**: Provides colored and categorized logging for different client types and components.
- **Message Formatter (`message_formatter.py`)**: Formats messages according to client settings, ensuring consistency and preventing markup conflicts.
- **Session Manager (`session_manager.py`)**: Handles session initialization, export, and import for various session types (file, memory, string).

## Plugin System

Plugins allow you to extend the functionality of your clients without modifying the core codebase. The project supports both bot and user plugins.

### Creating a Plugin

1. **Create Plugin Directory**

   For example, to create a new bot plugin named `bot3`:

   ```bash
   mkdir plugins/bot_plugins/bot3
   touch plugins/bot_plugins/bot3/__init__.py
   touch plugins/bot_plugins/bot3/bot_commands.py
   touch plugins/bot_plugins/bot3/bot_periodic.py
   ```

2. **Define Command Handlers**

   In `bot_commands.py`, define your command handlers using Pyrogram decorators.

   ```python
   from pyrogram import Client, filters
   from pyrogram.types import Message
   from utils.logger import get_logger

   logger = get_logger("Bot3Commands")

   class Bot3Commands:
       def __init__(self):
           self.task_manager = None

       async def hello_command(self, client: Client, message: Message):
           """Handler for the /hello command."""
           await message.reply_text("Hello from Bot3!")

   commands_handler = Bot3Commands()

   @Client.on_message(filters.command("hello") & filters.private)
   async def hello_handler(client: Client, message: Message):
       await commands_handler.hello_command(client, message)
   ```

3. **Define Periodic Tasks**

   In `bot_periodic.py`, create periodic tasks and define a scheduler function to add them to APScheduler.

   ```python
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from pyrogram import Client
   from utils.logger import get_logger

   logger = get_logger("Bot3Periodic")

   class Bot3PeriodicTasks:
       def __init__(self, client: Client):
           self.client = client
           self.logger = get_logger("Bot3Periodic")

       async def periodic_task(self):
           """A sample periodic task."""
           logger.info("Bot3 periodic task executed.")

   def schedule_bot3_tasks(client: Client, tasks: list) -> Optional[AsyncIOScheduler]:
       """Setup the scheduler for bot3."""
       try:
           scheduler = AsyncIOScheduler()
           task_manager = Bot3PeriodicTasks(client)

           # Link with the command handler if needed

           scheduler.add_job(
               task_manager.periodic_task,
               trigger="interval",
               minutes=1,
               max_instances=1,
               misfire_grace_time=15
           )

           scheduler.start()
           logger.info("Started bot3 scheduler")
           return scheduler

       except Exception as e:
           logger.error(f"Failed to setup scheduler for bot3: {e}")
           return None
   ```

4. **Update `config.yaml`**

   Add your new plugin to the `include` list under the respective client configuration.

   ```yaml
   plugins:
     enabled: true
     root: "plugins/bot_plugins"
     include:
       - "bot1"
       - "bot2"
       - "bot3"  # Newly added plugin
     exclude:
       - "excluded_plugin"
   ```

### Plugin Structure

Each plugin typically contains:

- **`__init__.py`**: Initializes the plugin package.
- **`*_commands.py`**: Defines command handlers using Pyrogram decorators.
- **`*_periodic.py`**: Defines periodic tasks and scheduler setup.

Ensure that your plugins follow this structure to be correctly loaded and managed by the `ClientManager`.

## Logging

The application provides comprehensive logging with colored outputs for different client types. Logs are categorized into separate files based on client types (e.g., `user.log`, `bot.log`, `system.log`) and also output to the console with color-coded messages.

### Log Files

- **ErrorHandler.log**: Logs related to error handling.
- **MessageFormatter.log**: Logs pertaining to message formatting.
- **SessionManager.log**: Logs about session management.
- **bot.log**: General logs for bot clients.
- **system.log**: Logs for system-level messages.
- **user.log**: General logs for user clients.

Logs are stored in the `logs/` directory with automatic rotation (max 2MB per file, up to 3 backups).

### Console Output

The console displays colored and categorized log messages for real-time monitoring. Different colors represent different log levels and client types for easy differentiation.

## Error Handling

The framework features an enhanced error handler (`EnhancedErrorHandler`) that manages different types of exceptions, including MTProto-specific errors like `FloodWait`. It maintains error statistics and can decide whether to retry operations based on the error type and severity.

### EnhancedErrorHandler

- **FloodWait Handling**: Automatically retries after waiting if the wait time is below a configurable threshold.
- **Detailed Logging**: Logs detailed information about errors, including client type and session information.
- **Statistics Tracking**: Keeps track of error counts and types for monitoring and debugging.
- **MTProto Support**: Utilizes MTProto functions to fetch additional error details when necessary.

**Example Usage:**

The `ClientManager` integrates `EnhancedErrorHandler` to process errors during client operations.

```python
self.error_handler = EnhancedErrorHandler(
    self.client,
    f"ErrorHandler_{self.config.session_name}",
    self.config.sleep_threshold
)
```

## Session Management

Sessions are managed using the `SessionManager`, which supports different session types:

### Session Types

- **File-Based**: Stores session data in files within the `sessions/` directory.
- **In-Memory**: Stores session data in memory (useful for ephemeral sessions).
- **String-Based**: Allows exporting and importing sessions as strings.

### SessionManager

- **Initialization**: Sets up the session based on the configuration type.
- **Exporting Sessions**: Can export session strings for backup or transfer.
- **Importing Sessions**: Allows restoring sessions from exported strings.
- **Session Information**: Provides details about the current session state.

**Example Configuration:**

```yaml
session:
  type: "file"  # Options: file, memory, string
  string: null
  workdir: "sessions"
  in_memory: false
```

## Connecting Clients

Connecting clients involves setting up both user and bot clients with their respective credentials and configurations.

### Obtaining Telegram API Credentials

1. **Register an Application**:
   - Go to [my.telegram.org](https://my.telegram.org/).
   - Log in with your Telegram account.
   - Navigate to the "API Development Tools" section.
   - Create a new application to obtain your `api_id` and `api_hash`.

### Adding a New Client

1. **Update `config.yaml`**

   Add a new client configuration under the `clients` section as shown in the [Client Configuration](#client-configuration) section.

2. **Set Up Plugin Directories**

   Create corresponding plugin directories for the new clients.

   ```bash
   mkdir plugins/user_plugins/user3
   touch plugins/user_plugins/user3/__init__.py
   touch plugins/user_plugins/user3/user_commands.py
   touch plugins/user_plugins/user3/user_periodic.py

   mkdir plugins/bot_plugins/bot3
   touch plugins/bot_plugins/bot3/__init__.py
   touch plugins/bot_plugins/bot3/bot_commands.py
   touch plugins/bot_plugins/bot3/bot_periodic.py
   ```

3. **Implement Plugin Functionality**

   Develop your command handlers and periodic tasks within the newly created plugin files, following the structure outlined in the [Plugin System](#plugin-system) section.

4. **Run the Application**

   Start the application to initialize the new clients.

   ```bash
   python main.py
   ```

   The application will automatically load the new client configurations and initialize the associated plugins and periodic tasks.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Make Changes and Commit**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

   Describe your changes and submit the PR for review.

**Guidelines:**

- Follow the existing code style and structure.
- Ensure that all new features are documented.
- Write clear and concise commit messages.
- Include tests for new functionalities if applicable.

## License

This project is licensed under the [MIT License](LICENSE).

---

*Developed with ❤️ using [Pyrogram](https://docs.pyrogram.org/).*

## Additional Notes

- **Ensure Configuration Accuracy**: Double-check your `config.yaml` for correct indentation and accurate information to prevent runtime errors.
- **Plugin Development**: When creating plugins, adhere to the existing plugin structure to ensure seamless integration and functionality.
- **Logging Levels**: Adjust logging levels as needed in `logger.py` to control the verbosity of log outputs.

If you encounter any issues or have questions, feel free to open an issue on the [GitHub repository](https://github.com/maryny4/Pyrogram-Multi-Client-Manager/issues).


