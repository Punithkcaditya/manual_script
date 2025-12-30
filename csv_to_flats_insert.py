#!/usr/bin/env python3
"""
CSV to Flats Table Insertion Script
Handles CSV data import into PostgreSQL flats table with column mapping and duplicate handling.
"""

import csv
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

def get_csv_to_db_mapping():
    """
    Returns mapping between CSV column names and database column names.
    Handles duplicate CSV column names by using positional mapping.
    """
    return {
        # Basic Information
        'Flat Master Name': 'name',
        'Agreement Charges (Record Currency)': 'agreement_charges_record_charges',
        'Agreement Charges': 'agreement_charges',
        'Available Date for Next Booking': 'available_date_for_next_booking',
        'Balcony Type': 'balcony_type',
        'Block Name': 'block_name',
        'Booking2Contarct days': 'booking_2_contarct_days',
        'Built-up Area (Sq. Ft.)': 'built_up_area',
        'Caretaker Master': 'care_taker_master',
        'Catalogue Price last updated date': 'catalogue_price_last_updates_date',
        'CIR Tracker': 'cir_tracker',
        'Cluster Name': 'cluster_name',
        'Created By': 'created_by',
        'Created Time': 'created_time',
        'Currency': 'currency',
        'Current Move-In Date': 'current_move_in_date',
        'Current Check-Out Date': 'current_check_out_date',
        'Current Tenant ID': 'current_tenant_id',
        'Electricity Meter Number': 'electricity_meter_number',
        'Email Opt Out': 'email_opt_out',
        'Exchange Rate': 'exchange_rate',
        'Flat Available to Rent Status': 'flat_available_rent_status',
        'Flat Booking Hold Status': 'flat_booking_hold_status',
        'Flat Category': 'flat_category',
        'Flat Facing': 'flat_facing',
        'Flat Iframe Embed for Virtual Tour': 'videos',  # Mapped to videos field
        'Flat Mailing City': 'flat_mailing_city',
        'Flat Mailing Country': 'flat_mailing_country',
        'Flat Mailing State': 'flat_mailing_state',
        'Flat Mailing Street': 'flat_mailing_street',
        'Flat Mailing Zip': 'flat_mailing_zip',
        'Flat Master Owner': 'flat_master_owner',
        'Flat Next Booking Status': 'flat_next_booking_status',
        'Flat Occupancy Status': 'flat_occupancy_status',
        'Flat Rent Next Start Date': 'flat_rent_next_start_date',
        'Flat Security Deposit (Record Currency)': 'flat_security_deposit_record_currency',
        'Flat Security Deposit': 'flat_security_deposit',
        'Flat Type': 'flat_type',
        'Flat Video': 'flat_video',
        'Flat_Number': 'flat_number',
        'Floor Number': 'floor_number',
        'Garbage charges (Record Currency)': 'garbage_amount_record_currency',
        'Garbage charges': 'garbage_amount',
        'Inside the Flat': 'inside_the_flat_description',
        'Inventory Trackers': 'track_inventory',
        'Landlord Mailing City': 'landlord_mailing_city',
        'Landlord Mailing Country': 'landlord_mailing_country',
        'Landlord Mailing State': 'landlord_mailing_state',
        'Landlord Mailing Street': 'landlord_mailing_street',
        'Landlord Mailing Zip': 'landlord_mailing_zip',
        'Landlord Name': 'landlord_name',
        'Website_Flat_URL': 'website_flat_url',
        'Validatortag': 'validatortag',
        'Update Status': 'update_status',
        'Unsubscribed Time': 'unsubsribed_time',
        'Terms & Conditions': 'terms_conditions',
        'Tag': 'product_tags',
        'Super Built-up Area (Sq. Ft.)': 'super_built_area',
        'Sample Contract Link': 'sample_contract_link',
        'Reserved Car Parking Available': 'reserved_car_parking_available',
        'Renewal rate': 'renewal_rate',
        'Record Id': 'record_id',
        'Property Unique ID': 'property_unique_id',
        'Property Onboarded Date': 'added_date',
        'Property Master': 'property_master',
        'Prepaid Move-Out Charge': 'move_out_charges',
        'Parking Queue': 'parking_queue',
        'No Of Bathrooms': 'no_of_bathrooms',
        'Next Move-In Date': 'next_move_in_date',
        'Next Booking ID': 'next_booking_id',
        'Monthly Rent': 'selling_price',
        'Long Description': 'description',
        'Max Occupants': 'max_occupancy',
        'Meta Title': 'meta_title',
        'Modified By': 'modified_by',
        'Monthly Maintenance': 'maintenance_amount',
        'Meta Description': 'meta_description',
        'Modified Time': 'modified_date',
        'Wifi ID': 'wifi_id',
        'Wifi Password': 'wifi_password',
        
        # Additional columns I might have missed
        'Booking2Contarct days': 'booking_2_contarct_days',
        'Caretaker Master': 'care_taker_master',
        'Catalogue Price last updated date': 'catalogue_price_last_updates_date',
        'CIR Tracker': 'cir_tracker',
        'Cluster Name': 'cluster_name',
        'Created By': 'created_by',
        'Created Time': 'created_time',
        'Currency': 'currency',
        'Current Move-In Date': 'current_move_in_date',
        'Current Check-Out Date': 'current_check_out_date',
        'Current Tenant ID': 'current_tenant_id',
        'Electricity Meter Number': 'electricity_meter_number',
        'Email Opt Out': 'email_opt_out',
        'Exchange Rate': 'exchange_rate',
        'Flat Available to Rent Status': 'flat_available_rent_status',
        'Flat Booking Hold Status': 'flat_booking_hold_status',
        'Flat Category': 'flat_category',
        'Flat Facing': 'flat_facing',
        'Flat Master Owner': 'flat_master_owner',
        'Flat Next Booking Status': 'flat_next_booking_status',
        'Flat Occupancy Status': 'flat_occupancy_status',
        'Flat Rent Next Start Date': 'flat_rent_next_start_date'
    }

