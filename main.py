import logging.config
import multiprocessing as mp

from config.logger import LOGGING
from src.utils import CITIES
from external.client import YandexWeatherAPI
from external.analyzer import analyze_json
from src.tasks import DataFetchingTask, DataCalculationTask


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_python_version():
    from src.utils import check_python_version

    check_python_version()


if __name__ == "__main__":
    mp.set_start_method('fork')
    logger.info("Fetching data ...")
    check_python_version()
    data_fetching_app_instacnce = DataFetchingTask(CITIES, YandexWeatherAPI.get_forecasting)
    fetched_data = data_fetching_app_instacnce.fetch_all()
    logger.info(f'Fetched data = {fetched_data}')
    data_calculation_instance = DataCalculationTask(fetched_data, analyze_json)
    analyzed_data = data_calculation_instance.calculate()
    logger.info(f'Analyzed data = {analyzed_data}')
