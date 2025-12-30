import csv
import json
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

def fix_json_format(value):
    """Fix malformed JSON strings like {savedName: file.webp} to proper JSON"""
    if not value or value.strip() == '':
        return None
    
    # If it's already valid JSON, return as is
    try:
        json.loads(value)
        return value
    except:
        pass
    
    # Fix common JSON formatting issues
    if '{' in value and '}' in value:
        # Add quotes around property names that don't have them
        fixed = re.sub(r'(\w+):\s*([^",}]+)', r'"\1": "\2"', value)
        # Handle already quoted values
        fixed = re.sub(r'(\w+):\s*"([^"]*)"', r'"\1": "\2"', fixed)
        
        try:
            # Validate the fixed JSON
            json.loads(fixed)
            return fixed
        except:
            # If still invalid, return as string
            return json.dumps(value)
    
    return json.dumps(value) if value else None

def convert_value(value, column_name, data_type):
    """Convert CSV string values to appropriate Python types"""
    if value is None or value.strip() == '':
        return None
    
    value = value.strip()
    
    # Handle specific enum columns
    if column_name == 'booking_lock_status':
        # Always return 'available' regardless of CSV value
        return 'available'
    
    # Handle columns with length restrictions
    if column_name == 'reserved_car_parking_available':
        # This field is VARCHAR(3), so truncate or use default
        if value and value.strip().upper() in ['YES', 'Y', 'TRUE', '1']:
            return 'YES'
        else:
            return 'NO'  # Default value
    
    # Handle JSON/JSONB columns
    if 'json' in data_type.lower():
        return fix_json_format(value)
    
    # Handle boolean columns
    if data_type.lower() == 'boolean':
        return value.lower() in ('true', 't', '1', 'yes', 'y')
    
    # Handle numeric types
    if 'numeric' in data_type.lower() or 'decimal' in data_type.lower():
        try:
            return float(value) if '.' in value else int(value)
        except:
            return None
    
    # Handle integer types
    if any(int_type in data_type.lower() for int_type in ['integer', 'bigint', 'smallint']):
        try:
            return int(float(value))  # Handle cases like "1.0"
        except:
            return None
    
    # Handle date/timestamp columns
    if 'date' in data_type.lower() or 'timestamp' in data_type.lower():
        if value.lower() in ['null', '']:
            return None
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(value, fmt)
                except:
                    continue
            return value  # Return as string if can't parse
        except:
            return None
    
    # Handle general varchar length limits
    if 'varchar' in data_type.lower() or 'character varying' in data_type.lower():
        # Truncate very long strings to prevent errors
        if len(value) > 255:  # General safety limit
            value = value[:255]
    
    # Default: return as string
    return value

