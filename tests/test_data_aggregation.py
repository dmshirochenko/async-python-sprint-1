import sys
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tasks import DataAggregationTask


class TestDataAggregationTask(unittest.TestCase):
    def setUp(self):
        self.original_data = {
            "City1": {"days": [{"date": "2023-01-01", "temp_avg": 20, "relevant_cond_hours": 5}]},
            "City2": {"days": [{"date": "2023-01-02", "temp_avg": 25, "relevant_cond_hours": 3}]},
        }
        self.aggregated_data = {
            "City1": {"average_temperature": 20, "total_relevant_condition_hours": 5},
            "City2": {"average_temperature": 25, "total_relevant_condition_hours": 3},
        }
        self.ranked_cities = ["City2", "City1"]
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_name = self.temp_file.name

        def test_write_aggregated_data_to_csv(self):
            DataAggregationTask.write_aggregated_data_to_csv(
                self.original_data, self.aggregated_data, self.ranked_cities, self.temp_file_name
            )

            # Read the file and check its content
            with open(self.temp_file_name, "r") as file:
                lines = file.readlines()
                self.assertIn("City,Avg Temperature,Total Cond Hours", lines[0])
                self.assertIn("City1", lines[1])
                self.assertIn("City2", lines[2])

        def tearDown(self):
            os.remove(self.temp_file_name)