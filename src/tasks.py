import logging
import concurrent.futures
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(self, url_dict: Dict[str, str], fetch_func: Callable[[str], Any], max_workers: int = 5) -> None:
        self.url_dict: Dict[str, str] = url_dict
        self.fetch_func: Callable[[str], Any] = fetch_func
        self.max_workers: int = max_workers

    def fetch_all(self) -> Dict[str, Any]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_city: Dict[concurrent.futures.Future, str] = {
                executor.submit(self.fetch_func, url): city for city, url in self.url_dict.items()
            }

            results: Dict[str, Any] = {}
            for future in concurrent.futures.as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    data = future.result()
                    results[city] = data
                except Exception as exc:
                    logger.error(f"Fetching data for {city} generated an exception: {exc}")
            return results


class DataCalculationTask:
    pass


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
