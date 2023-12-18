import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tasks import DataFetchingTask


# Mock fetch function
def mock_fetch_url(url, timeout):
    return f"Weather from {url}"


@pytest.fixture
def mock_fetch():
    return Mock(side_effect=mock_fetch_url)


def test_data_fetching_task(mock_fetch):
    urls = {"CITY1": "http://example.com/city1", "CITY2": "http://example.com/city2"}
    task = DataFetchingTask(urls, mock_fetch)

    results = task.fetch_all()
    assert len(results) == len(urls)
    for city, data in results.items():
        assert city in urls
        assert data == f"Weather from {urls[city]}"
    assert mock_fetch.call_count == len(urls)