def handle_duplicate_columns(headers):
    """
    Handle duplicate column names by creating unique identifiers.
    Returns a mapping of column positions to database fields.
    """
    position_mapping = {}
    seen_columns = {}
    mapping = get_csv_to_db_mapping()
    
    logger.info(f"Available mappings: {len(mapping)} columns")
    logger.info(f"Sample mappings: {dict(list(mapping.items())[:5])}")
    
    for i, header in enumerate(headers):
        header = header.strip()  # Remove any whitespace
        
        if header in seen_columns:
            # Handle duplicates
            seen_columns[header] += 1
            
            if header == 'Flats Unique ID':
                # Use the second occurrence for flat_unique_id
                if seen_columns[header] == 1:
                    position_mapping[i] = 'flat_unique_id'
            elif header == 'Last Activity Time':
                # Use the second occurrence for last_activity_time  
                if seen_columns[header] == 1:
                    position_mapping[i] = 'last_activity_time'
            elif header == 'Monthly Rent (Record Currency)':
                # Handle multiple occurrences
                position_mapping[i] = 'monthly_rent_record_currency'
                
        else:
            seen_columns[header] = 0
            # Map first occurrence normally
            if header in mapping:
                position_mapping[i] = mapping[header]
                logger.debug(f"Mapped '{header}' at position {i} to '{mapping[header]}'")
    
    logger.info(f"Final position mapping: {len(position_mapping)} columns mapped")
    return position_mapping

def clean_string_encoding(value):
    """Clean string to handle encoding issues"""
    if value is None:
        return None
    
    try:
        # Convert to string and handle encoding issues
        str_value = str(value)
        # Remove or replace problematic characters
        str_value = str_value.encode('utf-8', errors='replace').decode('utf-8')
        # Remove null bytes and other control characters
        str_value = ''.join(char for char in str_value if ord(char) >= 32 or char in '\t\n\r')
        return str_value.strip()
    except Exception:
        return str(value) if value else None

