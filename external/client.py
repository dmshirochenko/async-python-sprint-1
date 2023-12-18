import json
import logging
from http import HTTPStatus
from urllib.request import urlopen
from urllib.error import URLError

ERR_MESSAGE_TEMPLATE = "Unexpected error: {error}"


logger = logging.getLogger(__name__)


class YandexWeatherAPI:
    """
    Base class for requests
    """

    def __do_req(url: str, timeout: int = 10) -> str:
        """Base request method"""
        try:
            with urlopen(url, timeout=timeout) as response:
                logger.info(f"Url to open {str(url)}")
                resp_body = response.read().decode("utf-8")
                data = json.loads(resp_body)
            if response.status != HTTPStatus.OK:
                raise Exception("Error during execute request. {}: {}".format(resp_body.status, resp_body.reason))
            return data
        except URLError as ex:
            logger.error(f"Request timed out: {ex}")
            raise Exception(ERR_MESSAGE_TEMPLATE.format(error="Request timed out"))
        except Exception as ex:
            logger.error(ex)
            raise Exception(ERR_MESSAGE_TEMPLATE.format(error=ex))

    @staticmethod
    def get_forecasting(url: str, timeout: int = 10):
        """
        :param url: url_to_json_data as str
        :return: response data as json
        """
        return YandexWeatherAPI.__do_req(url, timeout)
