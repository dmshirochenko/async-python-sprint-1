import logging.config

from config.logger import LOGGING
from src.utils import CITIES
from external.client import YandexWeatherAPI
from src.tasks import DataFetchingTask


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_python_version():
    from src.utils import check_python_version

    check_python_version()


if __name__ == "__main__":
    logger.info("Fetching data ...")
    check_python_version()
    data_fetching_app_instacnce = DataFetchingTask(CITIES, YandexWeatherAPI.get_forecasting)
    fetched_data = data_fetching_app_instacnce.fetch_all()
