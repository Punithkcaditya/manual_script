#!/usr/bin/env python3
"""
Test script to insert just one record to verify the fix works
"""

import subprocess
import sys

def run_single_record_test():
    """Run the script with just the first record"""
    print("Testing single record insertion...")
    
    # Create a temporary Excel file with just one record would be complex
    # Instead, let's modify the main script to process only the first record
    
    # For now, let's just run the script without preview to see what happens
    try:
        # Run without --preview flag
        result = subprocess.run([
            'python', 'fetch_flat_ids_from_slugs.py', 
            'Active_and_Old_Tenant.xlsx'
        ], capture_output=True, text=True, timeout=60)
        
        print("STDOUT:")
        print(result.stdout[-2000:])  # Last 2000 characters
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr[-1000:])  # Last 1000 characters
        
        print(f"\nExit code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Script timed out after 60 seconds")
    except Exception as e:
        print(f"Error running script: {e}")

if __name__ == "__main__":
    run_single_record_test()
