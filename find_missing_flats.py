#!/usr/bin/env python3
"""
Simple script to find Flat Master Names that exist in Excel but not in database.
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

def get_flat_names_from_db():
    """Get all flat names from database"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM flats WHERE name IS NOT NULL AND name != ''")
        result = cursor.fetchall()
        
        flat_names = [row[0] for row in result]
        logger.info(f"Retrieved {len(flat_names)} flat names from database")
        return flat_names
        
    except Exception as e:
        logger.error(f"Error retrieving flat names from database: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_flat_names_from_excel(excel_file_path):
    """Get all flat names from Excel file"""
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
        
        if df is None or 'Flat Master Name' not in df.columns:
            logger.error("Column 'Flat Master Name' not found in Excel file")
            logger.error(f"Available columns: {list(df.columns) if df is not None else 'None'}")
            return None
        
        # Remove NaN and empty values
        flat_names = df['Flat Master Name'].dropna()
        flat_names = flat_names[flat_names.str.strip() != ''].tolist()
        
        logger.info(f"Retrieved {len(flat_names)} flat names from Excel")
        return flat_names
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise

def find_missing_flats(excel_file_path):
    """Find flats that exist in Excel but not in database"""
    
    # Get flat names from both sources
    excel_names = get_flat_names_from_excel(excel_file_path)
    if excel_names is None:
        return False
    
    db_names = get_flat_names_from_db()
    
    # Convert to sets for faster lookup
    excel_set = set(excel_names)
    db_set = set(db_names)
    
    # Find missing flats
    missing_flats = sorted(list(excel_set - db_set))
    
    # Print results
    logger.info(f"\n{'='*70}")
    logger.info("FLAT COMPARISON SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total flats in Excel: {len(excel_set)}")
    logger.info(f"Total flats in Database: {len(db_set)}")
    logger.info(f"Flats in Excel but NOT in Database: {len(missing_flats)}")
    
    if missing_flats:
        logger.info(f"\n{'='*70}")
        logger.info("FLAT MASTER NAMES MISSING FROM DATABASE")
        logger.info(f"{'='*70}")
        
        # Save to file
        output_file = 'missing_flat_names.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Flat Master Names that exist in Excel but are missing from database:\n")
            f.write("="*70 + "\n\n")
            
            for i, flat_name in enumerate(missing_flats, 1):
                logger.info(f"  {i:3d}. {flat_name}")
                f.write(f"{i:3d}. {flat_name}\n")
            
            f.write(f"\nSummary:\n")
            f.write(f"Total Excel flats: {len(excel_set)}\n")
            f.write(f"Total database flats: {len(db_set)}\n")
            f.write(f"Missing from database: {len(missing_flats)}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info(f"\nMissing flat names saved to: {output_file}")
        
        # Also create a simple CSV for easy import
        csv_file = 'missing_flat_names.csv'
        missing_df = pd.DataFrame({'Flat Master Name': missing_flats})
        missing_df.to_csv(csv_file, index=False)
        logger.info(f"Missing flat names also saved as CSV: {csv_file}")
        
    else:
        logger.info("\n✓ SUCCESS: All Excel flats exist in the database!")
    
    return True

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python find_missing_flats.py <excel_file_path>")
        print("Example: python find_missing_flats.py Flat_data_before_live.xlsx")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        sys.exit(1)
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    logger.info(f"Finding missing flats from: {excel_file_path}")
    
    try:
        success = find_missing_flats(excel_file_path)
        if success:
            logger.info("Missing flats check completed successfully!")
            sys.exit(0)
        else:
            logger.error("Missing flats check failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during missing flats check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
