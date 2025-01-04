from datetime import datetime, timedelta
from typing import Optional, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.errors import RPCError

from utils.logger import get_logger

logger = get_logger("Bot1Periodic")


class Bot1PeriodicTasks:
    def __init__(self, client: Client):
        self.client = client
        self.logger = get_logger("Bot1Periodic")
        from .bot_commands import commands_handler
        self.commands_handler = commands_handler

    async def update_user_messages(self):
        """Update user messages."""
        try:
            current_time = datetime.now()
            users_to_remove = []

            for user_id, session in self.commands_handler.user_sessions.items():
                try:
                    if current_time - session["start_time"] > timedelta(minutes=30):
                        users_to_remove.append(user_id)
                        continue

                    # Update the message
                    time_left = 30 - (current_time - session["start_time"]).seconds // 60
                    update_text = (
                        f"🤖 Bot #1 Status Update\n\n"
                        f"⏰ Current time: {current_time.strftime('%H:%M:%S')}\n"
                        f"📅 Started: {session['start_time'].strftime('%H:%M:%S')}\n"
                        f"⌛️ Time remaining: {time_left} minutes\n\n"
                        f"Updates will stop automatically after 30 minutes."
                    )

                    try:
                        await self.client.edit_message_text(
                            chat_id=session["message"].chat.id,
                            message_id=session["message"].id,
                            text=update_text
                        )
                    except RPCError as e:
                        if "MESSAGE_ID_INVALID" in str(e):
                            self.logger.info(
                                f"Message was deleted or became invalid for user {user_id}, removing session")
                            users_to_remove.append(user_id)
                        else:
                            raise e

                except Exception as e:
                    self.logger.error(f"Error updating message for user {user_id}: {e}")
                    users_to_remove.append(user_id)

            # Remove completed sessions
            for user_id in users_to_remove:
                self.commands_handler.user_sessions.pop(user_id, None)
                self.logger.info(f"Removed session for user {user_id}")

        except Exception as e:
            self.logger.error(f"Error in update task: {e}")


def schedule_bot1_tasks(client: Client, tasks: List[str]) -> Optional[AsyncIOScheduler]:
    """Setup the scheduler for bot1."""
    try:
        scheduler = AsyncIOScheduler()
        task_manager = Bot1PeriodicTasks(client)

        # Link with the command handler
        from .bot_commands import commands_handler
        commands_handler.task_manager = task_manager

        scheduler.add_job(
            task_manager.update_user_messages,
            trigger="interval",
            seconds=30,
            max_instances=1,
            misfire_grace_time=15
        )

        scheduler.start()
        logger.info("Started bot1 scheduler")
        return scheduler

    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}")
        return None
