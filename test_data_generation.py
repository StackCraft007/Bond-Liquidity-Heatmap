#!/usr/bin/env python3
"""Test script to verify data generation works independently."""
import subprocess
import sys
import pathlib

def test_data_generation():
    """Test the data generation process step by step."""
    print("=== Testing Data Generation Process ===\n")
    
    # Step 1: Generate data
    print("1. Generating synthetic trade data...")
    result = subprocess.run([sys.executable, "src/generate_data.py"], 
                          capture_output=True, text=True, cwd=pathlib.Path.cwd())
    
    if result.returncode == 0:
        print("✅ Data generation successful!")
        print("Output:")
        print(result.stdout)
    else:
        print("❌ Data generation failed!")
        print("Error:")
        print(result.stderr)
        return False
    
    # Step 2: Ingest data
    print("\n2. Ingesting data into database...")
    result = subprocess.run([sys.executable, "src/ingest.py"], 
                          capture_output=True, text=True, cwd=pathlib.Path.cwd())
    
    if result.returncode == 0:
        print("✅ Data ingestion successful!")
        print("Output:")
        print(result.stdout)
    else:
        print("❌ Data ingestion failed!")
        print("Error:")
        print(result.stderr)
        return False
    
    # Step 3: Compute metrics
    print("\n3. Computing depth metrics...")
    result = subprocess.run([sys.executable, "src/compute_metrics.py"], 
                          capture_output=True, text=True, cwd=pathlib.Path.cwd())
    
    if result.returncode == 0:
        print("✅ Metrics computation successful!")
        print("Output:")
        print(result.stdout)
    else:
        print("❌ Metrics computation failed!")
        print("Error:")
        print(result.stderr)
        return False
    
    print("\n=== All tests passed! ===")
    return True

if __name__ == "__main__":
    test_data_generation() 