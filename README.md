# MySolArk API Scraper

This script fetches historical energy data from the MySolArk platform by using their SolarKCloud API, and 
processing/saving it in a CSV format for further analysis. 

It captures the following data points as provided by the API:
- solar production (PV)
- battery status
- grid usage 
- load consumption data

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  ```bash
  pip install requests pandas
  ```

## Setup Instructions

1. **Get Your Plant ID**
   - Log into MySolArk
   - Look at the URL when viewing your plant dashboard
   - The plant ID is in the URL, e.g., `.../overview/012345` -> Plant ID is "012345"
   - Update the `plant_id` variable in the script (found on line 115):
     ```python
     plant_id = "YOUR_PLANT_ID_HERE"
     ```

2. **Get Authentication Token**
   - Open your web browser and log into MySolArk
   - Open Developer Tools (F12 or right-click -> Inspect)
   - Go to the Network tab
   - Refresh the page
   - Click on any request to solarkcloud.com
     - If you're having trouble finding the URL then just look for something along the lines of `day?lan=en&date=2024-10-26&id=012345` in the column titled _Name_ and click on it
   - In the request headers, find 'Authorization'
   - Copy the full token value (including "Bearer")
   - Update the token in the script (line 44):
     ```python
     self.session.headers.update({
         'Authorization': 'Bearer YOUR_TOKEN_HERE',
         'User-Agent': 'Mozilla/5.0',
         'Accept': 'application/json'
     })
     ```

## Usage

### Basic Usage

Run the script with default settings (fetches last 30 days):
```bash
python solar_fetch.py
```

### Modifying Date Range

To fetch data for a specific date range, modify the `main()` function:

```python
def main():
    PLANT_ID = "YOUR_PLANT_ID_HERE"
    api = SolarKCloudAPI(PLANT_ID)
    
    # Define custom date range
    start_date = datetime(2024, 1, 1)  # Year, Month, Day
    end_date = datetime(2024, 1, 31)
    
    # Fetch data with custom range
    df = api.fetch_monthly_data(start_date=start_date, end_date=end_date)
    
    if df is not None:
        save_to_csv(df, 'solar_data_january.csv')  # Custom filename
```

### Output Customization

1. **Change CSV Filename**
   ```python
   save_to_csv(df, 'your_custom_filename.csv')
   ```

2. **Modify CSV Format**
   Edit the `save_to_csv()` function:
   ```python
   def save_to_csv(df, filename='solar_data.csv'):
       df.to_csv(filename, index=False, sep=';')  # Change separator
       # or
       df.to_excel(filename.replace('.csv', '.xlsx'))  # Save as Excel
   ```

## Data Format

The script outputs a CSV file with the following columns:

- Time: Time of day (HH:MM)
- Date: Date of reading (YYYY-MM-DD)
- PV (W): Solar production in Watts
- Battery (W): Battery charge/discharge (-ve = discharge)
- SOC (%): Battery State of Charge percentage
- Grid (W): Grid import/export
- Load (W): Energy consumption

## Troubleshooting

1. **Authentication Errors**
   - Token might have expired -> Get a new token
   - Verify the Authorization header format includes "Bearer"

2. **Rate Limiting**
   - If you get HTTP 429 errors, increase the sleep time:
     ```python
     time.sleep(2)  # Increase from 1 to 2 seconds
     ```

3. **No Data Retrieved**
   - Check your date range
   - Verify your Plant ID
   - Ensure you have internet connectivity

## Advanced Usage

### Selecting Specific Metrics

Modify the `process_daily_data()` function to select specific metrics:

```python
def process_daily_data(self, raw_data):
    # ... existing code ...
    
    # Select only specific metrics
    desired_metrics = ['PV', 'Load']  # Only get PV and Load
    df = df.filter(regex=f"({'|'.join(desired_metrics)})")
    
    return df
```

### Adding Data Analysis

Add analysis functions to process the data:

```python
def analyze_daily_production(df):
    daily_stats = df.groupby('Date').agg({
        'PV (W)': ['max', 'mean'],
        'Load (W)': ['max', 'mean'],
        'Grid (W)': ['max', 'mean']
    }).round(2)
    
    return daily_stats
```

## Notes

- The script includes a 1-second delay between requests to avoid overwhelming the server
- Authentication tokens typically expire after some time
- Data is fetched in daily chunks and combined
- The script **_should_** handle connection errors and invalid data gracefully. Godspeed if you somehow broke it.