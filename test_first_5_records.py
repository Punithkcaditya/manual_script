#!/usr/bin/env python3
"""
Test script to insert just the first 5 records to verify everything works
"""

import subprocess
import sys
import time

def run_test():
    """Run the script and capture output"""
    print("Testing insertion of first few records...")
    
    try:
        # Run without --preview flag but interrupt after a few seconds
        process = subprocess.Popen([
            'python', 'fetch_flat_ids_from_slugs.py', 
            'Active_and_Old_Tenant.xlsx'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it run for 30 seconds (should process first few records)
        time.sleep(30)
        
        # Terminate the process
        process.terminate()
        
        # Get output
        stdout, stderr = process.communicate(timeout=5)
        
        print("STDOUT (last 2000 chars):")
        print(stdout[-2000:])
        
        if stderr:
            print("\nSTDERR:")
            print(stderr[-1000:])
            
        return process.returncode
        
    except Exception as e:
        print(f"Error running test: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_test()
    print(f"\nTest completed with exit code: {exit_code}")
