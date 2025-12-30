#!/usr/bin/env python3
"""
Flat Data Comparison Script
Compares Excel data with database flats table to identify mismatches.
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_db():
    """Create database connection using environment variables"""
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            options=os.getenv("DB_OPTIONS", "")
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def normalize_rent_status(value):
    """Convert Excel rent status values to database values"""
    if pd.isna(value):
        return None
    
    value_str = str(value).strip().lower()
    mapping = {
        'yes': 1, 'y': 1, 'true': 1, '1': 1,
        'no': 0, 'n': 0, 'false': 0, '0': 0
    }
    return mapping.get(value_str, None)

def normalize_booking_hold_status(value):
    """Convert Excel booking hold status values to database values"""
    if pd.isna(value):
        return None
    
    value_str = str(value).strip().lower()
    mapping = {
        'free': 1, 'FREE': 1, 'Free': 1,
        'on hold': 2, 'ON HOLD': 2, 'On Hold': 2, 'hold': 2, 'HOLD': 2, 'Hold': 2
    }
    return mapping.get(value_str, None)

def normalize_date(value):
    """Normalize date values for comparison"""
    if pd.isna(value):
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if value == '' or value.lower() in ['null', 'none', 'n/a', 'na', '-']:
            return None
    
    try:
        if isinstance(value, str):
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%b %d, %Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None
        elif hasattr(value, 'date'):
            return value.date()
        elif hasattr(value, 'to_pydatetime'):
            return value.to_pydatetime().date()
        else:
            return None
    except:
        return None

def get_flat_data_from_db():
    """Retrieve flat data from database"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Get all relevant columns from flats table
        query = """
        SELECT 
            name,
            slug,
            flat_available_rent_status,
            flat_booking_hold_status,
            flat_occupancy_status,
            flat_next_booking_status,
            available_date_for_next_booking
        FROM flats
        WHERE name IS NOT NULL
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Create DataFrame
        db_df = pd.DataFrame(rows, columns=columns)
        
        logger.info(f"Retrieved {len(db_df)} records from database")
        return db_df
        
    except Exception as e:
        logger.error(f"Error retrieving data from database: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def read_excel_data(excel_file_path):
    """Read and process Excel data"""
    try:
        # First, try to read with different header row options
        df = None
        header_row = None
        
        # Try different header rows (0, 1, 2, 3, 4, 5, 6) to find the actual column names
        for skip_rows in range(7):
            try:
                temp_df = pd.read_excel(excel_file_path, header=skip_rows)
                logger.info(f"Trying header row {skip_rows}: columns = {list(temp_df.columns)[:10]}...")
                
                # Check if we found the actual column headers
                if 'Flat Master Name' in temp_df.columns:
                    df = temp_df
                    header_row = skip_rows
                    logger.info(f"Found proper headers at row {skip_rows}")
                    break
                    
            except Exception as e:
                logger.debug(f"Failed to read with header={skip_rows}: {e}")
                continue
        
        # If we still haven't found proper headers, try reading without header and look for the row
        if df is None:
            logger.info("Searching for header row manually...")
            temp_df = pd.read_excel(excel_file_path, header=None)
            
            # Search for the row containing 'Flat Master Name'
            for idx, row in temp_df.iterrows():
                if row.astype(str).str.contains('Flat Master Name', na=False).any():
                    logger.info(f"Found 'Flat Master Name' in row {idx}")
                    # Re-read with this row as header
                    df = pd.read_excel(excel_file_path, header=idx)
                    header_row = idx
                    break
        
        if df is None:
            logger.error("Could not find proper column headers in Excel file")
            return None
        
        logger.info(f"Excel file loaded with {len(df)} rows and {len(df.columns)} columns (header at row {header_row})")
        logger.info(f"Excel columns: {list(df.columns)}")
        
        # Ensure we have the required columns
        required_columns = [
            'Flat Master Name',
            'Flat Available to Rent Status',
            'Flat Booking Hold Status',
            'Flat Occupancy Status',
            'Flat Next Booking Status',
            'Available Date for Next Booking'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns in Excel: {missing_columns}")
            return None
        
        # Rename columns for easier processing
        df = df.rename(columns={
            'Flat Master Name': 'name',
            'Flat Available to Rent Status': 'excel_rent_status',
            'Flat Booking Hold Status': 'excel_booking_status',
            'Flat Occupancy Status': 'excel_occupancy_status',
            'Flat Next Booking Status': 'excel_next_booking_status',
            'Available Date for Next Booking': 'excel_available_date'
        })
        
        # Filter out rows where name is null/empty
        df = df.dropna(subset=['name'])
        df = df[df['name'].str.strip() != '']
        
        logger.info(f"After filtering, {len(df)} rows with valid names")
        
        return df
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise

def compare_data(excel_df, db_df):
    """Compare Excel data with database data and identify mismatches"""
    mismatches = []
    
    logger.info("Starting data comparison...")
    
    # Create a lookup dictionary for database data using name as key
    db_lookup = {}
    for _, row in db_df.iterrows():
        db_lookup[row['name']] = row
    
    processed_count = 0
    for _, excel_row in excel_df.iterrows():
        flat_name = excel_row['name']
        processed_count += 1
        
        if processed_count % 100 == 0:
            logger.info(f"Processed {processed_count} records...")
        
        # Find corresponding database record
        if flat_name not in db_lookup:
            mismatches.append({
                'flat_name': flat_name,
                'slug': 'NOT_FOUND_IN_DB',
                'issue_type': 'MISSING_FROM_DB',
                'excel_value': 'N/A',
                'db_value': 'N/A',
                'details': 'Flat not found in database'
            })
            continue
        
        db_row = db_lookup[flat_name]
        flat_slug = db_row['slug'] if db_row['slug'] else flat_name.lower().strip()
        
        # Compare Flat Available to Rent Status
        excel_rent_status = normalize_rent_status(excel_row['excel_rent_status'])
        db_rent_status = db_row['flat_available_rent_status']
        
        if excel_rent_status != db_rent_status and excel_rent_status is not None:
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'RENT_STATUS_MISMATCH',
                'excel_value': f"{excel_row['excel_rent_status']} -> {excel_rent_status}",
                'db_value': db_rent_status,
                'details': f"Excel: {excel_row['excel_rent_status']} (normalized: {excel_rent_status}), DB: {db_rent_status}"
            })
        
        # Compare Flat Booking Hold Status
        excel_booking_status = normalize_booking_hold_status(excel_row['excel_booking_status'])
        db_booking_status = db_row['flat_booking_hold_status']
        
        if excel_booking_status != db_booking_status and excel_booking_status is not None:
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'BOOKING_HOLD_STATUS_MISMATCH',
                'excel_value': f"{excel_row['excel_booking_status']} -> {excel_booking_status}",
                'db_value': db_booking_status,
                'details': f"Excel: {excel_row['excel_booking_status']} (normalized: {excel_booking_status}), DB: {db_booking_status}"
            })
        
        # Compare Flat Occupancy Status (direct comparison)
        excel_occupancy = excel_row['excel_occupancy_status']
        db_occupancy = db_row['flat_occupancy_status']
        
        if not pd.isna(excel_occupancy) and str(excel_occupancy).strip() != str(db_occupancy).strip() and str(excel_occupancy).strip() != '':
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'OCCUPANCY_STATUS_MISMATCH',
                'excel_value': excel_occupancy,
                'db_value': db_occupancy,
                'details': f"Excel: {excel_occupancy}, DB: {db_occupancy}"
            })
        
        # Compare Flat Next Booking Status (direct comparison)
        excel_next_booking = excel_row['excel_next_booking_status']
        db_next_booking = db_row['flat_next_booking_status']
        
        if not pd.isna(excel_next_booking) and str(excel_next_booking).strip() != str(db_next_booking).strip() and str(excel_next_booking).strip() != '':
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'NEXT_BOOKING_STATUS_MISMATCH',
                'excel_value': excel_next_booking,
                'db_value': db_next_booking,
                'details': f"Excel: {excel_next_booking}, DB: {db_next_booking}"
            })
        
        # Compare Available Date for Next Booking
        excel_date = normalize_date(excel_row['excel_available_date'])
        db_date = db_row['available_date_for_next_booking']
        
        if excel_date is not None and db_date is not None:
            if excel_date != db_date:
                mismatches.append({
                    'flat_name': flat_name,
                    'slug': flat_slug,
                    'issue_type': 'AVAILABLE_DATE_MISMATCH',
                    'excel_value': excel_date,
                    'db_value': db_date,
                    'details': f"Excel: {excel_date}, DB: {db_date}"
                })
        elif excel_date is not None and db_date is None:
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'AVAILABLE_DATE_MISSING_IN_DB',
                'excel_value': excel_date,
                'db_value': 'NULL',
                'details': f"Excel has date {excel_date}, but DB is NULL"
            })
        elif excel_date is None and db_date is not None:
            mismatches.append({
                'flat_name': flat_name,
                'slug': flat_slug,
                'issue_type': 'AVAILABLE_DATE_MISSING_IN_EXCEL',
                'excel_value': 'NULL',
                'db_value': db_date,
                'details': f"Excel is NULL, but DB has date {db_date}"
            })
    
    logger.info(f"Comparison completed. Found {len(mismatches)} mismatches.")
    return mismatches

def generate_report(mismatches, output_file='flat_mismatches_report.csv'):
    """Generate a detailed report of mismatches"""
    try:
        if not mismatches:
            logger.info("No mismatches found! All data is consistent.")
            return
        
        # Convert to DataFrame for easy export
        report_df = pd.DataFrame(mismatches)
        
        # Sort by flat name and issue type
        report_df = report_df.sort_values(['flat_name', 'issue_type'])
        
        # Export to CSV
        report_df.to_csv(output_file, index=False)
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("MISMATCH SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total mismatches found: {len(mismatches)}")
        
        # Group by issue type
        issue_counts = report_df['issue_type'].value_counts()
        for issue_type, count in issue_counts.items():
            logger.info(f"{issue_type}: {count}")
        
        logger.info(f"\nDetailed report saved to: {output_file}")
        
        # Show unique flat slugs with issues
        unique_flats_with_issues = report_df['slug'].unique()
        logger.info(f"\nUnique flats with issues ({len(unique_flats_with_issues)}):")
        for slug in sorted(unique_flats_with_issues):
            if slug != 'NOT_FOUND_IN_DB':
                logger.info(f"  - {slug}")
        
        # Show first 10 mismatches as examples
        logger.info(f"\nFirst 10 mismatches (examples):")
        for i, mismatch in enumerate(mismatches[:10]):
            logger.info(f"{i+1}. {mismatch['flat_name']} ({mismatch['slug']})")
            logger.info(f"   Issue: {mismatch['issue_type']}")
            logger.info(f"   Details: {mismatch['details']}")
        
        if len(mismatches) > 10:
            logger.info(f"   ... and {len(mismatches) - 10} more (see full report)")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise

def find_missing_flat_names(excel_df, db_df, output_file='missing_flat_names.txt'):
    """Find and save Flat Master Names that exist in Excel but not in database"""
    # Create a set of database flat names for quick lookup
    db_flat_names = set(db_df['name'].tolist())
    
    # Find Excel flats not in database
    excel_flat_names = excel_df['name'].tolist()
    missing_flat_names = [name for name in excel_flat_names if name not in db_flat_names]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_missing = []
    for name in missing_flat_names:
        if name not in seen:
            unique_missing.append(name)
            seen.add(name)
    
    missing_flat_names = sorted(unique_missing)
    
    logger.info(f"\n{'='*70}")
    logger.info("FLAT MASTER NAMES MISSING FROM DATABASE")
    logger.info(f"{'='*70}")
    logger.info(f"Total Excel flats: {len(excel_flat_names)}")
    logger.info(f"Total database flats: {len(db_flat_names)}")
    logger.info(f"Flats in Excel but not in database: {len(missing_flat_names)}")
    
    if missing_flat_names:
        logger.info(f"\nMissing Flat Master Names:")
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Flat Master Names that exist in Excel but are missing from database:\n")
            f.write("="*70 + "\n\n")
            
            for i, flat_name in enumerate(missing_flat_names, 1):
                logger.info(f"  {i:3d}. {flat_name}")
                f.write(f"{i:3d}. {flat_name}\n")
            
            f.write(f"\nSummary:\n")
            f.write(f"Total Excel flats: {len(excel_flat_names)}\n")
            f.write(f"Total database flats: {len(db_flat_names)}\n")
            f.write(f"Missing from database: {len(missing_flat_names)}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info(f"\nMissing flat names saved to: {output_file}")
    else:
        logger.info("✓ All Excel flats exist in the database!")
    
    return missing_flat_names

def main():
    """Main function"""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python flat_data_comparison.py <excel_file_path> [--missing-only]")
        print("Example: python flat_data_comparison.py Flat_data_before_live.xlsx")
        print("Example: python flat_data_comparison.py Flat_data_before_live.xlsx --missing-only")
        print("\nOptions:")
        print("  --missing-only    Only show Flat Master Names missing from database")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    missing_only = len(sys.argv) == 3 and sys.argv[2] == '--missing-only'
    
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        sys.exit(1)
    
    logger.info(f"Starting data comparison between {excel_file_path} and database")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    try:
        # Read Excel data
        logger.info("Reading Excel file...")
        excel_df = read_excel_data(excel_file_path)
        if excel_df is None:
            sys.exit(1)
        
        # Get database data
        logger.info("Retrieving database data...")
        db_df = get_flat_data_from_db()
        
        if missing_only:
            # Only find and report missing flat names
            logger.info("Finding Flat Master Names missing from database...")
            missing_names = find_missing_flat_names(excel_df, db_df)
            logger.info(f"Found {len(missing_names)} flat names missing from database.")
        else:
            # Full comparison
            logger.info("Comparing data...")
            mismatches = compare_data(excel_df, db_df)
            
            # Generate report
            logger.info("Generating report...")
            generate_report(mismatches)
            
            # Also generate the missing names report
            logger.info("Finding missing flat names...")
            missing_names = find_missing_flat_names(excel_df, db_df)
        
        logger.info("Data comparison completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data comparison: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
