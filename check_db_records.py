#!/usr/bin/env python3
"""
Database verification script to check inserted records
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

def load_environment():
    """Load environment variables"""
    try:
        load_dotenv()
        print("SUCCESS: Environment loaded successfully")
    except Exception as e:
        print(f"WARNING: Could not load .env file: {e}")
        print("Continuing with system environment variables...")

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 5432)
        )
        print("SUCCESS: Database connection successful")
        return connection
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return None

def check_recent_records(connection):
    """Check for recently inserted records"""
    try:
        cursor = connection.cursor()
        
        # Check recent flat_booking_orders
        print("\n" + "="*60)
        print("CHECKING FLAT_BOOKING_ORDERS TABLE")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM flat_booking_orders 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)
        recent_bookings = cursor.fetchone()[0]
        print(f"Recent booking orders (last hour): {recent_bookings}")
        
        cursor.execute("SELECT COUNT(*) FROM flat_booking_orders")
        total_bookings = cursor.fetchone()[0]
        print(f"Total booking orders: {total_bookings}")
        
        # Show latest 5 booking orders
        cursor.execute("""
            SELECT id, flat_id, dummy_order_code, created_at 
            FROM flat_booking_orders 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        latest_bookings = cursor.fetchall()
        print("\nLatest 5 booking orders:")
        for booking in latest_bookings:
            print(f"  ID: {booking[0]}, Flat ID: {booking[1]}, Code: {booking[2]}, Created: {booking[3]}")
        
        # Check recent kyc_details
        print("\n" + "="*60)
        print("CHECKING KYC_DETAILS TABLE")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM kyc_details 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)
        recent_kyc = cursor.fetchone()[0]
        print(f"Recent KYC records (last hour): {recent_kyc}")
        
        cursor.execute("SELECT COUNT(*) FROM kyc_details")
        total_kyc = cursor.fetchone()[0]
        print(f"Total KYC records: {total_kyc}")
        
        # Show latest 5 KYC records
        cursor.execute("""
            SELECT booking_id, order_id, tenant_full_name, created_at 
            FROM kyc_details 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        latest_kyc = cursor.fetchall()
        print("\nLatest 5 KYC records:")
        for kyc in latest_kyc:
            print(f"  Booking ID: {kyc[0]}, Order ID: {kyc[1]}, Name: {kyc[2]}, Created: {kyc[3]}")
        
        # Check for specific booking reference IDs from Excel
        print("\n" + "="*60)
        print("CHECKING SPECIFIC BOOKING REFERENCE IDs")
        print("="*60)
        
        test_booking_refs = ['K02B30109092025', 'K02B30209092025', 'K02B30309092025']
        for booking_ref in test_booking_refs:
            cursor.execute("""
                SELECT booking_id, tenant_full_name, created_at 
                FROM kyc_details 
                WHERE booking_id = %s
            """, (booking_ref,))
            result = cursor.fetchone()
            if result:
                print(f"  FOUND: {booking_ref} -> {result[1]} (Created: {result[2]})")
            else:
                print(f"  NOT FOUND: {booking_ref}")
        
        cursor.close()
        
    except Exception as e:
        print(f"ERROR: Error checking records: {e}")

def check_table_structure(connection):
    """Check table structure"""
    try:
        cursor = connection.cursor()
        
        print("\n" + "="*60)
        print("CHECKING TABLE STRUCTURES")
        print("="*60)
        
        # Check kyc_details structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'kyc_details' 
            ORDER BY ordinal_position
        """)
        kyc_columns = cursor.fetchall()
        print("\nKYC_DETAILS table structure:")
        for col in kyc_columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Check flat_booking_orders structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'flat_booking_orders' 
            ORDER BY ordinal_position
        """)
        booking_columns = cursor.fetchall()
        print("\nFLAT_BOOKING_ORDERS table structure:")
        for col in booking_columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        cursor.close()
        
    except Exception as e:
        print(f"ERROR: Error checking table structure: {e}")

def main():
    print("DATABASE VERIFICATION SCRIPT")
    print("="*60)
    
    # Load environment
    load_environment()
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        sys.exit(1)
    
    try:
        # Check recent records
        check_recent_records(connection)
        
        # Check table structure
        check_table_structure(connection)
        
    finally:
        connection.close()
        print("\nSUCCESS: Database connection closed")

if __name__ == "__main__":
    main()