def get_column_info():
    """Define column data types for temp_flats table"""
    return {
        'id': 'bigint',
        'seller_id': 'bigint',
        'product_type_id': 'bigint',
        'flat_type': 'varchar',
        'flat_number': 'varchar',
        'name': 'varchar',
        'slug': 'varchar',
        'code': 'varchar',
        'route_id': 'bigint',
        'description': 'text',
        'featured_image': 'jsonb',
        'images': 'jsonb',
        'videos': 'text',
        'youtube_link': 'jsonb',
        'product_tags': 'text',
        'category': 'varchar',
        'price_with_tax': 'numeric',
        'price_setting': 'smallint',
        'selling_price': 'numeric',
        'original_price': 'numeric',
        'discount': 'numeric',
        'sku': 'varchar',
        'zoho_unique_id': 'varchar',
        'zoho_record_id': 'varchar',
        'barcode': 'varchar',
        'quantity': 'integer',
        'track_inventory': 'smallint',
        'allow_purchase': 'smallint',
        'low_stock_notification': 'smallint',
        'quantity_per_user': 'integer',
        'weight': 'numeric',
        'weight_type': 'smallint',
        'dim_length': 'numeric',
        'dim_width': 'numeric',
        'dim_height': 'numeric',
        'dim_type': 'smallint',
        'brand': 'bigint',
        'publish_now': 'smallint',
        'publish_date': 'timestamp',
        'meta_title': 'varchar',
        'meta_keywords': 'text',
        'meta_description': 'text',
        'meta_url': 'varchar',
        'meta_image': 'varchar',
        'status': 'smallint',
        'digital': 'smallint',
        'shipping': 'smallint',
        'selected_packaging': 'bigint',
        'tax': 'smallint',
        'gst_id': 'bigint',
        'tax_type': 'smallint',
        'goods_or_service': 'smallint',
        'hsn_sac_code': 'varchar',
        'tax_rate': 'numeric',
        'price_included_tax': 'smallint',
        'informations_for_custom_app': 'text',
        'gift_wrap_id': 'bigint',
        'gift_wrap_details': 'text',
        'gift_wrap_settings': 'smallint',
        'gift_wrap_allowed': 'smallint',
        'gift_wrap_price': 'numeric',
        'gift_wrap_price_included_tax': 'smallint',
        'gift_wrap_gst_type': 'smallint',
        'gift_wrap_hsn_sac_code': 'varchar',
        'gift_wrap_gst_id': 'bigint',
        'size_chart': 'text',
        'archived': 'smallint',
        'advance_booking_amount': 'numeric',
        'minimum_deposit': 'numeric',
        'flat_available_status': 'smallint',
        'available_date_for_next_booking': 'date',
        'flat_next_booking_status': 'varchar',
        'flat_available_rent_status': 'smallint',
        'flat_booking_hold_status': 'smallint',
        'buffer_days_for_booking': 'integer',
        'type': 'smallint',
        'floor_number': 'integer',
        'no_of_balconies': 'integer',
        'no_of_bathrooms': 'integer',
        'flat_facing': 'smallint',
        'added_date': 'timestamp',
        'modified_date': 'timestamp',
        'added_by': 'bigint',
        'modified_by': 'varchar',
        'added_by_name': 'varchar',
        'modified_by_name': 'varchar',
        'added_ip': 'varchar',
        'modified_ip': 'varchar',
        'sort_order': 'integer',
        'total_views': 'integer',
        'maintenance_included': 'smallint',
        'maintenance_amount': 'numeric',
        'garbage_included': 'smallint',
        'garbage_amount': 'numeric',
        'car_parking_allowed': 'smallint',
        'car_parking_included': 'smallint',
        'car_parking_amount': 'numeric',
        'move_out_included': 'smallint',
        'move_out_charges': 'numeric',
        'agreement_charges': 'numeric',
        'terms_conditions': 'text',
        'built_up_area': 'varchar',
        'super_built_area': 'varchar',
        'max_occupancy': 'varchar',
        'furnishing_type': 'smallint',
        'inside_the_flat_description': 'text',
        'landlord_name': 'varchar',
        'landlord_mailing_street': 'text',
        'landlord_mailing_city': 'varchar',
        'landlord_mailing_state': 'varchar',
        'landlord_mailing_zip': 'varchar',
        'landlord_mailing_country': 'varchar',
        'flat_mailing_street': 'text',
        'flat_mailing_city': 'varchar',
        'flat_mailing_state': 'varchar',
        'flat_mailing_zip': 'varchar',
        'flat_mailing_country': 'varchar',
        'renewal_rate': 'varchar',
        'webp_conversion': 'smallint',
        'balcony_id': 'bigint',
        'balcony_type': 'varchar',
        'total_available_parking_slots': 'integer',
        'map_description': 'text',
        'category_slug': 'varchar',
        'user_friendly_url': 'varchar',
        'property_id': 'integer',
        'gift_wrap_hsnsac_code': 'varchar',
        'block_name': 'varchar',
        'booking_2_contarct_days': 'integer',
        'care_taker_master': 'varchar',
        'catalogue_price_last_updates_date': 'date',
        'cir_tracker': 'varchar',
        'cluster_name': 'varchar',
        'created_by': 'varchar',
        'created_time': 'timestamp',
        'currency': 'varchar',
        'current_move_in_date': 'date',
        'current_check_out_date': 'date',
        'current_tenant_id': 'integer',
        'electricity_meter_number': 'varchar',
        'email_opt_out': 'boolean',
        'exchange_rate': 'integer',
        'flat_category': 'varchar',
        'flat_master_owner': 'varchar',
        'flat_rent_next_start_date': 'varchar',
        'flat_security_deposit': 'bigint',
        'agreement_charges_record_charges': 'bigint',
        'flat_security_deposit_record_currency': 'bigint',
        'flat_video': 'varchar',
        'flat_unique_id': 'varchar',
        'garbage_amount_record_currency': 'integer',
        'last_activity_time': 'timestamp',
        'website_flat_url': 'varchar',
        'validatortag': 'varchar',
        'update_status': 'varchar',
        'unsubsribed_time': 'timestamp',
        'unsubsribed_mode': 'varchar',
        'sample_contract_link': 'varchar',
        'reserved_car_parking_available': 'varchar',
        'record_id': 'varchar',
        'property_unique_id': 'varchar',
        'property_master': 'varchar',
        'parking_queue': 'boolean',
        'next_move_in_date': 'timestamp',
        'next_booking_id': 'varchar',
        'wifi_id': 'varchar',
        'wifi_password': 'varchar',
        'flat_occupancy_status': 'varchar',
        'booking_lock_status': 'varchar',
        'current_lock_id': 'varchar'
    }

