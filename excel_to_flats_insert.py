#!/usr/bin/env python3
"""
Excel to Flats Table Insertion Script
Simple script to insert data from Excel file into PostgreSQL flats table.
No update/delete/truncate logic - only inserts.
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_db():
    """Create database connection"""
    try:
        return psycopg2.connect(
            # dbname="kots_local_sep_10",  # Your database name
            # user="postgres",             # Your PostgreSQL username
            # password="lenovoN@100",      # Your PostgreSQL password
            # host="localhost",
            # port=5432
            dbname="kots_prod",  # Your database name
            user="postgres",             # Your PostgreSQL username
            password=")rD*4PW(lrm-)F-F6Z0XWcd~a9_B",      # Your PostgreSQL password
            host="kots-db-cluster.cluster-ch8uu0w02w3b.ap-south-1.rds.amazonaws.com",
            port=5432
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_excel_to_db_mapping():
    """
    Returns mapping between Excel column names and database column names.
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
        'Flat Iframe Embed for Virtual Tour': 'videos',
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
        'Flats Unique ID': 'flat_unique_id',
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
        'Last Activity Time': 'last_activity_time',
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
    }

def clean_currency_value(value):
    """Clean currency values and convert to numeric"""
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        # Convert to string first
        cleaned = str(value).strip()
        
        # Remove currency symbols and formatting
        currency_symbols = ['₹', '$', '€', '£', '¥', 'Rs.', 'Rs', 'INR', 'USD', 'EUR', '¢', '₨']
        for symbol in currency_symbols:
            cleaned = cleaned.replace(symbol, '')
        
        # Remove commas, spaces, and other formatting
        cleaned = cleaned.replace(',', '').replace(' ', '').replace('\u00a0', '').strip()
        
        # Handle empty or null values
        if cleaned == '' or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-']:
            return None
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Remove non-numeric characters except decimal point and minus
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        if cleaned == '' or cleaned == '-':
            return None
            
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def clean_data_value(value, field_name=None):
    """Clean and validate data values based on field type"""
    if pd.isna(value) or value == '' or value is None:
        return None
    
    # Handle specific field mappings
    if field_name == 'flat_facing':
        facing_map = {
            'North': 1, 'East': 2, 'West': 3, 'South': 4, 'North East' : 5, 'North West' : 6, 'South East' : 7, 'South West' : 8,
            'north': 1, 'east': 2, 'west': 3, 'south': 4, 'North East' : 5, 'North West' : 6, 'South East' : 7, 'South West' : 8,
            'NORTH': 1, 'EAST': 2, 'WEST': 3, 'SOUTH': 4 , 'NORTH EAST' : 5, 'NORTH WEST' : 6, 'SOUTH EAST' : 7, 'SOUTH WEST' : 8
        }
        return facing_map.get(str(value).strip(), None)
    
    elif field_name == 'flat_booking_hold_status':
        status_map = {
            'free': 1, 'Free': 1, 'FREE': 1,
            'on hold': 2, 'On Hold': 2, 'ON HOLD': 2, 'hold': 2, 'Hold': 2, 'HOLD': 2
        }
        return status_map.get(str(value).strip(), None)
    
    elif field_name == 'flat_available_rent_status':
        available_map = {
            'yes': 1, 'Yes': 1, 'YES': 1, 'y': 1, 'Y': 1,
            'no': 0, 'No': 0, 'NO': 0, 'n': 0, 'N': 0
        }
        return available_map.get(str(value).strip(), None)
    
    elif field_name == 'track_inventory':
        bool_map = {'Yes': 1, 'No': 0, 'TRUE': 1, 'FALSE': 0, '1': 1, '0': 0}
        return bool_map.get(str(value).strip(), None)
    
    elif field_name == 'reserved_car_parking_available':
        # Return as VARCHAR(3) - 'YES' or 'NO'
        parking_map = {
            'YES': 'YES', 'Yes': 'YES', 'yes': 'YES', 'Y': 'YES', 'y': 'YES',
            'NO': 'NO', 'No': 'NO', 'no': 'NO', 'N': 'NO', 'n': 'NO'
        }
        return parking_map.get(str(value).strip(), 'NO')
    
    elif field_name == 'email_opt_out':
        opt_out_map = {
            'YES': True, 'Yes': True, 'yes': True, 'Y': True, 'y': True, 'TRUE': True, 'True': True, 'true': True,
            'NO': False, 'No': False, 'no': False, 'N': False, 'n': False, 'FALSE': False, 'False': False, 'false': False
        }
        return opt_out_map.get(str(value).strip(), False)
    
    elif field_name == 'parking_queue':
        parking_map = {
            'YES': True, 'Yes': True, 'yes': True, 'Y': True, 'y': True, 'TRUE': True, 'True': True, 'true': True,
            'NO': False, 'No': False, 'no': False, 'N': False, 'n': False, 'FALSE': False, 'False': False, 'false': False
        }
        return parking_map.get(str(value).strip(), False)
    
    elif field_name == 'booking_lock_status':
        # Always return 'available' as per your requirement
        return 'available'
    
    # Handle currency fields
    elif field_name in ['agreement_charges', 'selling_price', 'maintenance_amount', 
                       'garbage_amount', 'flat_security_deposit', 'move_out_charges',
                       'agreement_charges_record_charges', 'flat_security_deposit_record_currency',
                       'garbage_amount_record_currency', 'renewal_rate', 'exchange_rate']:
        return clean_currency_value(value)
    
    # Handle date fields
    elif field_name in ['added_date', 'modified_date', 'current_move_in_date',
                       'current_check_out_date', 'catalogue_price_last_updates_date',
                       'available_date_for_next_booking', 'created_time', 'flat_rent_next_start_date',
                       'next_move_in_date', 'unsubsribed_time', 'last_activity_time']:
        if pd.isna(value):
            return None
        try:
            # Handle pandas datetime
            if hasattr(value, 'strftime'):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            # Handle string dates
            elif isinstance(value, str):
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%b %d, %Y']:
                    try:
                        return datetime.strptime(value.strip(), fmt).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue
            return None
        except:
            return None
    
    # Handle integer fields
    elif field_name in ['floor_number', 'no_of_bathrooms', 'booking_2_contarct_days', 'current_tenant_id']:
        try:
            return int(float(value)) if not pd.isna(value) else None
        except (ValueError, TypeError):
            return None
    
    # Default: return as string
    return str(value).strip() if not pd.isna(value) else None