def clean_currency_value(value):
    """Specifically clean currency values"""
    if value is None or value == '':
        return None
    
    try:
        # Convert to string first
        cleaned = str(value).strip()
        
        # Remove various currency symbols and formatting
        currency_symbols = ['₹', '$', '€', '£', '¥', 'Rs.', 'Rs', 'INR', 'USD', 'EUR', '¢', '₨']
        for symbol in currency_symbols:
            cleaned = cleaned.replace(symbol, '')
        
        # Remove commas, spaces, and other formatting characters
        cleaned = cleaned.replace(',', '').replace(' ', '').replace('\u00a0', '').strip()
        
        # Handle empty or null values
        if cleaned == '' or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-']:
            return None
        
        # Handle negative values in parentheses like (500.00)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Remove any remaining non-numeric characters except decimal point and minus sign
        import re
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        if cleaned == '' or cleaned == '-':
            return None
            
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def clean_data_value(value, field_type='text', field_name=None):
    """Clean and validate data values"""
    if value is None or value == '':
        return None
    
    # First clean encoding issues
    value = clean_string_encoding(value)
    
    # Handle specific field mappings for enumerated values
    if field_name == 'flat_facing':
        # Map direction strings to numeric values based on your logic
        facing_map = {
            'North': 1, 'East': 2, 'West': 3, 'South': 4
        }
        return facing_map.get(str(value).strip(), None)
    
    elif field_name == 'flat_booking_hold_status':
        # Map text values to numeric: free=1, on hold=2
        status_map = {
            'free': 1, 'Free': 1, 'FREE': 1,
            'on hold': 2, 'On Hold': 2, 'ON HOLD': 2, 'hold': 2, 'Hold': 2, 'HOLD': 2
        }
        return status_map.get(str(value).strip(), None)
    
    elif field_name == 'flat_available_rent_status':
        # Map text values to numeric: yes=1, no=0
        available_map = {
            'yes': 1, 'Yes': 1, 'YES': 1, 'y': 1, 'Y': 1,
            'no': 0, 'No': 0, 'NO': 0, 'n': 0, 'N': 0
        }
        return available_map.get(str(value).strip(), None)
    
    elif field_name == 'track_inventory':
        # Map boolean-like values
        bool_map = {'Yes': 1, 'No': 0, 'TRUE': 1, 'FALSE': 0, '1': 1, '0': 0}
        return bool_map.get(str(value).strip(), None)
    
    elif field_name == 'reserved_car_parking_available':
        # Map YES/NO values to numeric: YES=1, NO=0
        parking_map = {
            'YES': 1, 'Yes': 1, 'yes': 1, 'Y': 1, 'y': 1,
            'NO': 0, 'No': 0, 'no': 0, 'N': 0, 'n': 0
        }
        return parking_map.get(str(value).strip(), None)
    
    elif field_name == 'email_opt_out':
        # Map YES/NO values to numeric: YES=1, NO=0
        opt_out_map = {
            'YES': 1, 'Yes': 1, 'yes': 1, 'Y': 1, 'y': 1,
            'NO': 0, 'No': 0, 'no': 0, 'N': 0, 'n': 0
        }
        return opt_out_map.get(str(value).strip(), None)
    
    # Handle string values
    if field_type == 'text':
        return str(value).strip()
    
    # Handle numeric values
    elif field_type in ['numeric', 'integer']:
        # First check if the value looks like text that should not be converted
        str_value = str(value).strip().lower()
        if str_value in ['booked', 'available', 'occupied', 'vacant', 'pending', 'confirmed', 'cancelled']:
            # This looks like status text, return None instead of trying to convert
            logger.warning(f"Field '{field_name}' received text value '{value}' but expected numeric. Returning None.")
            return None
        
        # Use the specialized currency cleaning function
        cleaned_value = clean_currency_value(value)
        if cleaned_value is None:
            return None
        
        try:
            return cleaned_value if field_type == 'numeric' else int(cleaned_value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to {field_type} for field '{field_name}'. Returning None.")
            return None
    
    # Handle dates
    elif field_type == 'date':
        if isinstance(value, str) and value.strip():
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%b %d, %Y']:
                    try:
                        return datetime.strptime(value.strip(), fmt).date()
                    except ValueError:
                        continue
                return None
            except:
                return None
        return None
    
    return value

def process_csv_file(csv_file_path):
    """
    Process CSV file and insert data into flats table
    """
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        return False
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Try different encodings to handle the CSV file
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        file_content = None
        
        for encoding in encodings_to_try:
            try:
                with open(csv_file_path, 'r', encoding=encoding, errors='replace') as file:
                    file_content = file.read()
                logger.info(f"Successfully read CSV file with {encoding} encoding")
                break
            except Exception as e:
                logger.warning(f"Failed to read with {encoding} encoding: {e}")
                continue
        
        if file_content is None:
            logger.error("Could not read CSV file with any encoding")
            return False
        
        # Parse CSV from string content
        from io import StringIO
        csv_file_obj = StringIO(file_content)
        csv_reader = csv.reader(csv_file_obj)
        
        # Skip the first 6 rows (header info) and get actual column headers from row 7
        for i in range(6):
            next(csv_reader)  # Skip rows 1-6
        
        headers = next(csv_reader)  # Get headers from row 7
        
        logger.info(f"Found {len(headers)} columns in CSV")
        logger.info(f"First few headers: {headers[:10]}")  # Show first 10 headers
        
        # Get position mapping for duplicates
        position_mapping = handle_duplicate_columns(headers)
        
        # Prepare database columns that actually exist in the flats table schema
        db_columns = [
                'name', 'slug', 'flat_number', 'flat_type', 'selling_price', 'description',
                'built_up_area', 'super_built_area', 'floor_number', 'no_of_bathrooms',
                'max_occupancy', 'balcony_type', 'flat_facing', 'videos',
                'meta_title', 'meta_description', 'landlord_name',
                'landlord_mailing_street', 'landlord_mailing_city', 'landlord_mailing_state',
                'landlord_mailing_zip', 'landlord_mailing_country',
                'flat_mailing_street', 'flat_mailing_city', 'flat_mailing_state',
                'flat_mailing_zip', 'flat_mailing_country', 'maintenance_amount',
                'garbage_amount', 'move_out_charges', 'agreement_charges',
                'flat_security_deposit', 'terms_conditions', 'inside_the_flat_description',
                'renewal_rate', 'added_date', 'modified_date',
                'product_tags', 'track_inventory', 'flat_unique_id',
                'website_flat_url', 'wifi_id', 'wifi_password', 'flat_occupancy_status',
                # Adding all the mapped columns from CSV
                'agreement_charges_record_charges', 'available_date_for_next_booking',
                'block_name', 'booking_2_contarct_days', 'care_taker_master',
                'catalogue_price_last_updates_date', 'cir_tracker', 'cluster_name',
                'created_by', 'created_time', 'currency', 'current_move_in_date',
                'current_check_out_date', 'current_tenant_id', 'electricity_meter_number',
                'email_opt_out', 'exchange_rate', 'flat_booking_hold_status',
                'flat_available_rent_status', 'flat_available_status', 'flat_category',
                'flat_master_owner', 'flat_next_booking_status', 'flat_rent_next_start_date',
                'flat_security_deposit_record_currency', 'flat_video', 'garbage_amount_record_currency',
                'update_status', 'unsubsribed_time', 'sample_contract_link',
                'reserved_car_parking_available', 'parking_queue', 'next_move_in_date',
                'next_booking_id', 'modified_by', 'validatortag', 'record_id',
                'property_unique_id', 'property_master'
        ]
        
        # Filter only columns that exist in position mapping, plus special generated columns
        available_columns = [col for col in db_columns if col in position_mapping.values()]
        
        # Add special columns that are generated (not directly mapped from CSV)
        if 'name' in [col for col in db_columns if col in position_mapping.values()]:
            if 'slug' not in available_columns:
                available_columns.append('slug')
        
        if 'flat_available_rent_status' in [col for col in db_columns if col in position_mapping.values()]:
            if 'flat_available_status' not in available_columns:
                available_columns.append('flat_available_status')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_available_columns = []
        for col in available_columns:
            if col not in seen:
                unique_available_columns.append(col)
                seen.add(col)
        available_columns = unique_available_columns
        
        logger.info(f"Position mapping has {len(position_mapping)} entries")
        logger.info(f"Mapped {len(available_columns)} columns to database")
        
        # Debug: Show some mappings
        if len(position_mapping) > 0:
            logger.info(f"Sample position mappings: {dict(list(position_mapping.items())[:5])}")
        
        if len(available_columns) == 0:
            logger.error("No columns were mapped! Check column name matching.")
            return False
        
        # Prepare INSERT query (no ON CONFLICT since flat_number has no unique constraint)
        placeholders = ', '.join(['%s'] * len(available_columns))
        
        query = f"""
            INSERT INTO flats ({', '.join(available_columns)}) 
            VALUES ({placeholders})
        """
        
        logger.info(f"Insert query: {query}")
        
        # Process each row
        rows_processed = 0
        rows_failed = 0
        
        for row_num, row in enumerate(csv_reader, start=8):  # Start at 8 because headers are on row 7, data starts row 8
            try:
                # First pass: collect source values for special columns
                name_value = None
                rent_status_value = None
                
                # Pre-collect name and rent status values
                for pos, mapped_col in position_mapping.items():
                    if mapped_col == 'name' and pos < len(row):
                        name_raw = row[pos]
                        name_value = clean_data_value(name_raw, 'text', 'name')
                    elif mapped_col == 'flat_available_rent_status' and pos < len(row):
                        rent_raw = row[pos]
                        rent_status_value = clean_data_value(rent_raw, 'enum', 'flat_available_rent_status')
                
                # Debug logging for first few rows
                if rows_processed < 3:
                    logger.info(f"Row {row_num}: name_value='{name_value}', rent_status_value='{rent_status_value}'")
                
                # Build values list based on column mapping
                values = []
                for col in available_columns:
                    # Handle special generated columns
                    if col == 'slug':
                        # Generate slug from name (lowercase)
                        cleaned_value = name_value.lower().strip() if name_value else None
                        values.append(cleaned_value)
                        continue
                    elif col == 'flat_available_status':
                        # Duplicate flat_available_rent_status value
                        cleaned_value = rent_status_value
                        values.append(cleaned_value)
                        continue
                    
                    # Find the position of this column in the CSV
                    csv_position = None
                    for pos, mapped_col in position_mapping.items():
                        if mapped_col == col:
                            csv_position = pos
                            break
                    
                    if csv_position is not None and csv_position < len(row):
                        raw_value = row[csv_position]
                        
                        # Apply data type specific cleaning
                        if col in ['agreement_charges', 'selling_price', 'maintenance_amount', 
                                 'garbage_amount', 'flat_security_deposit', 'move_out_charges',
                                 'agreement_charges_record_charges', 'flat_security_deposit_record_currency',
                                 'garbage_amount_record_currency', 'renewal_rate', 'exchange_rate']:
                            # Debug currency cleaning for first few rows
                            if rows_processed < 3 and raw_value and '₹' in str(raw_value):
                                logger.info(f"Currency cleaning - Column: {col}, Original: '{raw_value}' -> Cleaned: '{clean_currency_value(raw_value)}'")
                            cleaned_value = clean_data_value(raw_value, 'numeric', col)
                        elif col in ['added_date', 'modified_date', 'current_move_in_date',
                                   'current_check_out_date', 'catalogue_price_last_updates_date',
                                   'available_date_for_next_booking', 'created_time', 'flat_rent_next_start_date',
                                   'next_move_in_date', 'unsubsribed_time']:
                            cleaned_value = clean_data_value(raw_value, 'date', col)
                        elif col in ['floor_number', 'no_of_bathrooms', 'booking_2_contarct_days']:
                            cleaned_value = clean_data_value(raw_value, 'integer', col)
                        elif col in ['flat_facing', 'flat_booking_hold_status', 'flat_available_rent_status',
                                   'track_inventory', 'email_opt_out', 'reserved_car_parking_available']:
                            # Debug parking field
                            if col == 'reserved_car_parking_available' and rows_processed < 5:
                                logger.info(f"Processing {col}: raw_value='{raw_value}' -> cleaned='{clean_data_value(raw_value, 'enum', col)}'")
                            cleaned_value = clean_data_value(raw_value, 'enum', col)
                        elif col in ['created_by', 'currency', 'flat_category', 'flat_master_owner',
                                   'validatortag', 'record_id', 'property_unique_id', 'max_occupancy',
                                   'block_name', 'cluster_name', 'care_taker_master', 'cir_tracker',
                                   'electricity_meter_number', 'flat_next_booking_status', 'flat_video',
                                   'update_status', 'sample_contract_link', 'parking_queue', 'modified_by',
                                   'property_master', 'current_tenant_id', 'next_booking_id']:
                            cleaned_value = clean_data_value(raw_value, 'text', col)
                        else:
                            cleaned_value = clean_data_value(raw_value, 'text', col)
                        
                        values.append(cleaned_value)
                    else:
                        values.append(None)
                
                # Debug: Log values for problematic rows
                if rows_processed < 3 or rows_failed > 0:
                    logger.info(f"Row {row_num} values (first 5): {values[:5]}")
                
                # Debug: Check for potential problematic values before insert
                for i, val in enumerate(values):
                    if isinstance(val, str) and val.lower() in ['booked', 'available', 'occupied']:
                        logger.warning(f"Row {row_num}: Found status text '{val}' in column {available_columns[i]} at position {i}")
                
                # Debug: Check reserved_car_parking_available specifically for first few rows
                if rows_processed < 3:
                    for i, col in enumerate(available_columns):
                        if col == 'reserved_car_parking_available':
                            logger.info(f"Row {row_num}: reserved_car_parking_available at position {i} = '{values[i]}'")
                
                # Simply insert the record
                try:
                    cursor.execute(query, values)
                    conn.commit()
                    rows_processed += 1
                    
                    if rows_processed % 100 == 0:
                        logger.info(f"Processed {rows_processed} rows...")
                except Exception as db_error:
                    conn.rollback()  # Rollback the failed transaction
                    logger.error(f"Database error on row {row_num}: {db_error}")
                    logger.error(f"Query: {query}")
                    logger.error(f"Values: {values}")
                    raise  # Re-raise to see the full stack trace
                    
            except Exception as e:
                logger.error(f"Error processing row {row_num}: {e}")
                logger.error(f"Row data: {row[:5]}...")  # Show first 5 columns for debugging
                rows_failed += 1
                continue
        
        # Individual transactions are already committed
        
        logger.info(f"Successfully processed {rows_processed} rows")
        logger.info(f"Failed rows: {rows_failed}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the CSV import"""
    if len(sys.argv) != 2:
        print("Usage: python csv_to_flats_insert.py <csv_file_path>")
        print("Example: python csv_to_flats_insert.py data.csv")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    logger.info(f"Starting CSV import from: {csv_file_path}")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    success = process_csv_file(csv_file_path)
    
    if success:
        logger.info("CSV import completed successfully!")
        sys.exit(0)
    else:
        logger.error("CSV import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
