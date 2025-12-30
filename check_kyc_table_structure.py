#!/usr/bin/env python3
"""
Script to check the structure of kyc_details table
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        load_dotenv()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
    
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 5432)
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_table_structure(cursor, table_name):
    """Check the structure of a table"""
    print(f"\n{'='*60}")
    print(f"TABLE STRUCTURE: {table_name.upper()}")
    print(f"{'='*60}")
    
    try:
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        if columns:
            print(f"Columns in {table_name}:")
            print("-" * 80)
            print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default':<20}")
            print("-" * 80)
            
            for col in columns:
                default_val = str(col[3])[:18] if col[3] else 'None'
                print(f"{col[0]:<30} {col[1]:<20} {col[2]:<10} {default_val:<20}")
        else:
            print(f"Table {table_name} not found or no columns")
            
    except Exception as e:
        print(f"Error checking table structure: {e}")

def check_recent_kyc_records(cursor):
    """Check recent kyc_details records with correct columns"""
    print(f"\n{'='*60}")
    print("RECENT KYC_DETAILS RECORDS")
    print(f"{'='*60}")
    
    try:
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM kyc_details")
        total_count = cursor.fetchone()[0]
        print(f"Total records in kyc_details: {total_count}")
        
        # Get recent records with basic columns
        cursor.execute("""
            SELECT 
                booking_id, 
                order_id, 
                tenant_status,
                tenant_full_name,
                created_at
            FROM kyc_details 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_records = cursor.fetchall()
        
        if recent_records:
            print(f"\nLatest 10 records:")
            print("-" * 100)
            print(f"{'Booking ID':<20} {'Order ID':<10} {'Status':<20} {'Name':<30} {'Created At':<20}")
            print("-" * 100)
            
            for record in recent_records:
                print(f"{record[0]:<20} {record[1]:<10} {record[2]:<20} {record[3]:<30} {record[4]}")
        else:
            print("No records found in kyc_details")
            
    except Exception as e:
        print(f"Error checking kyc_details: {e}")

def main():
    """Main function"""
    print("Checking table structures and recent records...")
    
    connection = connect_db()
    if not connection:
        print("Failed to connect to database")
        sys.exit(1)
    
    try:
        cursor = connection.cursor()
        
        # Check table structures
        check_table_structure(cursor, 'flat_booking_orders')
        check_table_structure(cursor, 'kyc_details')
        
        # Check recent records
        check_recent_kyc_records(cursor)
        
    except Exception as e:
        print(f"Error during database check: {e}")
    finally:
        if connection:
            connection.close()
            print(f"\nDatabase connection closed.")

if __name__ == "__main__":
    main()

