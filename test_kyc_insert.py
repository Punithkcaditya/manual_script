#!/usr/bin/env python3
"""
Test script to debug KYC insertion issue
"""

import os
import sys
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

def load_environment():
    """Load environment variables"""
    try:
        load_dotenv()
        print("SUCCESS: Environment loaded successfully")
    except Exception as e:
        print(f"WARNING: Could not load .env file: {e}")

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

def test_kyc_insert(connection):
    """Test KYC insertion with minimal data"""
    try:
        cursor = connection.cursor()
        
        # Test with minimal required columns only
        print("\nTesting minimal KYC insert...")
        
        test_booking_id = "TEST_BOOKING_123"
        test_order_id = 18700  # Use an existing order_id from our previous inserts
        current_time = datetime.now()
        
        # Try inserting with only required columns
        minimal_insert = """
            INSERT INTO kyc_details (
                booking_id, order_id, created_at
            ) VALUES (
                %s, %s, %s
            ) RETURNING booking_id
        """
        
        print(f"Attempting to insert:")
        print(f"  booking_id: {test_booking_id}")
        print(f"  order_id: {test_order_id}")
        print(f"  created_at: {current_time}")
        
        cursor.execute(minimal_insert, (test_booking_id, test_order_id, current_time))
        result = cursor.fetchone()
        
        if result:
            print(f"SUCCESS: Inserted KYC record with booking_id: {result[0]}")
            
            # Clean up test record
            cursor.execute("DELETE FROM kyc_details WHERE booking_id = %s", (test_booking_id,))
            print("SUCCESS: Test record cleaned up")
            
        else:
            print("ERROR: No result returned from INSERT")
        
        connection.commit()
        cursor.close()
        
    except Exception as e:
        print(f"ERROR: KYC insert test failed: {e}")
        connection.rollback()

def check_kyc_constraints(connection):
    """Check KYC table constraints"""
    try:
        cursor = connection.cursor()
        
        print("\nChecking KYC table constraints...")
        
        # Check NOT NULL constraints
        cursor.execute("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'kyc_details' 
            AND is_nullable = 'NO'
            ORDER BY ordinal_position
        """)
        
        constraints = cursor.fetchall()
        print("NOT NULL columns:")
        for col in constraints:
            print(f"  {col[0]}: nullable={col[1]}, default={col[2]}")
        
        cursor.close()
        
    except Exception as e:
        print(f"ERROR: Failed to check constraints: {e}")

def main():
    print("KYC INSERT DEBUG SCRIPT")
    print("="*50)
    
    # Load environment
    load_environment()
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        sys.exit(1)
    
    try:
        # Check constraints
        check_kyc_constraints(connection)
        
        # Test minimal insert
        test_kyc_insert(connection)
        
    finally:
        connection.close()
        print("\nSUCCESS: Database connection closed")

if __name__ == "__main__":
    main()
