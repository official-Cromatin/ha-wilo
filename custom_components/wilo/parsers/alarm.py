"""Parser used to parse alarm page."""
import regex

from .base import BaseParser


class AlarmParser(BaseParser):
    """Parser optimized to parse alarms."""
    def parse(html:str) -> dict:
        alarm_match = regex.search(r"<h2>Alarm</h2>(.*?)<br>", html, regex.DOTALL)
        if alarm_match:
            alarm_text = alarm_match.group(1).strip()
            return {"Alarm": alarm_text}
        return {}
