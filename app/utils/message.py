import re
from typing import Optional

from discord import Message


def extract_url_from_message(message: Message) -> Optional[str]:
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                      message.content)
    return urls[0] if urls else None
