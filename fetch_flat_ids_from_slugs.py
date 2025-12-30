#!/usr/bin/env python3
"""
Import Tenant Data Script
Reads Active_and_Old_Tenant.xlsx file and imports tenant data into flat_booking_orders and kyc_details tables
Matches flat_slug from Excel to name column in flats table and inserts complete tenant records
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv
import logging
import re

# Configure logging first
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flat_ids_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Warning: Could not load .env file: {e}")
    logger.info("Continuing with system environment variables...")

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
        return None

def clean_flat_slug(flat_slug):
    """Clean and normalize flat slug for matching"""
    if pd.isna(flat_slug) or flat_slug is None:
        return None
    
    try:
        cleaned = str(flat_slug).strip()
        if not cleaned or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        return cleaned
    except Exception:
        return None

def clean_string_value(value):
    """Clean and normalize string values"""
    if pd.isna(value) or value is None:
        return None
    
    try:
        cleaned = str(value).strip()
        if not cleaned or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        return cleaned
    except Exception:
        return None

def clean_phone_number(phone):
    """Clean phone number by removing country code 91"""
    if pd.isna(phone) or phone is None:
        return None
    
    try:
        phone_str = str(phone).strip()
        # Remove any non-digit characters except +
        phone_clean = re.sub(r'[^\d+]', '', phone_str)
        
        # Remove +91 or 91 prefix
        if phone_clean.startswith('+91'):
            phone_clean = phone_clean[3:]
        elif phone_clean.startswith('91') and len(phone_clean) > 10:
            phone_clean = phone_clean[2:]
        
        # Validate phone number length (should be 10 digits for Indian numbers)
        if len(phone_clean) == 10 and phone_clean.isdigit():
            return phone_clean
        
        return None
    except Exception:
        return None

def parse_date_value(date_value):
    """Parse date from various formats to YYYY-MM-DD HH:MM:SS format"""
    if pd.isna(date_value) or date_value is None:
        return None
    
    try:
        # If it's already a datetime object
        if isinstance(date_value, (datetime, date)):
            return date_value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date_value, datetime) else f"{date_value.strftime('%Y-%m-%d')} 00:00:00"
        
        date_str = str(date_value).strip()
        if not date_str or date_str.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        
        # Try different date formats
        date_formats = [
            '%m/%d/%Y',      # 9/16/2025
            '%d/%m/%Y',      # 16/9/2025
            '%d-%b-%Y',      # 9-Sep-2025
            '%d-%B-%Y',      # 9-September-2025
            '%Y-%m-%d',      # 2025-09-16
            '%m-%d-%Y',      # 09-16-2025
            '%d/%b/%Y',      # 16/Sep/2025
            '%d/%B/%Y',      # 16/September/2025
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing date '{date_value}': {e}")
        return None

def parse_date_only(date_value):
    """Parse date from various formats to YYYY-MM-DD format"""
    if pd.isna(date_value) or date_value is None:
        return None
    
    try:
        # If it's already a datetime object
        if isinstance(date_value, (datetime, date)):
            return date_value.strftime('%Y-%m-%d')
        
        date_str = str(date_value).strip()
        if not date_str or date_str.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        
        # Try different date formats
        date_formats = [
            '%m/%d/%Y',      # 9/16/2025
            '%d/%m/%Y',      # 16/9/2025
            '%d-%b-%Y',      # 9-Sep-2025
            '%d-%B-%Y',      # 9-September-2025
            '%Y-%m-%d',      # 2025-09-16
            '%m-%d-%Y',      # 09-16-2025
            '%d/%b/%Y',      # 16/Sep/2025
            '%d/%B/%Y',      # 16/September/2025
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing date '{date_value}': {e}")
        return None

def clean_numeric_value(value):
    """Clean numeric values"""
    if pd.isna(value) or value is None:
        return None
    
    try:
        # If it's already a number
        if isinstance(value, (int, float)):
            return value
        
        # Clean string representation
        cleaned = str(value).strip()
        if not cleaned or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹$,\s]', '', cleaned)
        
        return float(cleaned) if '.' in cleaned else int(cleaned)
    except Exception:
        return None

def clean_boolean_value(value):
    """Clean boolean values - Yes=1, No=0"""
    if pd.isna(value) or value is None:
        return 0
    
    try:
        cleaned = str(value).strip().lower()
        if cleaned in ['yes', 'y', '1', 'true', 'confirmed']:
            return 1
        else:
            return 0
    except Exception:
        return 0

def read_excel_file(excel_file_path, sheet_name="Active Tenant"):
    """
    Read Excel file and return tenant data
    Returns list of tenant records with all required fields
    """
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        return []
    
    try:
        # Try reading with different engines and parameters
        df = None
        
        # Try openpyxl engine first
        try:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
            logger.info(f"Successfully read Excel file sheet '{sheet_name}' with openpyxl engine")
        except Exception as e:
            logger.warning(f"Failed to read with openpyxl: {e}")
            
            # Try xlrd engine as fallback
            try:
                df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='xlrd')
                logger.info(f"Successfully read Excel file sheet '{sheet_name}' with xlrd engine")
            except Exception as e2:
                logger.error(f"Failed to read with xlrd: {e2}")
                return []
        
        if df is None or df.empty:
            logger.error("Excel file is empty or could not be read")
            return []
        
        logger.info(f"Excel file contains {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Column names: {list(df.columns)}")
        
        # Extract tenant records
        tenant_records = []
        processed_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract flat_slug (required field)
                flat_slug = clean_flat_slug(row.get('flat_slug'))
                
                if flat_slug is None:
                    skipped_count += 1
                    logger.debug(f"Row {index + 1}: Skipping - empty flat_slug")
                    continue
                
                # Extract all required fields for flat_booking_orders
                tenant_record = {
                    'row_number': index + 1,
                    'flat_slug': flat_slug,
                    
                    # flat_booking_orders fields
                    'booking_reference_id': clean_string_value(row.get('booking_reference_id')),
                    'contract_start_date': parse_date_value(row.get('contract_start_date')),
                    'contract_end_date': parse_date_value(row.get('contract_end_date')),
                    'lock_in_period': clean_numeric_value(row.get('lock_in_period')),
                    'tenant_phone_number': clean_phone_number(row.get('tenant_phone_number')),
                    'tenant_email': clean_string_value(row.get('tenant_email')),
                    'notice_start_date': parse_date_only(row.get('notice_start_date')),
                    'notice_issued_date': parse_date_only(row.get('notice_issued_date')),
                    'tenant_move_out_date': parse_date_only(row.get('tenant_move_out_date')),
                    'fixed_cam_charge': clean_numeric_value(row.get('fixed_cam_charge')),
                    'booking_browser_version': clean_string_value(row.get('booking_browser_version')),
                    'booking_ip_address': clean_string_value(row.get('booking_ip_address')),
                    'booking_confirmation': clean_boolean_value(row.get('booking_confirmation')),
                    'booking_amount': clean_numeric_value(row.get('booking_amount')),
                    
                    # kyc_details fields
                    'tenant_status': clean_string_value(row.get('tenant_status')),
                    'resident_type': clean_string_value(row.get('resident_type')),
                    'tenant_full_name': clean_string_value(row.get('tenant_full_name')),
                    'date_of_birth': parse_date_only(row.get('date_of_birth')),
                    'gender': clean_string_value(row.get('gender')),
                    'company_name': clean_string_value(row.get('company_name')),
                    'job_role': clean_string_value(row.get('job_role')),
                    'work_location': clean_string_value(row.get('work_location')),
                    'work_id': clean_string_value(row.get('work_id')),
                    'purpose_of_relocation': clean_string_value(row.get('purpose_of_relocation')),
                    'aadhaar_number': clean_string_value(row.get('aadhaar_number')),
                    'pan_number': clean_string_value(row.get('pan_number')),
                    'co1_name': clean_string_value(row.get('co1_name')),
                    'co1_phone': clean_phone_number(row.get('co1_phone')),
                    'co1_aadhaar': clean_string_value(row.get('co1_aadhaar')),
                    'emergency_contact_name': clean_string_value(row.get('emergency_contact_name')),
                    'emergency_contact_number': clean_phone_number(row.get('emergency_contact_number')),
                    'emergency_contact_relation': clean_string_value(row.get('emergency_contact_relation')),
                    'co2_aadhaar': clean_string_value(row.get('co2_aadhaar')),
                    'co2_name': clean_string_value(row.get('co2_name')),
                    'co2_phone': clean_phone_number(row.get('co2_phone')),
                    'co3_aadhaar': clean_string_value(row.get('co3_aadhaar')),
                    'co3_name': clean_string_value(row.get('co3_name')),
                    'co3_phone': clean_phone_number(row.get('co3_phone')),
                    'passport_number': clean_string_value(row.get('passport_number'))
                }
                
                tenant_records.append(tenant_record)
                processed_count += 1
                
                # Log first few processed items for verification
                if processed_count <= 3:
                    logger.info(f"Row {index + 1}: Found tenant '{tenant_record['tenant_full_name']}' for flat '{flat_slug}'")
                
            except Exception as e:
                logger.warning(f"Row {index + 1}: Error processing row - {e}")
                skipped_count += 1
                continue
        
        logger.info(f"Successfully processed {processed_count} tenant records")
        logger.info(f"Skipped {skipped_count} rows due to missing data")
        
        return tenant_records
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return []

def fetch_flat_ids(conn, tenant_records):
    """
    Fetch flat IDs from database based on flat slugs
    Returns dictionary mapping flat_slug to flat_id
    """
    if not tenant_records:
        logger.warning("No tenant records to process")
        return {}
    
    try:
        cursor = conn.cursor()
        
        # Prepare the query to fetch all flat IDs at once
        flat_slug_list = [record['flat_slug'] for record in tenant_records]
        
        # Use parameterized query to avoid SQL injection
        placeholders = ','.join(['%s'] * len(flat_slug_list))
        query = f"""
            SELECT id, name 
            FROM flats 
            WHERE name IN ({placeholders})
            ORDER BY name
        """
        
        cursor.execute(query, flat_slug_list)
        results = cursor.fetchall()
        
        # Create mapping dictionary
        flat_id_mapping = {}
        for flat_id, name in results:
            flat_id_mapping[name] = flat_id
        
        cursor.close()
        
        logger.info(f"Found {len(flat_id_mapping)} matching flats in database")
        
        return flat_id_mapping
        
    except Exception as e:
        logger.error(f"Error fetching flat IDs: {e}")
        return {}

def insert_booking_order(conn, tenant_record, flat_id):
    """
    Insert record into flat_booking_orders table
    Returns the inserted booking order ID
    """
    try:
        cursor = conn.cursor()
        
        # Insert into flat_booking_orders
        insert_query = """
            INSERT INTO flat_booking_orders (
                flat_id, dummy_order_code, flat_booking_order_code, 
                contract_start_date, contract_end_date, lock_in_period,
                tenant_phone_number, tenant_email, notice_start_date,
                notice_issued_date, tenant_move_out_date, fixed_cam_charge,
                booking_browser_version, booking_ip_address, booking_confirmation,
                booking_amount, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """
        
        current_time = datetime.now()
        
        cursor.execute(insert_query, (
            flat_id,
            tenant_record['booking_reference_id'],  # dummy_order_code
            tenant_record['booking_reference_id'],  # flat_booking_order_code
            tenant_record['contract_start_date'],
            tenant_record['contract_end_date'],
            tenant_record['lock_in_period'],
            tenant_record['tenant_phone_number'],
            tenant_record['tenant_email'],
            tenant_record['notice_start_date'],
            tenant_record['notice_issued_date'],
            tenant_record['tenant_move_out_date'],
            tenant_record['fixed_cam_charge'],
            tenant_record['booking_browser_version'],
            tenant_record['booking_ip_address'],
            tenant_record['booking_confirmation'],
            tenant_record['booking_amount'],
            current_time,
            current_time
        ))
        booking_order_id = cursor.fetchone()[0]
        cursor.close()
        
        logger.info(f"  Inserted booking order ID: {booking_order_id}")
        return booking_order_id
        
    except Exception as e:
        logger.error(f"  Error inserting booking order: {e}")
        conn.rollback()
        raise

def insert_kyc_details(conn, tenant_record, booking_order_id):
    """
    Insert record into kyc_details table
    Returns the inserted kyc_details booking_id
    """
    try:
        cursor = conn.cursor()
        
        # Insert into kyc_details - corrected query with booking_id and booking_reference_id
        insert_query = """
            INSERT INTO kyc_details (
                booking_id, order_id, tenant_status, resident_type, tenant_full_name,
                date_of_birth, gender, company_name, job_role, work_location,
                work_id, purpose_of_relocation, aadhaar_number, pan_number,
                co1_name, co1_phone, co1_aadhaar, emergency_contact_name,
                emergency_contact_number, emergency_contact_relation,
                co2_aadhaar, co2_name, co2_phone, co3_aadhaar, co3_name,
                co3_phone, passport_number, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING booking_id
        """
        
        current_time = datetime.now()
        logger.info(f"  About to insert KYC details with booking_id: {tenant_record['booking_reference_id']} and order_id: {booking_order_id}")
        
        cursor.execute(insert_query, (
            tenant_record['booking_reference_id'],  # booking_id - from Excel
            booking_order_id,  # order_id - the ID from flat_booking_orders
            tenant_record['tenant_status'],
            tenant_record['resident_type'],
            tenant_record['tenant_full_name'],
            tenant_record['date_of_birth'],
            tenant_record['gender'],
            tenant_record['company_name'],
            tenant_record['job_role'],
            tenant_record['work_location'],
            tenant_record['work_id'],
            tenant_record['purpose_of_relocation'],
            tenant_record['aadhaar_number'],
            tenant_record['pan_number'],
            tenant_record['co1_name'],
            tenant_record['co1_phone'],
            tenant_record['co1_aadhaar'],
            tenant_record['emergency_contact_name'],
            tenant_record['emergency_contact_number'],
            tenant_record['emergency_contact_relation'],
            tenant_record['co2_aadhaar'],
            tenant_record['co2_name'],
            tenant_record['co2_phone'],
            tenant_record['co3_aadhaar'],
            tenant_record['co3_name'],
            tenant_record['co3_phone'],
            tenant_record['passport_number'],
            current_time
        ))
        kyc_details_booking_id = cursor.fetchone()[0]
        cursor.close()
        
        logger.info(f"  Inserted KYC details with booking_id: {kyc_details_booking_id}")
        return kyc_details_booking_id
        
    except Exception as e:
        logger.error(f"  Error inserting KYC details: {e}")
        conn.rollback()
        raise

def process_tenant_data(conn, tenant_records, flat_id_mapping, preview_only=False):
    """
    Process tenant data and insert into database tables
    """
    results = []
    stats = {
        'processed': 0,
        'successful_inserts': 0,
        'flat_not_found': 0,
        'insert_errors': 0
    }
    
    logger.info("=" * 70)
    logger.info("TENANT DATA PROCESSING RESULTS")
    logger.info("=" * 70)
    
    for tenant_record in tenant_records:
        try:
            stats['processed'] += 1
            flat_slug = tenant_record['flat_slug']
            row_number = tenant_record['row_number']
            tenant_name = tenant_record['tenant_full_name'] or 'Unknown'
            
            logger.info(f"Row {row_number}: Processing tenant '{tenant_name}' for flat '{flat_slug}'")
            
            if flat_slug not in flat_id_mapping:
                stats['flat_not_found'] += 1
                logger.warning(f"  Flat '{flat_slug}' not found in database")
                results.append({
                    'row_number': row_number,
                    'flat_slug': flat_slug,
                    'tenant_name': tenant_name,
                    'status': 'Flat Not Found',
                    'booking_order_id': None,
                    'kyc_details_id': None
                })
                continue
            
            flat_id = flat_id_mapping[flat_slug]
            logger.info(f"  Found flat ID: {flat_id}")
            
            if preview_only:
                logger.info(f"  [PREVIEW] Would insert booking order and KYC details")
                results.append({
                    'row_number': row_number,
                    'flat_slug': flat_slug,
                    'tenant_name': tenant_name,
                    'status': 'Preview - Would Insert',
                    'booking_order_id': 'PREVIEW',
                    'kyc_details_id': 'PREVIEW'
                })
                continue
            
            # Insert booking order
            booking_order_id = insert_booking_order(conn, tenant_record, flat_id)
            logger.info(f"  Received booking_order_id: {booking_order_id} (type: {type(booking_order_id)})")
            
            # Insert KYC details
            kyc_details_id = insert_kyc_details(conn, tenant_record, booking_order_id)
            
            # Commit the transaction
            conn.commit()
            
            stats['successful_inserts'] += 1
            logger.info(f"  SUCCESS: Inserted booking order {booking_order_id} and KYC details {kyc_details_id}")
            
            results.append({
                'row_number': row_number,
                'flat_slug': flat_slug,
                'tenant_name': tenant_name,
                'status': 'Success',
                'booking_order_id': booking_order_id,
                'kyc_details_id': kyc_details_id
            })
            
        except Exception as e:
            stats['insert_errors'] += 1
            logger.error(f"Row {row_number}: Error processing tenant - {e}")
            conn.rollback()
            
            results.append({
                'row_number': row_number,
                'flat_slug': flat_slug,
                'tenant_name': tenant_name,
                'status': f'Error: {str(e)}',
                'booking_order_id': None,
                'kyc_details_id': None
            })
            continue
    
    logger.info("=" * 70)
    logger.info(f"Total tenant records processed: {stats['processed']}")
    logger.info(f"Successful inserts: {stats['successful_inserts']}")
    logger.info(f"Flats not found: {stats['flat_not_found']}")
    logger.info(f"Insert errors: {stats['insert_errors']}")
    logger.info("=" * 70)
    
    # Verify actual database records if any inserts were successful
    if stats['successful_inserts'] > 0 and not preview_only:
        verify_database_inserts(conn)
    
    return results, stats

def verify_database_inserts(conn):
    """Verify the actual database inserts by querying recent records"""
    try:
        cursor = conn.cursor()
        
        logger.info("\n" + "=" * 70)
        logger.info("DATABASE VERIFICATION - Recent Inserts")
        logger.info("=" * 70)
        
        # Check recent flat_booking_orders
        cursor.execute("""
            SELECT COUNT(*) FROM flat_booking_orders 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)
        recent_booking_orders = cursor.fetchone()[0]
        logger.info(f"Recent flat_booking_orders (last hour): {recent_booking_orders}")
        
        # Check recent kyc_details
        cursor.execute("""
            SELECT COUNT(*) FROM kyc_details 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)
        recent_kyc_details = cursor.fetchone()[0]
        logger.info(f"Recent kyc_details (last hour): {recent_kyc_details}")
        
        # Show sample of recent records
        if recent_booking_orders > 0:
            logger.info("\nSample recent flat_booking_orders:")
            cursor.execute("""
                SELECT id, flat_id, dummy_order_code, tenant_phone_number, created_at
                FROM flat_booking_orders 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                logger.info(f"  ID: {row[0]}, Flat: {row[1]}, Code: {row[2]}, Phone: {row[3]}, Created: {row[4]}")
        
        if recent_kyc_details > 0:
            logger.info("\nSample recent kyc_details:")
            cursor.execute("""
                SELECT booking_id, order_id, tenant_full_name, tenant_status, created_at
                FROM kyc_details 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                logger.info(f"  Booking ID: {row[0]}, Order ID: {row[1]}, Name: {row[2]}, Status: {row[3]}, Created: {row[4]}")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error verifying database inserts: {e}")

def save_results_to_excel(results, output_file):
    """Save processing results to Excel file"""
    try:
        df_results = pd.DataFrame(results)
        df_results.to_excel(output_file, index=False)
        logger.info(f"Results saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to Excel: {e}")

def main():
    """Main function to run the tenant data import"""
    if len(sys.argv) < 2:
        print("Usage: python fetch_flat_ids_from_slugs.py <excel_file_path> [--preview] [--output=results.xlsx] [--sheet=SheetName]")
        print("Example: python fetch_flat_ids_from_slugs.py Active_and_Old_Tenant.xlsx")
        print("  --preview : Show what would be inserted without making changes")
        print("  --output  : Save results to Excel file")
        print("  --sheet   : Specify sheet name (default: 'Active Tenant')")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    
    # Parse command line arguments
    preview_only = '--preview' in sys.argv
    output_file = None
    sheet_name = "Active Tenant"
    
    for arg in sys.argv:
        if arg.startswith('--output='):
            output_file = arg.split('=')[1]
        elif arg.startswith('--sheet='):
            sheet_name = arg.split('=')[1]
    
    logger.info(f"Starting tenant data import from: {excel_file_path}")
    logger.info(f"Sheet: {sheet_name}")
    logger.info(f"Preview mode: {preview_only}")
    logger.info(f"Log file: flat_ids_fetch.log")
    if output_file:
        logger.info(f"Results will be saved to: {output_file}")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    # Step 1: Read Excel file
    logger.info("Step 1: Reading Excel file...")
    tenant_records = read_excel_file(excel_file_path, sheet_name)
    
    if not tenant_records:
        logger.error("No valid tenant records found in Excel file. Exiting.")
        sys.exit(1)
    
    # Step 2: Connect to database
    logger.info("Step 2: Connecting to database...")
    conn = connect_db()
    
    if conn is None:
        logger.error("Could not connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Step 3: Fetch flat IDs
        logger.info("Step 3: Fetching flat IDs from database...")
        flat_id_mapping = fetch_flat_ids(conn, tenant_records)
        
        # Step 4: Process tenant data
        logger.info("Step 4: Processing tenant data...")
        results, stats = process_tenant_data(conn, tenant_records, flat_id_mapping, preview_only)
        
        # Step 5: Save results if requested
        if output_file:
            logger.info("Step 5: Saving results to Excel...")
            save_results_to_excel(results, output_file)
        
        if stats['successful_inserts'] > 0:
            logger.info(f"SUCCESS: Imported {stats['successful_inserts']} tenant records!")
        elif preview_only:
            logger.info("Preview completed - no database changes made")
        else:
            logger.info("No tenant records were imported")
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
