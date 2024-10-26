import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json


def process_daily_data(raw_data):
    """Process the raw JSON data into a pandas DataFrame"""
    if not raw_data or 'data' not in raw_data or 'infos' not in raw_data['data']:
        return None

    records = []
    date = None

    # Get the first timestamp's records to determine the date
    metrics = {}
    for info in raw_data['data']['infos']:
        label = info['label']
        unit = info['unit']

        for record in info['records']:
            time_str = record['time']
            value = float(record['value'])

            if time_str not in metrics:
                metrics[time_str] = {}

            metrics[time_str][f"{label} ({unit})"] = value

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(metrics, orient='index')
    df.index.name = 'Time'
    return df


class SolarKCloudAPI:
    def __init__(self, plant_id):
        self.base_url = "https://www.solarkcloud.com/api/v1"
        self.plant_id = plant_id
        self.session = requests.Session()

        # TODO: ADD AUTHORIZATION TOKEN BELOW INCLUDING THE 'Bearer' PART OF THE TOKEN
        self.session.headers.update({
            'Authorization': 'Bearer YOUR_TOKEN_HERE',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })

    def get_daily_data(self, date):
        """Fetch data for a specific date"""
        endpoint = f"{self.base_url}/plant/energy/{self.plant_id}/day"

        params = {
            'lan': 'en',
            'date': date.strftime('%Y-%m-%d'),
            'id': self.plant_id
        }

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {date}: {e}")
            return None

    def fetch_monthly_data(self, start_date=None, end_date=None):
        """Fetch data for a date range"""
        if start_date is None:
            # Default to last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        if end_date is None:
            end_date = datetime.now()

        all_data = []
        current_date = start_date

        while current_date <= end_date:
            print(f"Fetching data for {current_date.date()}")

            # Fetch data for the current date
            daily_data = self.get_daily_data(current_date)

            if daily_data:
                df = process_daily_data(daily_data)
                if df is not None:
                    # Add date column
                    df['Date'] = current_date.date()
                    all_data.append(df)

            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
            current_date += timedelta(days=1)

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data)
            # Reset index to make Date and Time regular columns
            combined_df.reset_index(inplace=True)
            return combined_df
        return None


def save_to_csv(df, filename='solar_data.csv'):
    """Save the DataFrame to a CSV file"""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def main():
    # TODO: ADD YOUR PLANT ID (IT CAN BE FOUND IN THE URL .../overview/<plantID>)
    plant_id = "XXXXXXX"

    # Initialize the API client
    api = SolarKCloudAPI(plant_id)

    # Fetch last 30 days of data
    df = api.fetch_monthly_data()

    if df is not None:
        # Save to CSV
        save_to_csv(df)

        # Print some basic statistics
        print("\nData Summary:")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Total records: {len(df)}")

        # Calculate daily totals
        daily_stats = df.groupby('Date').agg({
            'PV (W)': 'max',
            'Load (W)': 'max',
            'Grid (W)': 'max'
        }).round(2)

        print("\nDaily Maximum Values:")
        print(daily_stats)
    else:
        print("No data was collected")


if __name__ == "__main__":
    main()