def process_excel_file(excel_file_path):
    """Process Excel file and insert data into flats table"""
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        return False
    
    try:
        # Read Excel file
        logger.info(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path, skiprows=6)  # Skip first 6 rows like in your CSV script
        
        logger.info(f"Found {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)[:10]}")  # Show first 10 columns
        
        # Get column mapping
        column_mapping = get_excel_to_db_mapping()
        
        # Connect to database
        conn = connect_db()
        cursor = conn.cursor()
        
        # Prepare mapped columns
        mapped_columns = []
        for excel_col in df.columns:
            if excel_col in column_mapping:
                mapped_columns.append(column_mapping[excel_col])
        
        # Add generated columns
        if 'name' in mapped_columns:
            mapped_columns.append('slug')
        if 'flat_available_rent_status' in mapped_columns:
            mapped_columns.append('flat_available_status')
        
        # Add booking_lock_status if not present
        if 'booking_lock_status' not in mapped_columns:
            mapped_columns.append('booking_lock_status')
        
        # Remove duplicates while preserving order
        unique_columns = []
        seen = set()
        for col in mapped_columns:
            if col not in seen:
                unique_columns.append(col)
                seen.add(col)
        mapped_columns = unique_columns
        
        logger.info(f"Mapped {len(mapped_columns)} columns to database")
        logger.info(f"Mapped columns: {mapped_columns}")
        
        # Prepare INSERT query
        placeholders = ', '.join(['%s'] * len(mapped_columns))
        query = f"""
            INSERT INTO flats ({', '.join(mapped_columns)}) 
            VALUES ({placeholders})
        """
        
        logger.info(f"Insert query prepared for {len(mapped_columns)} columns")
        
        # Process each row
        rows_processed = 0
        rows_failed = 0
        
        for index, row in df.iterrows():
            try:
                values = []
                name_value = None
                rent_status_value = None
                
                # First pass: get name and rent status for generated columns
                for excel_col in df.columns:
                    if excel_col in column_mapping:
                        db_col = column_mapping[excel_col]
                        if db_col == 'name':
                            name_value = clean_data_value(row[excel_col], 'name')
                        elif db_col == 'flat_available_rent_status':
                            rent_status_value = clean_data_value(row[excel_col], 'flat_available_rent_status')
                
                # Build values for each mapped column
                for db_col in mapped_columns:
                    if db_col == 'slug':
                        # Generate slug from name
                        slug_value = name_value.lower().strip() if name_value else None
                        values.append(slug_value)
                    elif db_col == 'flat_available_status':
                        # Copy from flat_available_rent_status
                        values.append(rent_status_value)
                    elif db_col == 'booking_lock_status':
                        # Always set to 'available'
                        values.append('available')
                    else:
                        # Find corresponding Excel column
                        excel_col = None
                        for exc_col, db_mapped in column_mapping.items():
                            if db_mapped == db_col:
                                excel_col = exc_col
                                break
                        
                        if excel_col and excel_col in df.columns:
                            raw_value = row[excel_col]
                            cleaned_value = clean_data_value(raw_value, db_col)
                            values.append(cleaned_value)
                        else:
                            values.append(None)
                
                # Execute insert
                cursor.execute(query, values)
                conn.commit()
                rows_processed += 1
                
                if rows_processed % 50 == 0:
                    logger.info(f"Processed {rows_processed} rows...")
                    
            except Exception as e:
                conn.rollback()
                logger.error(f"Error processing row {index + 1}: {e}")
                logger.error(f"Row data sample: {dict(row.head())}")
                rows_failed += 1
                continue
        
        logger.info(f"Successfully processed {rows_processed} rows")
        logger.info(f"Failed rows: {rows_failed}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the Excel import"""
    if len(sys.argv) != 2:
        print("Usage: python excel_to_flats_insert.py <excel_file_path>")
        print("Example: python excel_to_flats_insert.py flat_data_for_k27_k23.xlsx")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    
    logger.info(f"Starting Excel import from: {excel_file_path}")
    
    success = process_excel_file(excel_file_path)
    
    if success:
        logger.info("Excel import completed successfully!")
        sys.exit(0)
    else:
        logger.error("Excel import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
