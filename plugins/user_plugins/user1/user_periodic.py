from datetime import datetime, timedelta
from typing import Optional, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.errors import RPCError

from utils.logger import get_logger

logger = get_logger("User1Periodic")


class User1PeriodicTasks:
    def __init__(self, client: Client):
        self.client = client
        self.logger = get_logger("User1Periodic")
        from .user_commands import commands_handler
        self.commands_handler = commands_handler

    async def update_saved_message(self):
        """Update the message in Saved Messages."""
        try:
            if not self.commands_handler.saved_message:
                return

            current_time = datetime.now()

            if not self.commands_handler.start_time:
                return

            # Check if the time has expired (30 minutes)
            if current_time - self.commands_handler.start_time > timedelta(minutes=30):
                self.commands_handler.saved_message = None
                self.commands_handler.start_time = None
                self.logger.info("Session expired")
                return

            me = await self.client.get_me()
            time_left = 30 - (current_time - self.commands_handler.start_time).seconds // 60

            update_text = (
                f"👤 User Account #1 Status\n\n"
                f"Current time: {current_time.strftime('%H:%M:%S')}\n"
                f"Started: {self.commands_handler.start_time.strftime('%H:%M:%S')}\n"
                f"Time remaining: {time_left} minutes\n\n"
                f"Account: {me.first_name} {me.last_name or ''}\n"
                f"Plugin: User Plugin #1\n"
                f"Status: Active ✅"
            )

            try:
                await self.client.edit_message_text(
                    chat_id=self.commands_handler.saved_message.chat.id,
                    message_id=self.commands_handler.saved_message.id,
                    text=update_text
                )
            except RPCError as e:
                if "MESSAGE_ID_INVALID" in str(e):
                    self.logger.info("Message was deleted or became invalid, stopping periodic tasks")
                    self.commands_handler.saved_message = None
                    self.commands_handler.start_time = None
                else:
                    raise e

        except Exception as e:
            self.logger.error(f"Error updating saved message: {e}")
            self.commands_handler.saved_message = None
            self.commands_handler.start_time = None


def schedule_user1_tasks(client: Client, tasks: List[str]) -> Optional[AsyncIOScheduler]:
    """Setup the scheduler for user1."""
    try:
        scheduler = AsyncIOScheduler()
        task_manager = User1PeriodicTasks(client)

        # Link with the command handler
        from .user_commands import commands_handler
        commands_handler.task_manager = task_manager

        scheduler.add_job(
            task_manager.update_saved_message,
            trigger="interval",
            seconds=30,
            max_instances=1,
            misfire_grace_time=15
        )

        scheduler.start()
        logger.info("Started user1 scheduler")
        return scheduler

    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}")
        return None
