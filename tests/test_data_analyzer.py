import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tasks import DataAnalyzingTask


class TestDataAnalyzingTask(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "City1": {"days": [{"temp_avg": 20, "relevant_cond_hours": 5}, {"temp_avg": 22, "relevant_cond_hours": 4}]},
            "City2": {"days": [{"temp_avg": 25, "relevant_cond_hours": 3}, {"temp_avg": 23, "relevant_cond_hours": 6}]},
        }

    def test_data_processing(self):
        task = DataAnalyzingTask(self.sample_data)
        results = task.execute()

        expected_results = {
            "City1": {"average_temperature": 21, "total_relevant_condition_hours": 9},
            "City2": {"average_temperature": 24, "total_relevant_condition_hours": 9},
        }
        self.assertEqual(results, expected_results)

    def test_ranking(self):
        task = DataAnalyzingTask(self.sample_data)
        _, ranked_cities = task.execute_and_rank()

        expected_ranking = ["City2", "City1"]
        self.assertEqual(ranked_cities, expected_ranking)

    def test_execute_and_rank(self):
        task = DataAnalyzingTask(self.sample_data)
        results, ranked_cities = task.execute_and_rank()

        self.assertIsNotNone(results)
        self.assertIsNotNone(ranked_cities)
        self.assertIn("City1", ranked_cities)
        self.assertIn("City2", ranked_cities)