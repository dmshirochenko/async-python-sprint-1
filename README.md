
## Overview

This tool is designed to fetch, calculate, and analyze weather conditions for a predefined list of cities using the Yandex Weather API. It processes weather data to determine the average temperature and precipitation information for each city over a specified period. The analysis helps identify the most favorable city for travel based on weather conditions.

# Installation and Running

1. To run the script:
2. `python -m pip install --upgrade pip`
3. `pip install -r requirements.txt`
4. Rename `.env_example` to `.env`
5. `python main.py`

The script's output will be saved in the file `output.csv`.

# Project Structure
- `main.py`: The project's entry point.
- `src/tasks.py`: Contains the classes `DataFetchingTask`, `DataCalculationTask`, `DataAnalyzingTask`, `DataAggregationTask`.
- `external/`: Folder for external code or libraries.
- `tests/`: Folder containing tests to verify the project's functionality.

### Features

1. **Weather Data Collection**: Retrieves weather conditions for cities listed in the `CITIES` variable within [utils.py](utils.py) using the `YandexWeatherAPI` class from the `external/client.py` module. An example of using `YandexWeatherAPI` is provided for reference.

2. **Weather Data Analysis**:
   - Calculates the average temperature and analyzes precipitation information during the day from 9 AM to 7 PM.
   - Determines the total hours without precipitation (rain, snow, hail, or storm) within the specified timeframe.
   - Temperature and precipitation data paths are `forecasts>[day]>hours>temp` and `forecasts>[day]>hours>condition`, respectively.
   - Weather conditions are detailed in the `condition` section available [here](https://yandex.ru/dev/weather/doc/dg/concepts/forecast-test.html#resp-format__forecasts) or in the [conditions.txt](examples/conditions.txt) file.

3. **Data Aggregation**: Merges the analyzed data and saves the result in a structured format(CSV).

4. **Final Analysis**: Concludes which city is most favorable for travel based on the highest average temperature and maximum hours without precipitation. Multiple cities are listed if they share the top spot.
