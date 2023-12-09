import logging
import concurrent.futures

logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(self, url_dict, fetch_func, max_workers=5):
        self.url_dict = url_dict
        self.fetch_func = fetch_func
        self.max_workers = max_workers

    def fetch_all(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_city = {executor.submit(self.fetch_func, url): city for city, url in self.url_dict.items()}

            results = {}
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
