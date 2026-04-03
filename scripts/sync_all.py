#!/usr/bin/env python3
"""
Master sync script for Vietnam Urban Planning Database.
Runs all fetch scripts and generates unified metadata.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
METADATA_DIR = BASE_DIR / "metadata"

def run_script(script_name):
    """Run a fetch script and return success status."""
    script_path = SCRIPT_DIR / script_name
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=False,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout after 5 minutes")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def generate_master_metadata():
    """Generate unified metadata from all city metadata files."""
    print("\n" + "="*60)
    print("Generating Master Metadata")
    print("="*60)
    
    master_metadata = {
        "project": "vietnam-urban-planning-db",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "cities": {},
        "administrative": {}
    }
    
    # Collect all city metadata
    cities = [
        "ho-chi-minh-city", "hanoi", "haiphong", "da-nang",
        "phu-quoc", "binh-duong", "vung-tau", "can-tho"
    ]
    
    for city in cities:
        city_metadata_file = DATA_DIR / city / "metadata.json"
        if city_metadata_file.exists():
            with open(city_metadata_file, 'r', encoding='utf-8') as f:
                city_metadata = json.load(f)
                master_metadata["cities"][city] = city_metadata
                print(f"  ✓ {city}")
        else:
            print(f"  ⚠ {city} - no metadata found")
    
    # Check for administrative data
    admin_metadata_file = DATA_DIR / "administrative" / "metadata.json"
    if admin_metadata_file.exists():
        with open(admin_metadata_file, 'r', encoding='utf-8') as f:
            master_metadata["administrative"] = json.load(f)
    
    # Save master metadata
    master_metadata_file = METADATA_DIR / "sources.json"
    with open(master_metadata_file, 'w', encoding='utf-8') as f:
        json.dump(master_metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n  ✓ Master metadata saved to {master_metadata_file}")
    return master_metadata

def generate_data_inventory():
    """Generate inventory of all available data files."""
    print("\n" + "="*60)
    print("Generating Data Inventory")
    print("="*60)
    
    inventory = {
        "generated_at": datetime.now().isoformat(),
        "total_files": 0,
        "total_size_bytes": 0,
        "by_category": {}
    }
    
    for category_dir in DATA_DIR.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            inventory["by_category"][category_name] = {
                "files": [],
                "total_size": 0
            }
            
            for data_file in category_dir.glob("*.geojson"):
                size = data_file.stat().st_size
                inventory["by_category"][category_name]["files"].append({
                    "name": data_file.name,
                    "size": size,
                    "path": str(data_file.relative_to(BASE_DIR))
                })
                inventory["by_category"][category_name]["total_size"] += size
                inventory["total_size_bytes"] += size
                inventory["total_files"] += 1
            
            print(f"  {category_name}: {len(inventory['by_category'][category_name]['files'])} files")
    
    # Save inventory
    inventory_file = METADATA_DIR / "inventory.json"
    with open(inventory_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)
    
    print(f"\n  ✓ Inventory saved to {inventory_file}")
    print(f"  Total files: {inventory['total_files']}")
    print(f"  Total size: {inventory['total_size_bytes'] / (1024*1024):.2f} MB")
    
    return inventory

def main():
    print("="*60)
    print("Vietnam Urban Planning DB - Sync All")
    print("="*60)
    
    results = {}
    
    # Run each fetch script
    scripts = [
        ("fetch_boundaries.py", "Administrative Boundaries"),
        ("fetch_hcmgis.py", "Ho Chi Minh City"),
        ("fetch_hanoi.py", "Hanoi"),
        ("fetch_other_cities.py", "Other Cities")
    ]
    
    for script_name, description in scripts:
        success = run_script(script_name)
        results[description] = "✓ Success" if success else "✗ Failed"
    
    # Generate metadata
    master_metadata = generate_master_metadata()
    inventory = generate_data_inventory()
    
    # Final summary
    print("\n" + "="*60)
    print("Sync Complete - Summary")
    print("="*60)
    
    for description, status in results.items():
        print(f"  {description}: {status}")
    
    print(f"\n  Total data files: {inventory['total_files']}")
    print(f"  Total size: {inventory['total_size_bytes'] / (1024*1024):.2f} MB")
    print(f"\n  Metadata: {METADATA_DIR / 'sources.json'}")
    print(f"  Inventory: {METADATA_DIR / 'inventory.json'}")

if __name__ == "__main__":
    main()
