#!/usr/bin/env python3
"""
Fetch GIS data for other Vietnamese cities from GADM.
Cities: Hải Phòng, Đà Nẵng, Phú Quốc, Bình Dương, Vũng Tàu, Cần Thơ
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# City configurations with GADM province names (no spaces)
CITIES = {
    "haiphong": {"name": "Hải Phòng", "gadm_name": "HảiPhòng"},
    "da-nang": {"name": "Đà Nẵng", "gadm_name": "ĐàNẵng"},
    "binh-duong": {"name": "Bình Dương", "gadm_name": "BìnhDương"},
    "can-tho": {"name": "Cần Thơ", "gadm_name": "CầnThơ"},
    "vung-tau": {"name": "Bà Rịa - Vũng Tàu", "gadm_name": "BàRịa-VũngTàu"},
    "phu-quoc": {"name": "Phú Quốc", "gadm_name": "KiênGiang"}  # District level
}

def fetch_gadm_data():
    """Download Vietnam districts from GADM."""
    url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_2.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json()

def extract_city_data(city_code, city_config, all_data):
    """Extract and save data for a specific city."""
    data_dir = DATA_DIR / city_code
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Filter features for this city
    city_features = [
        f for f in all_data.get('features', [])
        if f.get('properties', {}).get('NAME_1') == city_config['gadm_name']
    ]
    
    if not city_features:
        print(f"  ⚠ No data found for {city_config['name']}")
        return False
    
    # Save GeoJSON
    city_data = {
        "type": "FeatureCollection",
        "features": city_features,
        "crs": all_data.get('crs')
    }
    
    output_path = data_dir / f"{city_code}_districts_gadm.geojson"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(city_data, f, ensure_ascii=False, indent=2)
    
    # Save metadata
    metadata = {
        "city": city_config['name'],
        "gadm_source": "GADM 4.1",
        "gadm_url": "https://gadm.org",
        "features_count": len(city_features),
        "last_updated": datetime.now().isoformat(),
        "data_path": str(output_path)
    }
    
    metadata_path = data_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Saved {len(city_features)} districts ({output_path.stat().st_size/1024:.1f} KB)")
    return True

def main():
    print("="*60)
    print("Other Cities GIS Data Fetcher")
    print("="*60)
    
    print("\nDownloading Vietnam districts from GADM...")
    try:
        all_data = fetch_gadm_data()
        total_features = len(all_data.get('features', []))
        print(f"  ✓ Downloaded {total_features} districts")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return
    
    print("\nExtracting city data...")
    results = {}
    for city_code, city_config in CITIES.items():
        print(f"\n{city_config['name']}:")
        success = extract_city_data(city_code, city_config, all_data)
        results[city_code] = success
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    success_count = sum(results.values())
    print(f"Cities processed: {success_count}/{len(CITIES)}")
    for city_code, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {CITIES[city_code]['name']}")

if __name__ == "__main__":
    main()
