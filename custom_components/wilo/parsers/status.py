"""Parser used to parse status page."""
import regex 

from .base import BaseParser


class StatusParser(BaseParser):
    def parse(html:str) -> dict:
        data = {}

        pattern = regex.compile(r"<span[^>]*>(.*?)</span>\s*<b>(.*?)</b>", regex.DOTALL)
        for match in pattern.finditer(html):
            key = match.group(1).strip().rstrip(":")
            value = match.group(2).strip()
            data[key] = value
        return data
