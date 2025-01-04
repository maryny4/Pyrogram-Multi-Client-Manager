from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.logger import get_logger

logger = get_logger("User2Commands")


class User2Commands:
    def __init__(self):
        self.task_manager = None
        self.saved_message = None
        self.start_time = None

    async def start_command(self, client: Client, message: Message):
        """
        Handler for the /start command for user2.
        Responds only to commands in Saved Messages.
        """
        try:
            # Check if the message is in Saved Messages
            me = await client.get_me()
            if message.chat.id != me.id:
                logger.info(f"Ignoring /start in chat {message.chat.id}")
                return

            logger.info("Received /start in Saved Messages")

            start_text = (
                f"👤 User Account #2\n\n"
                f"Account Information:\n"
                f"• Name: {me.first_name} {me.last_name or ''}\n"
                f"• Username: @{me.username}\n"
                f"• ID: {me.id}\n"
                f"• Plugin: User Plugin #1\n\n"
                f"Message will be updated every 30 seconds\n"
                f"Updates will continue for 30 minutes"
            )

            # Send and save the message
            self.saved_message = await message.reply_text(start_text)
            self.start_time = datetime.now()

            logger.info("Started new session in Saved Messages")

        except Exception as e:
            logger.error(f"Error in start command: {e}")


commands_handler = User2Commands()


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await commands_handler.start_command(client, message)
