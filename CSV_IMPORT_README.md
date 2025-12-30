# CSV to Flats Table Import Script

This script handles the import of CSV data into the PostgreSQL `flats` table, with proper column mapping and handling of duplicate column names.

## Features

- **Column Mapping**: Automatically maps CSV column names to database column names
- **Duplicate Handling**: Properly handles duplicate column names in the CSV (Last Activity Time, Flats Unique ID, Monthly Rent (Record Currency))
- **Data Cleaning**: Cleans and validates data types (text, numeric, dates, integers)
- **Error Handling**: Comprehensive error handling with detailed logging
- **Batch Processing**: Processes large CSV files efficiently with progress tracking

## Prerequisites

1. Python 3.7 or higher
2. PostgreSQL database with the `flats` table
3. Environment variables configured for database connection

## Installation

1. Install required dependencies:
```bash
pip install -r requirements_csv_import.txt
```

2. Set up your environment variables in a `.env` file:
```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_OPTIONS=your_database_options
```

## Usage

Run the script with your CSV file path:

```bash
python csv_to_flats_insert.py your_data_file.csv
```

### Example:
```bash
python csv_to_flats_insert.py flat_data.csv
```

## CSV Column Mapping

The script maps the following CSV columns to database columns:

### Basic Information
- `Flat Master Name` → `name`
- `Agreement Charges (Record Currency)` → `agreement_charges_record_charges`
- `Agreement Charges` → `agreement_charges`
- `Available Date for Next Booking` → `available_date_for_next_booking`
- `Balcony Type` → `balcony_type`
- `Block Name` → `block_name`
- `Built-up Area (Sq. Ft.)` → `built_up_area`

### Financial Information
- `Monthly Rent` → `selling_price`
- `Monthly Maintenance` → `maintenance_amount`
- `Garbage charges` → `garbage_amount`
- `Flat Security Deposit` → `flat_security_deposit`
- `Prepaid Move-Out Charge` → `move_out_charges`

### Property Details
- `Flat Type` → `flat_type`
- `Flat_Number` → `flat_number`
- `Floor Number` → `floor_number`
- `No Of Bathrooms` → `no_of_bathrooms`
- `Max Occupants` → `max_occupancy`

### Contact Information
- `Landlord Name` → `landlord_name`
- `Landlord Mailing City` → `landlord_mailing_city`
- `Landlord Mailing Country` → `landlord_mailing_country`
- `Landlord Mailing State` → `landlord_mailing_state`

### Duplicate Column Handling

The script handles these duplicate columns by position:

1. **Flats Unique ID** (appears twice)
   - First occurrence → `flat_unique_id`
   - Second occurrence → `flat_unique_id` (overwrites first)

2. **Last Activity Time** (appears twice)
   - First occurrence → `last_activity_time`
   - Second occurrence → `last_activity_time` (overwrites first)

3. **Monthly Rent (Record Currency)** (appears twice)
   - Mapped to `monthly_rent_record_currency`

## Data Type Handling

The script automatically handles different data types:

- **Text Fields**: Trimmed and cleaned
- **Numeric Fields**: Currency symbols removed, converted to float/decimal
- **Date Fields**: Multiple date formats supported (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
- **Integer Fields**: Converted to integers for counts and IDs

## Error Handling

- **Row-level errors**: Logged but don't stop the entire import
- **Connection errors**: Script exits with proper error message
- **Data validation errors**: Invalid data is set to NULL
- **Missing environment variables**: Checked before execution

## Logging

The script provides detailed logging:
- Progress updates every 100 rows
- Error details for failed rows
- Summary of successful and failed rows
- Database connection status

## Sample Output

```
2024-01-15 10:30:00,123 - INFO - Starting CSV import from: flat_data.csv
2024-01-15 10:30:00,456 - INFO - Found 75 columns in CSV
2024-01-15 10:30:00,789 - INFO - Mapped 68 columns to database
2024-01-15 10:30:01,012 - INFO - Processed 100 rows...
2024-01-15 10:30:02,345 - INFO - Processed 200 rows...
2024-01-15 10:30:05,678 - INFO - Successfully processed 1334 rows
2024-01-15 10:30:05,901 - INFO - Failed rows: 0
2024-01-15 10:30:05,234 - INFO - CSV import completed successfully!
```

## Troubleshooting

### Common Issues:

1. **"Database connection failed"**
   - Check your environment variables
   - Verify database is running and accessible

2. **"CSV file not found"**
   - Check the file path
   - Ensure the file exists and is readable

3. **"Missing required environment variables"**
   - Ensure all required variables are set in your .env file

4. **Data validation errors**
   - Check the CSV data format
   - Ensure date formats are consistent
   - Verify numeric fields don't contain invalid characters

### Performance Tips:

- For large CSV files (>10,000 rows), the script processes in batches
- Monitor database connection limits
- Ensure sufficient disk space for database growth

## Support

For issues or questions, check the logs first. The script provides detailed error messages that should help identify the problem.
