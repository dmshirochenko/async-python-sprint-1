import logging.config
import multiprocessing as mp

from config.logger import LOGGING
from src.utils import CITIES
from external.client import YandexWeatherAPI
from external.analyzer import analyze_json
from src.tasks import DataFetchingTask, DataCalculationTask, DataAnalyzingTask, DataAggregationTask


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_python_version():
    from src.utils import check_python_version

    check_python_version()


if __name__ == "__main__":
    check_python_version()
    mp.set_start_method("fork")  # could be removed if not used on mac/m1
    logger.info("Fetching data ...")
    data_fetching_app_instacnce = DataFetchingTask(CITIES, YandexWeatherAPI.get_forecasting)
    fetched_data = data_fetching_app_instacnce.fetch_all()
    logger.info(f"Fetched data = {fetched_data}")

    logger.info("Weather parameters calculation ...")
    data_calculation_instance = DataCalculationTask(fetched_data, analyze_json)
    calculated_data = data_calculation_instance.execute()
    logger.info(f"Calculated data = {calculated_data}")

    logger.info("Analyzing and ranking ...")
    city_rank_calc_isntance = DataAnalyzingTask(calculated_data)
    analyezed_data, most_favorable_cities = city_rank_calc_isntance.execute_and_rank()
    logger.info(f"Analyaed data = {analyezed_data}, Ranked data = {most_favorable_cities}")

    logger.info("Writing results to the file ...")
    DataAggregationTask.write_aggregated_data_to_csv(
        calculated_data, analyezed_data, most_favorable_cities, "output.csv"
    )
