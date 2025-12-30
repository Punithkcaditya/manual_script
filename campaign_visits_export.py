#!/usr/bin/env python3
"""
Campaign Visits Export Script
Exports campaign_visits data to CSV with enriched information from related tables.
"""

import os
import sys
import psycopg2
import csv
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
            port=os.getenv("DB_PORT", 5432)
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_campaign_visits_data(conn):
    """
    Query campaign_visits with all required joins and transformations.
    Returns distinct records based on lead_id.
    """
    try:
        cursor = conn.cursor()
        
        # Complex query with all joins and logic
        query = """
        WITH unique_bookings AS (
            SELECT DISTINCT ON (dummy_order_code)
                id,
                dummy_order_code,
                flat_booking_order_code,
                flat_slug,
                tenant_phone_number
            FROM flat_booking_orders
            WHERE flat_booking_order_code IS NOT NULL
              AND flat_booking_order_code <> '-'
            ORDER BY dummy_order_code, created_at DESC
        ),
        distinct_visits AS (
            SELECT DISTINCT ON (cv.ip_address)
                cv.id,
                cv.timestamp,
                cv.ip_address,
                cv.created_at,
                cv.referrer,
                cv.user_agent,
                cv.area,
                cv.city,
                cv.flat_id,
                cv.dummy_order_code,
                cv.campaign_id,
                cv.lead_id,
                cv.page,

                CASE
                    WHEN cv.campaign_id LIKE 'M00%' THEN 'META'
                    ELSE 'GOOGLE'
                END AS source,

                CASE
                    WHEN cv.page = 'whatsapp_click' THEN 'whatsapp'
                    WHEN ce.id IS NOT NULL THEN 'paidlead_form'
                    WHEN sw.id IS NOT NULL THEN 'phone_call'
                    ELSE NULL
                END AS action_type,

                CASE
                    WHEN ub.dummy_order_code IS NOT NULL THEN 'YES'
                    ELSE 'No'
                END AS bookings,
                
                ub.flat_slug AS flat_view

            FROM public.campaign_visits cv

            LEFT JOIN unique_bookings ub
                ON cv.dummy_order_code = ub.dummy_order_code

            LEFT JOIN contact_enquiries ce
                ON ce.ip::text = cv.ip_address::text

            LEFT JOIN sales_webhook sw
                ON ub.tenant_phone_number IS NOT NULL
                AND sw.phone = CONCAT('+91', ub.tenant_phone_number)

            WHERE cv.timestamp > TIMESTAMPTZ '2025-12-09 18:30:00+00'

            ORDER BY cv.ip_address, cv.timestamp DESC
        )
        SELECT 
            timestamp::date AS date,
            campaign_id,
            source,
            action_type,
            page AS page_url,
            bookings,
            ip_address::text AS ip_address,
            COALESCE(flat_view, '') AS flat_view,
            timestamp AS time_stamp
        FROM distinct_visits
        ORDER BY timestamp DESC
        """
        
        logger.info("Executing query to fetch campaign visits data...")
        cursor.execute(query)
        # print(query)
        # exit()
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} distinct records")
        cursor.close()
        
        return columns, rows
        
    except Exception as e:
        logger.error(f"Error retrieving data from database: {e}")
        raise

def export_to_csv(columns, rows, output_file='campaign_visits_export.csv'):
    """Export data to CSV file"""
    try:
        # Map database column names to CSV column names
        csv_column_mapping = {
            'date': 'Date',
            'campaign_id': 'campaign_id',
            'source': 'Source',
            'action_type': 'action_type (whatsapp / phone_call / paidlead_form)',
            'page_url': 'page_url',
            'bookings': 'Bookings',
            'ip_address': 'IP ADRESS',
            'flat_view': 'FLAT VIEW',
            'time_stamp': 'Time Stamp'
        }
        
        # Create CSV with proper column order
        csv_columns = [
            'Date',
            'campaign_id',
            'Source',
            'action_type (whatsapp / phone_call / paidlead_form)',
            'page_url',
            'Bookings',
            'IP ADRESS',
            'FLAT VIEW',
            'Time Stamp'
        ]
        
        logger.info(f"Writing data to {output_file}...")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(csv_columns)
            
            # Write data rows
            for row in rows:
                # Convert row to dict for easier mapping
                row_dict = dict(zip(columns, row))
                
                # Helper function to format values
                def format_value(value):
                    if value is None:
                        return ''
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    # Handle date objects (from timestamp::date)
                    if hasattr(value, 'strftime'):
                        try:
                            return value.strftime('%Y-%m-%d')
                        except:
                            return str(value)
                    return str(value)
                
                # Format the row according to CSV column order
                csv_row = [
                    format_value(row_dict.get('date')),  # Date
                    format_value(row_dict.get('campaign_id')),  # campaign_id
                    format_value(row_dict.get('source')),  # Source
                    format_value(row_dict.get('action_type')),  # action_type
                    format_value(row_dict.get('page_url')),  # page_url
                    format_value(row_dict.get('bookings', 'No')),  # Bookings
                    format_value(row_dict.get('ip_address')),  # IP ADRESS
                    format_value(row_dict.get('flat_view')),  # FLAT VIEW
                    format_value(row_dict.get('time_stamp'))  # Time Stamp
                ]
                
                writer.writerow(csv_row)
        
        logger.info(f"Successfully exported {len(rows)} records to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise

def main():
    """Main function"""
    logger.info("="*60)
    logger.info("Campaign Visits Export Script")
    logger.info("="*60)
    
    # Connect to database
    conn = None
    try:
        conn = connect_db()
        logger.info("Database connection established")
        
        # Get data
        columns, rows = get_campaign_visits_data(conn)
        
        if not rows:
            logger.warning("No data found to export")
            return
        
        # Export to CSV
        output_file = export_to_csv(columns, rows)
        
        logger.info("="*60)
        logger.info(f"Export completed successfully!")
        logger.info(f"Output file: {output_file}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()

