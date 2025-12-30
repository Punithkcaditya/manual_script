# Flat Data Comparison Script

This script compares data between Excel file (`Flat_data_before_live.xlsx`) and the PostgreSQL flats table to identify mismatches.

## Features

The script compares the following fields:

1. **Flat Available to Rent Status**: Converts Excel values (yes/no) to database values (1/0)
2. **Flat Booking Hold Status**: Converts Excel values (free/on hold) to database values (1/2)
3. **Flat Occupancy Status**: Direct string comparison
4. **Flat Next Booking Status**: Direct string comparison  
5. **Available Date for Next Booking**: Date comparison with normalization

## Prerequisites

1. Install required dependencies:
```bash
pip install -r requirements_csv_import.txt
```

2. Ensure your `.env` file contains database connection details:
```
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=your_port
DB_OPTIONS=your_options (optional)
```

## Usage

### Full Comparison
Run the script with the Excel file path for complete comparison:

```bash
python flat_data_comparison.py Flat_data_before_live.xlsx
```

### Missing Flats Only
To only find Flat Master Names that exist in Excel but not in database:

```bash
python flat_data_comparison.py Flat_data_before_live.xlsx --missing-only
```

### Simple Missing Flats Check
For a quick check of only missing flat names, use the dedicated script:

```bash
python find_missing_flats.py Flat_data_before_live.xlsx
```

## Output

### Full Comparison Output
The script will:

1. Log progress to console
2. Generate a detailed CSV report (`flat_mismatches_report.csv`) containing:
   - Flat name and slug
   - Issue type 
   - Excel vs Database values
   - Detailed descriptions

3. Print a summary showing:
   - Total number of mismatches
   - Breakdown by issue type
   - **Separate section highlighting Flat Master Names missing from database**
   - List of unique flat slugs with issues
   - Examples of first 10 mismatches

4. Create a dedicated file (`missing_flat_names.txt`) with just the missing flat names

### Missing Flats Only Output
When using `--missing-only` or the dedicated `find_missing_flats.py` script:

1. Console output showing:
   - Total flats in Excel vs Database
   - Count of missing flats
   - **Complete numbered list of missing Flat Master Names**

2. Files created:
   - `missing_flat_names.txt` - Formatted text file with missing names
   - `missing_flat_names.csv` - CSV file for easy import/processing

## Issue Types

- `MISSING_FROM_DB`: Flat exists in Excel but not in database
- `RENT_STATUS_MISMATCH`: Flat Available to Rent Status doesn't match
- `BOOKING_HOLD_STATUS_MISMATCH`: Flat Booking Hold Status doesn't match
- `OCCUPANCY_STATUS_MISMATCH`: Flat Occupancy Status doesn't match
- `NEXT_BOOKING_STATUS_MISMATCH`: Flat Next Booking Status doesn't match
- `AVAILABLE_DATE_MISMATCH`: Available Date for Next Booking doesn't match
- `AVAILABLE_DATE_MISSING_IN_DB`: Date exists in Excel but not in database
- `AVAILABLE_DATE_MISSING_IN_EXCEL`: Date exists in database but not in Excel

## Value Mappings

### Flat Available to Rent Status
- Excel: `yes`, `y`, `true`, `1` → Database: `1`
- Excel: `no`, `n`, `false`, `0` → Database: `0`

### Flat Booking Hold Status  
- Excel: `free`, `Free`, `FREE` → Database: `1`
- Excel: `on hold`, `On Hold`, `ON HOLD`, `hold`, `Hold`, `HOLD` → Database: `2`

## Script Structure

- **Database Connection**: Uses environment variables for secure connection
- **Data Normalization**: Handles different formats and case variations
- **Comprehensive Comparison**: Checks all required fields systematically
- **Detailed Reporting**: Provides actionable insights for data reconciliation
