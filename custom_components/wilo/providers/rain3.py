"""Implements the provider for rain3 pump."""

import re

from aiohttp import ClientError, ClientResponseError, ClientSession
from lxml import html as lxml_html

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..datastores import Rain3Datastore
from ..models import WiloModels
from .base import BaseProvider


class Rain3Provider(BaseProvider):
    """Provider class for rain3 pump."""

    SENSORS = []

    def __init__(self, device_ip, device_id, hass):
        """Initialize rain3 provider class.

        :param str device_ip:
            IP adress of rain3 pump.

        :param int device_id:
            ID of the device.

        :param HomeAssistant hass:
            Home assistant instance used for various tasks.
        """
        super().__init__(device_ip, device_id, WiloModels.RAIN3, hass)
        self.__client_session:ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        """Cached home assistant aiohttp client session."""
        if self.__client_session is None:
            self.__client_session = async_get_clientsession(self._hass)
        return self.__client_session

    async def async_create_device_info(self):
        """Creates device info for rain3 pump."""
        device_data = await self.async_update()

        self._device_info = DeviceInfo(
            configuration_url=f"http://{self._device_ip}",
            connections={("ip", self._device_ip)},
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=DOMAIN.capitalize(),
            model=self._model.value.capitalize(),
            name=f"{DOMAIN.capitalize()} {self._model.value.capitalize()} ({self._device_ip})",
            serial_number=device_data.serial_number,
            sw_version=device_data.software_version,
        )

    async def async_update(self):
        """Update the Datastore in the DataUpdateCoordinator."""
        combined_data = {}
        for url_path in ["identity", "state", "download", "setup", "installation", "settings", "errors"]:
            html = await self.__fetch_html(url_path)
            if not html:
                combined_data[url_path] = {}
                continue

            if url_path == "errors":
                parsed = self._parse_errors_page(html)
            else:
                parsed = self._parse_html(html)

            combined_data[url_path] = parsed
        return Rain3Datastore(combined_data)

    def _clean_key(self, raw_key: str) -> str:
        """Cleans the given key removing setting numbers and error codes.

        :param str raw_key:
            String to be cleaned.

        :returns str:
            Cleaned key.
        """
        key = raw_key.strip()
        key = self._RE_LEADING_NUM.sub("", key)
        key = self._RE_E_CODE.sub("", key)
        key = self._RE_TRAILING_COLON.sub("", key)
        return key.strip()

    def _clean_value(self, raw_value: str | None) -> str:
        """Cleans the given value.

        :param str | None raw_value:
            String to be cleaned, can be None.

        :returns str:
            Cleaned value.
        """
        if not raw_value:
            return ""
        value = raw_value.replace("\x00", "").strip()
        return re.sub(r"<br\s*/?>", "", value, flags=re.IGNORECASE).strip()

    def _parse_html(self, html: str) -> dict[str, str]:
        """Default parser for pages using the following format: `<span>...<b>...</b>`.

        :param str html:
            HTML as string to be parsed.

        :returns dict[str, str]:
            Dictionary containing parsed data from the given input html document.
        """
        root = lxml_html.fromstring(html.replace("\x00", ""))
        results: dict[str, str] = {}

        for span in root.xpath("//span"):
            raw_key = span.text_content() or ""
            b = span.xpath("following::b[1]")
            if not b:
                continue

            raw_value = b[0].text_content() or ""
            key = self._clean_key(raw_key)
            if not key or key.lower().startswith("last occur"):
                continue

            value = self._clean_value(raw_value)
            results[key] = value

        return results

    def _parse_errors_page(self, html: str) -> dict[str, str]:
        """Specialized parser used for error-endpoint to extract additional fields like alarm history.

        :param str html:
            HTML as string to be parsed.

        :returns dict[str, str]:
            Dictionary containing parsed data from the given input html document.
        """
        root = lxml_html.fromstring(html.replace("\x00", ""))
        results: dict[str, str] = {}

        results.update(self._parse_html(html))

        alarm_text = root.xpath("string(//h2[normalize-space()='Alarm']/following-sibling::text()[1])")
        if alarm_text:
            results["Alarm"] = self._clean_value(alarm_text)

        history = []
        b_tags = root.xpath("//h3[normalize-space()='Alarm history']/following-sibling::b")
        for b in b_tags:
            timestamp = self._clean_value(b.text_content())
            prev = b.getprevious()
            if prev is not None and prev.tail:
                error_text = self._clean_value(prev.tail)
            else:
                error_text = self._clean_value(b.xpath("preceding-sibling::text()[1]")[0] if b.xpath("preceding-sibling::text()[1]") else "")
            history.append({"error": error_text, "timestamp": timestamp})

        if history:
            results["Alarm history"] = history

        return results

    async def __fetch_html(self, url_path:str, timeout:int = 10) -> str | None:
        """Loads the contents of the webpage and returns them.

        Errors are silently ignored and logged directly to ha.

        :param str url_path:
            Path of the url to the requested webpage.

        :param int timeout:
            Timeout in seconds before the request fails with a timeout error.

        :returns str:
            Content of the response.

        :returns None:
            An error occured.
        """
        try:
            async with self.session.get(f"http://{self._device_ip}/{url_path}", timeout=timeout) as response:
                if response.status != 200:
                    self._logger.warning("Unexpected response status %s while fetching %s", response.status, url_path)

                return await response.text()
        except TimeoutError:
            self._logger.warning("Timeout after %s seconds while fetching %s", timeout, url_path)
        except ClientResponseError as err:
            self._logger.warning("Client response error while fetching %s: %s", url_path, err)
        except ClientError as err:
            self._logger.warning("Client error while fetching %s: %s", url_path, err)