def insert_csv_to_temp_flats(csv_file_path, db_config):
    """
    Read CSV file and insert data into temp_flats table
    
    Args:
        csv_file_path (str): Path to the CSV file
        db_config (dict): Database connection configuration
    """
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return False
    
    column_types = get_column_info()
    
    try:
        # Connect to PostgreSQL
        print("Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clear existing data in temp_flats (optional)
        print("Clearing existing data in temp_flats...")
        cur.execute("TRUNCATE TABLE public.temp_flats RESTART IDENTITY;")
        
        # Read CSV file
        print(f"Reading CSV file: {csv_file_path}")
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Get column names from CSV
            csv_columns = csv_reader.fieldnames
            print(f"Found {len(csv_columns)} columns in CSV")
            
            # Prepare INSERT statement
            valid_columns = [col for col in csv_columns if col in column_types]
            print(f"Valid columns for insertion: {len(valid_columns)}")
            
            placeholders = ', '.join(['%s'] * len(valid_columns))
            columns_str = ', '.join(valid_columns)
            
            insert_query = f"""
                INSERT INTO public.temp_flats ({columns_str}) 
                VALUES ({placeholders})
            """
            
            # Process and insert rows
            successful_inserts = 0
            failed_inserts = 0
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (accounting for header)
                try:
                    # Convert values according to their data types
                    values = []
                    for col in valid_columns:
                        raw_value = row.get(col, '')
                        converted_value = convert_value(raw_value, col, column_types[col])
                        values.append(converted_value)
                    
                    # Execute insert
                    cur.execute(insert_query, values)
                    successful_inserts += 1
                    
                    if successful_inserts % 100 == 0:
                        print(f"Inserted {successful_inserts} rows...")
                        
                except Exception as e:
                    failed_inserts += 1
                    print(f"Error inserting row {row_num}: {str(e)}")
                    if failed_inserts <= 5:  # Show first 5 errors
                        print(f"Problematic row data: {dict(row)}")
                    
                    # Continue with next row instead of failing completely
                    continue
            
            # Commit the transaction
            conn.commit()
            
            print(f"\n=== Import Summary ===")
            print(f"Total rows processed: {successful_inserts + failed_inserts}")
            print(f"Successful inserts: {successful_inserts}")
            print(f"Failed inserts: {failed_inserts}")
            print(f"Success rate: {(successful_inserts/(successful_inserts + failed_inserts))*100:.2f}%")
            
            return True
            
    except Exception as e:
        print(f"Database error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the CSV import"""
    
    # Database configuration - UPDATE THESE VALUES
    db_config = {
        'host': 'localhost',
        'database': 'kots_local_sep_10',  # Your database name
        'user': 'postgres',               # Your PostgreSQL username
        'password': 'lenovoN@100',      # Your PostgreSQL password
        'port': 5432
    }
    
    # CSV file path - UPDATE THIS PATH
    csv_file_path = 'some_flats.csv'  # Path to your CSV file
    
    print("=== CSV to temp_flats Import Script ===")
    print(f"CSV File: {csv_file_path}")
    print(f"Database: {db_config['database']}")
    print(f"Host: {db_config['host']}")
    
    # Confirm before proceeding
    confirm = input("\nProceed with import? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Import cancelled.")
        return
    
    # Run the import
    success = insert_csv_to_temp_flats(csv_file_path, db_config)
    
    if success:
        print("\n✅ Import completed successfully!")
        print("You can now query the temp_flats table to verify the data.")
    else:
        print("\n❌ Import failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
