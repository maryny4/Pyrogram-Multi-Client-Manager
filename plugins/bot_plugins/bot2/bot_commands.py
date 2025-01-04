from datetime import datetime

from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from utils.logger import get_logger

logger = get_logger("Bot2Commands")


class Bot2Commands:
    def __init__(self):
        self.task_manager = None
        self.user_sessions = {}

    async def start_command(self, client: Client, message: Message):
        """
        Handler for the /start command for bot2.
        """
        try:
            user = message.from_user
            logger.info(f"Received /start from user {user.id} ({user.first_name})")

            # Bot information
            me = await client.get_me()
            start_text = (
                f"👋 Hello! I'm Bot #2\n\n"
                f"Bot Information:\n"
                f"• Name: {me.first_name}\n"
                f"• Username: @{me.username}\n"
                f"• ID: {me.id}\n"
                f"• Type: Telegram Bot #2\n\n"
                f"I will update this message every 30 seconds with current time.\n"
                f"Updates will continue for 30 minutes."
            )

            # Send the message and save it
            sent_message = await message.reply_text(start_text)

            if self.task_manager:
                # Save user session information
                self.user_sessions[user.id] = {
                    "message": sent_message,
                    "start_time": datetime.now()
                }

            logger.info(f"Sent welcome message to user {user.id}")

        except RPCError as e:
            logger.error(f"Telegram error in start command: {e}")
        except Exception as e:
            logger.error(f"Error in start command: {e}")


commands_handler = Bot2Commands()


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await commands_handler.start_command(client, message)
