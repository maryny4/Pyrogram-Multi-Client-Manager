from typing import Optional, Union, Dict, Any

from pyrogram import enums, Client

from utils.logger import get_logger


class MessageFormatter:
    def __init__(self, client: Client):
        """
        Message formatter considering client settings.

        Args:
            client: Instance of Pyrogram client.
        """
        self.client = client
        self.logger = get_logger(f"MessageFormatter_{client.name}")

        # Get the markup mode from client settings
        self.default_parse_mode = self._get_client_parse_mode()

        # Save client information
        self.client_info = {
            'name': client.name,
            'type': 'bot' if client.bot_token else 'user',
            'app_version': client.app_version,
            'device_model': client.device_model,
            'lang_code': client.lang_code
        }

        # Allowed HTML tags
        self.ALLOWED_HTML_TAGS = [
            '<b>', '</b>', '<i>', '</i>', '<u>', '</u>',
            '<s>', '</s>', '<code>', '</code>', '<pre>', '</pre>',
            '<a>', '</a>', '<spoiler>', '</spoiler>'
        ]

        # Special characters for Markdown
        self.MARKDOWN_SPECIAL_CHARS = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']

    def _get_client_parse_mode(self) -> enums.ParseMode:
        """Get the markup mode from client settings."""
        client_parse_mode = getattr(self.client, 'parse_mode', 'DEFAULT')
        return self._normalize_parse_mode(client_parse_mode)

    def _normalize_parse_mode(self, parse_mode: Union[str, enums.ParseMode]) -> enums.ParseMode:
        """
        Normalize the markup mode.

        Args:
            parse_mode: Markup mode as a string or enum.

        Returns:
            enums.ParseMode: Normalized markup mode.
        """
        if isinstance(parse_mode, str):
            try:
                return enums.ParseMode[parse_mode.upper()]
            except KeyError:
                self.logger.warning(
                    f"Invalid parse mode: {parse_mode} for {self.client_info['name']}, using DEFAULT"
                )
                return enums.ParseMode.DEFAULT
        return parse_mode

    def format_message(self, text: str, parse_mode: Optional[Union[str, enums.ParseMode]] = None,
                       clean_html: bool = True) -> str:
        """
        Format the message.

        Args:
            text: Text to format.
            parse_mode: Markup mode.
            clean_html: Whether to clean HTML tags.

        Returns:
            str: Formatted text.
        """
        mode = self._normalize_parse_mode(parse_mode) if parse_mode else self.default_parse_mode

        try:
            # Check for markup conflicts
            if mode != enums.ParseMode.DISABLED and self._has_conflicting_tags(text):
                self.logger.warning(
                    f"Detected conflicting markup tags in message for {self.client_info['name']}, "
                    f"switching to DISABLED mode"
                )
                mode = enums.ParseMode.DISABLED

            # Apply formatting based on the mode
            if mode == enums.ParseMode.HTML:
                if clean_html:
                    text = self._clean_html(text)
            elif mode == enums.ParseMode.MARKDOWN:
                text = self._escape_markdown(text)

            return text

        except Exception as e:
            self.logger.error(
                f"Error formatting message for {self.client_info['name']}: {str(e)}"
            )
            return text

    def _has_conflicting_tags(self, text: str) -> bool:
        """
        Check for conflicting markup tags.

        Args:
            text: Text to check.

        Returns:
            bool: Whether there are conflicts.
        """
        markdown_tags = ['**', '__', '~~', '`', '```']
        has_markdown = any(tag in text for tag in markdown_tags)
        has_html = any(tag in text for tag in self.ALLOWED_HTML_TAGS)

        return has_markdown and has_html

    def _clean_html(self, text: str) -> str:
        """
        Clean HTML tags, keeping only allowed ones.

        Args:
            text: Original text.

        Returns:
            str: Cleaned text.
        """
        # First, escape all HTML tags
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        # Restore allowed tags
        for tag in self.ALLOWED_HTML_TAGS:
            escaped_tag = tag.replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace(escaped_tag, tag)

        return text

    def _escape_markdown(self, text: str) -> str:
        """
        Escape special Markdown characters.

        Args:
            text: Original text.

        Returns:
            str: Text with escaped characters.
        """
        for char in self.MARKDOWN_SPECIAL_CHARS:
            text = text.replace(char, f'\\{char}')
        return text

    def create_button_text(self, text: str, parse_mode: Optional[Union[str, enums.ParseMode]] = None) -> str:
        """
        Format text for buttons considering restrictions.

        Args:
            text: Text for the button.
            parse_mode: Markup mode.

        Returns:
            str: Formatted text for the button.
        """
        # Buttons have specific restrictions
        mode = self._normalize_parse_mode(parse_mode) if parse_mode else self.default_parse_mode

        # Limited set of tags is supported in buttons
        allowed_button_html_tags = ['<b>', '</b>', '<i>', '</i>', '<u>', '</u>', '<s>', '</s>']

        try:
            if mode == enums.ParseMode.HTML:
                # Clean text from all tags except those allowed for buttons
                text = self._clean_html(text)
                for tag in self.ALLOWED_HTML_TAGS:
                    if tag not in allowed_button_html_tags:
                        text = text.replace(tag, '')
            elif mode == enums.ParseMode.MARKDOWN:
                # Only basic formatting is supported in buttons
                text = self._escape_markdown(text)

            return text

        except Exception as e:
            self.logger.error(
                f"Error formatting button text for {self.client_info['name']}: {str(e)}"
            )
            return text

    def get_formatter_info(self) -> Dict[str, Any]:
        """
        Get information about the current formatting settings.

        Returns:
            Dict[str, Any]: Information about the formatter.
        """
        return {
            'client': self.client_info,
            'default_parse_mode': self.default_parse_mode.value,
            'allowed_html_tags': self.ALLOWED_HTML_TAGS,
            'markdown_special_chars': self.MARKDOWN_SPECIAL_CHARS
        }

    def format_system_message(self, text: str) -> str:
        """
        Format system messages (logs, errors, etc.).

        Args:
            text: Text of the system message.

        Returns:
            str: Formatted system message.
        """
        try:
            # Always use HTML for system messages
            if self.client_info['type'] == 'bot':
                prefix = '🤖'
            else:
                prefix = '👤'

            formatted_text = (
                f"{prefix} <b>{self.client_info['name']}</b>\n"
                f"<code>{text}</code>"
            )

            return self.format_message(formatted_text, enums.ParseMode.HTML)

        except Exception as e:
            self.logger.error(
                f"Error formatting system message for {self.client_info['name']}: {str(e)}"
            )
            return text
