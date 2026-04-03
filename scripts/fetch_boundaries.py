#!/usr/bin/env python3
"""
Fetch Vietnam administrative boundaries data.
Downloads provinces, districts, and wards GeoJSON from available sources.
"""

import os
import json
import requests
from pathlib import Path

# Base paths
DATA_DIR = Path(__file__).parent.parent / "data" / "administrative"
METADATA_DIR = Path(__file__).parent.parent / "metadata"

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Known data sources
SOURCES = {
    "provinces": [
        # Primary source - Local copy from GISData repo
        {
            "name": "adminvsrm/GISData",
            "file": "Vietnam Administrative Divisions (Post-2025)/Provinces.geojson"
        }
    ],
    "districts": [],
    "wards": []
}

def download_with_progress(url: str, dest: Path, headers=None):
    """Download file with progress tracking."""
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        print(f"\nSaved to {dest}")
        return True
    except Exception as e:
        print(f"Error downloading from {url}: {e}")
        return False

def fetch_gadm_vietnam():
    """
    Fetch Vietnam boundaries from GADM (Global Administrative Areas).
    GADM provides free administrative boundaries for all countries.
    """
    print("Fetching Vietnam boundaries from GADM...")
    
    # GADM GeoJSON URLs (Level 0 = country, 1 = provinces, 2 = districts, 3 = wards)
    gadm_urls = {
        "country": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_0.json",
        "provinces": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_1.json",
        "districts": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_2.json",
        "wards": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_3.json"
    }
    
    results = {}
    for level, url in gadm_urls.items():
        dest = DATA_DIR / f"{level}_gadm.geojson"
        print(f"\nDownloading {level} boundaries...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if download_with_progress(url, dest, headers):
            results[level] = str(dest)
            # Also save as standard name for provinces
            if level == "provinces":
                standard_dest = DATA_DIR / "provinces.geojson"
                import shutil
                shutil.copy(dest, standard_dest)
                print(f"Also saved as {standard_dest}")
    
    return results

def main():
    print("="*60)
    print("Vietnam Administrative Boundaries Fetcher")
    print("="*60)
    
    # Try GADM first (most reliable source)
    results = fetch_gadm_vietnam()
    
    print("\n" + "="*60)
    print("Fetch Results:")
    print("="*60)
    for level, path in results.items():
        print(f"✓ {level}: {path}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()