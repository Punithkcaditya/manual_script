#!/usr/bin/env python3
"""
Script to check database for recent insertions in flat_booking_orders and kyc_details tables
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
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

def check_recent_flat_booking_orders(cursor, hours=24):
    """Check for recent insertions in flat_booking_orders table"""
    print(f"\n{'='*60}")
    print(f"FLAT_BOOKING_ORDERS - Recent insertions (last {hours} hours)")
    print(f"{'='*60}")
    
    try:
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM flat_booking_orders")
        total_count = cursor.fetchone()[0]
        print(f"Total records in flat_booking_orders: {total_count}")
        
        # Check recent insertions
        since_time = datetime.now() - timedelta(hours=hours)
        cursor.execute("""
            SELECT 
                id, 
                flat_id, 
                dummy_order_code, 
                flat_booking_order_code,
                tenant_phone_number,
                tenant_email,
                created_at
            FROM flat_booking_orders 
            WHERE created_at >= %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (since_time,))
        
        recent_records = cursor.fetchall()
        
        if recent_records:
            print(f"Recent records found: {len(recent_records)}")
            print("\nRecent insertions:")
            print("-" * 100)
            print(f"{'ID':<8} {'Flat ID':<8} {'Order Code':<20} {'Phone':<15} {'Email':<25} {'Created At':<20}")
            print("-" * 100)
            
            for record in recent_records:
                print(f"{record[0]:<8} {record[1]:<8} {record[2]:<20} {record[4]:<15} {record[5]:<25} {record[6]}")
        else:
            print(f"No records found in the last {hours} hours")
            
        # Check the latest 5 records regardless of time
        print(f"\nLatest 5 records (regardless of time):")
        cursor.execute("""
            SELECT 
                id, 
                flat_id, 
                dummy_order_code, 
                flat_booking_order_code,
                tenant_phone_number,
                created_at
            FROM flat_booking_orders 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        latest_records = cursor.fetchall()
        if latest_records:
            print("-" * 80)
            print(f"{'ID':<8} {'Flat ID':<8} {'Order Code':<20} {'Phone':<15} {'Created At':<20}")
            print("-" * 80)
            for record in latest_records:
                print(f"{record[0]:<8} {record[1]:<8} {record[2]:<20} {record[4]:<15} {record[5]}")
        
    except Exception as e:
        print(f"Error checking flat_booking_orders: {e}")

def check_recent_kyc_details(cursor, hours=24):
    """Check for recent insertions in kyc_details table"""
    print(f"\n{'='*60}")
    print(f"KYC_DETAILS - Recent insertions (last {hours} hours)")
    print(f"{'='*60}")
    
    try:
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM kyc_details")
        total_count = cursor.fetchone()[0]
        print(f"Total records in kyc_details: {total_count}")
        
        # Check recent insertions
        since_time = datetime.now() - timedelta(hours=hours)
        cursor.execute("""
            SELECT 
                booking_id, 
                order_id, 
                tenant_status,
                tenant_full_name,
                tenant_phone_number,
                created_at
            FROM kyc_details 
            WHERE created_at >= %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (since_time,))
        
        recent_records = cursor.fetchall()
        
        if recent_records:
            print(f"Recent records found: {len(recent_records)}")
            print("\nRecent insertions:")
            print("-" * 100)
            print(f"{'Booking ID':<20} {'Order ID':<10} {'Status':<20} {'Name':<25} {'Phone':<15} {'Created At':<20}")
            print("-" * 100)
            
            for record in recent_records:
                print(f"{record[0]:<20} {record[1]:<10} {record[2]:<20} {record[3]:<25} {record[4]:<15} {record[5]}")
        else:
            print(f"No records found in the last {hours} hours")
            
        # Check the latest 5 records regardless of time
        print(f"\nLatest 5 records (regardless of time):")
        cursor.execute("""
            SELECT 
                booking_id, 
                order_id, 
                tenant_status,
                tenant_full_name,
                created_at
            FROM kyc_details 
            ORDER BY booking_id DESC 
            LIMIT 5
        """)
        
        latest_records = cursor.fetchall()
        if latest_records:
            print("-" * 80)
            print(f"{'Booking ID':<20} {'Order ID':<10} {'Status':<20} {'Name':<25} {'Created At':<20}")
            print("-" * 80)
            for record in latest_records:
                print(f"{record[0]:<20} {record[1]:<10} {record[2]:<20} {record[3]:<25} {record[4]}")
        
    except Exception as e:
        print(f"Error checking kyc_details: {e}")

def check_database_connection_info(cursor):
    """Check database connection and basic info"""
    print(f"\n{'='*60}")
    print("DATABASE CONNECTION INFO")
    print(f"{'='*60}")
    
    try:
        # Check current database
        cursor.execute("SELECT current_database(), current_user, version()")
        db_info = cursor.fetchone()
        print(f"Database: {db_info[0]}")
        print(f"User: {db_info[1]}")
        print(f"PostgreSQL Version: {db_info[2]}")
        
        # Check current time
        cursor.execute("SELECT NOW()")
        current_time = cursor.fetchone()[0]
        print(f"Database Time: {current_time}")
        
    except Exception as e:
        print(f"Error getting database info: {e}")

def main():
    """Main function"""
    print("Checking database for recent insertions...")
    
    connection = connect_db()
    if not connection:
        print("Failed to connect to database")
        sys.exit(1)
    
    try:
        cursor = connection.cursor()
        
        # Check database connection info
        check_database_connection_info(cursor)
        
        # Check recent insertions (last 24 hours)
        check_recent_flat_booking_orders(cursor, hours=24)
        check_recent_kyc_details(cursor, hours=24)
        
        # Also check last 1 hour for very recent insertions
        print(f"\n{'='*60}")
        print("CHECKING LAST 1 HOUR FOR VERY RECENT INSERTIONS")
        print(f"{'='*60}")
        
        check_recent_flat_booking_orders(cursor, hours=1)
        check_recent_kyc_details(cursor, hours=1)
        
    except Exception as e:
        print(f"Error during database check: {e}")
    finally:
        if connection:
            connection.close()
            print(f"\nDatabase connection closed.")

if __name__ == "__main__":
    main()

