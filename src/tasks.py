import logging
import concurrent.futures
from multiprocessing import Process, Queue
from typing import Any, Callable, Dict, List, Tuple, Optional

import numpy as np

logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(
        self, url_dict: Dict[str, str], fetch_func: Callable[[str, int], Any], max_workers: int = 5, timeout: int = 10
    ) -> None:
        self.url_dict: Dict[str, str] = url_dict
        self.fetch_func: Callable[[str, int], Any] = fetch_func
        self.max_workers: int = max_workers
        self.timeout: int = timeout

    def fetch_all(self) -> Dict[str, Any]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_city: Dict[concurrent.futures.Future, str] = {
                executor.submit(self.fetch_func, url, self.timeout): city for city, url in self.url_dict.items()
            }

            results: Dict[str, Any] = {}
            for future in concurrent.futures.as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    data = future.result(timeout=self.timeout)
                    results[city] = data
                except concurrent.futures.TimeoutError:
                    logger.exception(f"Fetching data for {city} timed out.")
                except Exception as exc:
                    logger.exception(f"Fetching data for {city} generated an exception: {exc}")

            return results


class Worker(Process):
    def __init__(self, func: Callable, task_queue: Queue, result_queue: Queue) -> None:
        super().__init__()
        self.func: Callable[[Any], Any] = func
        self.task_queue: Queue = task_queue
        self.result_queue: Queue = result_queue

    def run(self) -> None:
        while True:
            key, value = self.task_queue.get()
            if key is None:
                self.result_queue.put((None, None))
                break
            try:
                result = self.func(value)
                self.result_queue.put((key, result))
            except Exception as e:
                logger.exception(f"Error processing {key}: {e}")
                self.result_queue.put((key, None))


class MultiprocessingTaskManager:
    def __init__(self, data_dict: Dict[Any, Any], calc_func: Callable[[Any], Any], num_workers: int = 4) -> None:
        self.data_dict: Dict[Any, Any] = data_dict
        self.calc_func: Callable[[Any], Any] = calc_func
        self.num_workers: int = num_workers
        self.task_queue: Queue = Queue()
        self.result_queue: Queue = Queue()

    def _start_workers(self) -> List[Worker]:
        workers = []
        for _ in range(self.num_workers):
            worker = Worker(self.calc_func, self.task_queue, self.result_queue)
            workers.append(worker)
            worker.start()
        return workers

    def _send_tasks(self) -> None:
        for key, value in self.data_dict.items():
            self.task_queue.put((key, value))
        for _ in range(self.num_workers):
            self.task_queue.put((None, None))

    def _collect_results(self) -> Dict[Any, Any]:
        results = {}
        finished_workers = 0
        while finished_workers < self.num_workers:
            key, result = self.result_queue.get()
            if key is None:
                finished_workers += 1
            else:
                if not result:
                    logger.warning(f"Input data for key '{key}' is empty...")
                    continue
                else:
                    results[key] = result
        return results

    def _join_workers(self, workers: List[Worker]) -> None:
        for worker in workers:
            worker.join()

    def execute(self) -> Dict[Any, Any]:
        workers = self._start_workers()
        self._send_tasks()
        results = self._collect_results()
        self._join_workers(workers)
        return results


class DataCalculationTask(MultiprocessingTaskManager):
    def __init__(self, data_dict: Dict[Any, Any], calc_func: Callable[[Any], Any], num_workers: int = 4) -> None:
        super().__init__(data_dict, calc_func, num_workers)


class DataAnalyzingTask(MultiprocessingTaskManager):
    def __init__(self, data_dict: Dict[str, Any], num_workers: int = 4) -> None:
        super().__init__(data_dict, self.calculate_city_data, num_workers)

    @staticmethod
    def calculate_city_data(input_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
        if not input_data or "days" not in input_data or not input_data["days"]:
            logger.warning("Input data is empty or malformed...")
            return {}

        days_data = input_data["days"]
        logger.info(f"Days_data: {days_data}")

        total_temp_avg = 0
        total_relevant_cond_hours = 0
        valid_temp_days = 0

        for day in days_data:
            if "temp_avg" in day and day["temp_avg"] is not None:
                total_temp_avg += day["temp_avg"]
                valid_temp_days += 1

            if "relevant_cond_hours" in day and day["relevant_cond_hours"] is not None:
                total_relevant_cond_hours += day["relevant_cond_hours"]

        avg_temp = total_temp_avg / valid_temp_days if valid_temp_days else None

        return {"average_temperature": avg_temp, "total_relevant_condition_hours": total_relevant_cond_hours}

    def find_most_favorable_cities(self, results: Dict[str, Any]) -> List[str]:
        try:
            ranked_cities = sorted(
                results.items(),
                key=lambda x: (x[1].get("average_temperature", 0), x[1].get("total_relevant_condition_hours", 0)),
                reverse=True,
            )
            ranked_city_names = [city for city, _ in ranked_cities]
            return ranked_city_names
        except KeyError as e:
            logger.exception(f"Key error encountered: {e}. Check the data format.")
            return []
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return []

    def execute_and_rank(self) -> Tuple[Dict[str, Any], List[str]]:
        results = self.execute()
        return results, self.find_most_favorable_cities(results)


class DataAggregationTask:
    @staticmethod
    def write_aggregated_data_to_csv(
        original_data: Dict[str, Any],
        aggregated_data: Dict[str, Dict[str, Any]],
        ranked_cities: List[str],
        filename: str,
    ) -> None:
        try:
            csv_data = []
            for city in ranked_cities:
                avg_temp = aggregated_data.get(city, {}).get("average_temperature", 0)
                total_hours = aggregated_data.get(city, {}).get("total_relevant_condition_hours", 0)

                for day in original_data.get(city, {}).get("days", []):
                    row = (
                        city,
                        avg_temp,
                        total_hours,
                        day.get("date", ""),
                        day.get("hours_start", 0) or 0,
                        day.get("hours_end", 0) or 0,
                        day.get("hours_count", 0) or 0,
                        day.get("temp_avg", 0) or 0,
                        day.get("relevant_cond_hours", 0) or 0,
                    )
                    csv_data.append(row)

            dtype = [
                ("City", "U50"),
                ("Avg Temperature", "f8"),
                ("Total Cond Hours", "i8"),
                ("Date", "U10"),
                ("Hours Start", "i8"),
                ("Hours End", "i8"),
                ("Hours Count", "i8"),
                ("Daily Avg Temp", "f8"),
                ("Daily Cond Hours", "i8"),
            ]
            structured_array = np.array(csv_data, dtype=dtype)

            # Write to CSV file
            header = (
                "City,Avg Temperature,Total Cond Hours,Date,Hours Start,"
                "Hours End,Hours Count,Daily Avg Temp,Daily Cond Hours"
            )
            np.savetxt(filename, structured_array, delimiter=",", fmt="%s", header=header, comments="")

        except KeyError as e:
            logger.exception(f"Key error encountered: {e}. Check your data format.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
