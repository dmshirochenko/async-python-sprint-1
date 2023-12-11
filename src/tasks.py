import logging
import concurrent.futures
from multiprocessing import Process, Queue
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


class Worker(Process):
    def __init__(self, func: Callable, task_queue: Queue, result_queue: Queue):
        super().__init__()
        self.func = func
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            key, value = self.task_queue.get()
            if key is None:
                break
            result = self.func(value)
            self.result_queue.put((key, result))


class DataCalculationTask:
    def __init__(self, data_dict: Dict[Any, Any], calc_func: Callable[[Any], Any], num_workers: int = 4):
        self.data_dict = data_dict
        self.calc_func = calc_func
        self.num_workers = num_workers

    def calculate(self) -> Dict[Any, Any]:
        task_queue = Queue()
        result_queue = Queue()
        workers = []

        for _ in range(self.num_workers):
            worker = Worker(self.calc_func, task_queue, result_queue)
            workers.append(worker)
            worker.start()

        for key, value in self.data_dict.items():
            task_queue.put((key, value))

        for _ in range(self.num_workers):
            task_queue.put((None, None))

        results = {}
        for _ in range(len(self.data_dict)):
            key, result = result_queue.get()
            results[key] = result

        for worker in workers:
            worker.join()

        return results


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
