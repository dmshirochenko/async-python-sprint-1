import argparse
import json
import logging
from dataclasses import dataclass, field
from functools import reduce
from operator import getitem
from typing import Optional, List, Dict


INPUT_FORECAST_PATH = "forecasts"
INPUT_DATE_PATH = "date"

INPUT_HOURS_PATH = "hours"
INPUT_HOUR_PATH = "hour"
INPUT_TEMPERATURE_PATH = "temp"
INPUT_CONDITION_PATH = "condition"
INPUT_DAY_HOURS_START = 9
INPUT_DAY_HOURS_END = 19
INPUT_DAY_SUITABLE_CONDITIONS = (
    "clear",
    "partly-cloudy",
    "cloudy",
    "overcast",
)

OUTPUT_RAW_DATA_KEY = "raw_data"
OUTPUT_DAYS_KEY = "days"
DEFAULT_OUTPUT_RESULT = {
    OUTPUT_DAYS_KEY: [],
}


@dataclass
class HourInfo:
    raw_data: Dict[str, tuple[str, int]] = field(repr=False)
    condition: Optional[str] = field(init=False, default=None)
    temperature: Optional[int] = field(init=False, default=None)
    hour: Optional[int] = field(init=False, default=None)

    @staticmethod
    def is_hour_suitable(data):
        hour = int(data[INPUT_HOUR_PATH])
        return (hour >= INPUT_DAY_HOURS_START) and (hour <= INPUT_DAY_HOURS_END)

    @property
    def is_cond_suitable(self):
        return self.condition in INPUT_DAY_SUITABLE_CONDITIONS

    def __post_init__(self):
        self.parse()

    def parse(self):
        if not self.raw_data:
            return

        self.hour = int(self.raw_data[INPUT_HOUR_PATH])
        self.temperature = int(deep_getitem(self.raw_data, INPUT_TEMPERATURE_PATH))
        self.condition = deep_getitem(self.raw_data, INPUT_CONDITION_PATH)


@dataclass
class DayInfo:
    raw_data: Dict[str, tuple[str, int]] = field(repr=False)
    hours: Optional[List[HourInfo]] = field(init=False, repr=False, default=None)

    date: Optional[str] = field(init=False, default=None)
    hour_start: Optional[int] = field(init=False, default=None)
    hour_end: Optional[int] = field(init=False, default=None)

    hours_count: Optional[int] = field(init=False, default=None)
    temperature_avg: Optional[float] = field(init=False, default=None)
    relevant_condition_hours: int = field(init=False, default=0)

    def to_json(self):
        return {
            "date": self.date,
            "hours_start": self.hour_start,
            "hours_end": self.hour_end,
            "hours_count": self.hours_count,
            "temp_avg": round(self.temperature_avg, 3) if self.temperature_avg else self.temperature_avg,
            "relevant_cond_hours": self.relevant_condition_hours,
        }

    def __post_init__(self):
        self.parse()

    def parse(self):
        if not self.raw_data:
            return

        self.date = self.raw_data[INPUT_DATE_PATH]

        temp = 0
        hours_count = 0
        conds_count = 0

        self.hours = self.raw_data[INPUT_HOURS_PATH]
        for hour_data in self.hours:
            if not HourInfo.is_hour_suitable(hour_data):
                continue

            h_info = HourInfo(raw_data=hour_data)
            h_hour = h_info.hour
            self.hour_start = self.hour_start or h_hour
            self.hour_end = h_hour

            temp += h_info.temperature
            if h_info.is_cond_suitable:
                conds_count += 1
            hours_count += 1

        self.relevant_condition_hours = conds_count
        self.hours_count = hours_count
        if hours_count > 0:
            self.temperature_avg = temp / hours_count


def deep_getitem(obj, path: str):
    try:
        return reduce(getitem, path.split(">"), obj)
    except (KeyError, TypeError):
        return None


def analyze_json(data):
    if not data:
        logging.warning("Input data is empty...")
        return {}

    # analyzing days
    time_start = None
    time_end = None

    logging.info(f"Data {data}")
    days_data = deep_getitem(data, INPUT_FORECAST_PATH)
    days = []
    for day_data in days_data:
        d_info = DayInfo(raw_data=day_data)
        d_date = d_info.date

        time_start = time_start or d_date
        time_end = d_date

        days.append(d_info.to_json())

    result = DEFAULT_OUTPUT_RESULT
    result[OUTPUT_DAYS_KEY] = days
    return result
