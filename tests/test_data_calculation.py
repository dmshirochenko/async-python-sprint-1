import sys
from pathlib import Path
import unittest
from unittest.mock import Mock
from multiprocessing import Queue

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tasks import DataCalculationTask


def mock_calculation_function(input_data):
    return input_data * 2


class TestDataCalculationTask(unittest.TestCase):
    def setUp(self):
        self.sample_data = {1: 10, 2: 20, 3: 30}

    def test_execute(self):
        task = DataCalculationTask(self.sample_data, mock_calculation_function)
        results = task.execute()

        expected_results = {1: 20, 2: 40, 3: 60}
        self.assertEqual(results, expected_results)