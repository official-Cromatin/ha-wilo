"""Parser used to parse settings page."""
import regex

from .base import BaseParser


class SettingsParser(BaseParser):
    """Parser optimized to parse settings."""
    def parse(html:str) -> dict:
        data = {}

        pattern = regex.compile(r"<span[^>]*>(.*?)</span>\s*<b>(.*?)</b>", regex.DOTALL)
        for match in pattern.finditer(html):
            raw_key = match.group(1).strip()
            value = match.group(2).strip()

            clean_key = regex.sub(r"^\d+(\.\d+)*\s*", "", raw_key)
            clean_key = clean_key.rstrip(":")

            if clean_key.lower().startswith("last occur"):
                continue

            data[clean_key] = value
        return data
