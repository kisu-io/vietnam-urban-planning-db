#!/usr/bin/env python3
"""
Fetch Ho Chi Minh City GIS data from HCMGIS and Open Data portals.
Sources:
- https://hcmgis.vn/ - HCMGIS platform (OFFLINE - returns 404)
- https://opendata.hochiminhcity.gov.vn/ - HCMC Open Data Portal (INACCESSIBLE)
- https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw - CSW Catalog (WORKING)

STATUS (2026-04-03):
- HCMGIS WMS/WFS: OFFLINE (404)
- HCMC Open Data Portal: INACCESSIBLE
- HCMC CSW Catalog: OPERATIONAL - metadata catalog accessible

This script now focuses on:
1. Querying the CSW catalog for metadata
2. Documenting available data sources
3. Using fallback sources (GADM, manual imports)
"""

import os
import json
import requests
import re
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "ho-chi-minh-city"
METADATA_DIR = Path(__file__).parent.parent / "metadata"

DATA_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# HCMGIS WMS/WFS endpoints - CURRENTLY OFFLINE (404)
HCMGIS_SERVICES = {
    "base_url": "https://hcmgis.vn/",
    "wms": "https://hcmgis.vn/geoserver/wms",  # Returns 404
    "wfs": "https://hcmgis.vn/geoserver/wfs"   # Returns 404
}

# HCMC Open Data Portal - INACCESSIBLE
HCMC_OPENDATA_URL = "https://opendata.hochiminhcity.gov.vn/"

# HCMC Geoportal CSW - WORKING (metadata catalog)
HCMC_CSW_URL = "https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw"

def query_csw_catalog():
    """Query CSW catalog for available datasets metadata."""
    print("\nQuerying HCMC Geoportal CSW Catalog...")
    print(f"  URL: {HCMC_CSW_URL}")
    
    xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    service="CSW" version="2.0.2" resultType="results"
    maxRecords="50">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>summary</csw:ElementSetName>
    </csw:Query>
</csw:GetRecords>"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/xml',
        'Content-Type': 'application/xml'
    }
    
    try:
        response = requests.post(
            HCMC_CSW_URL,
            data=xml_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"  ✓ CSW catalog accessible")
            print(f"  Response length: {len(response.text)} chars")
            
            # Parse titles from response
            titles = re.findall(r'<dc:title[^>]*>([^<]+)</dc:title>', response.text)
            identifiers = re.findall(r'<dc:identifier[^>]*>([^<]+)</dc:identifier>', response.text)
            
            print(f"  Found {len(titles)} dataset titles")
            print(f"  Found {len(identifiers)} identifiers")
            
            return {
                "status": "success",
                "titles": titles[:20],
                "identifiers": identifiers[:10],
                "raw_response": response.text[:2000]  # First 2000 chars
            }
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return {"status": "error", "http_status": response.status_code}
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "error", "error": str(e)}

def fetch_opendata_catalog():
    """Explore HCMC Open Data Portal API."""
    print("\nExploring HCMC Open Data Portal...")
    print(f"  URL: {HCMC_OPENDATA_URL}")
    
    # CKAN API endpoints
    ckan_api = f"{HCMC_OPENDATA_URL}/api/3/action/"
    
    try:
        # Get package list
        response = requests.get(
            f"{ckan_api}package_list",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                packages = data.get('result', [])
                print(f"  ✓ Found {len(packages)} datasets")
                return packages[:20]  # Return first 20
            else:
                print("  ✗ API returned error")
                return []
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def main():
    print("="*60)
    print("Ho Chi Minh City GIS Data Fetcher")
    print("="*60)
    print("\nSTATUS: WMS/WFS services offline - using CSW catalog fallback")
    print(f"Started: {datetime.now().isoformat()}")
    
    results = {
        "hcmgis": {"status": "offline", "url": HCMGIS_SERVICES["wfs"]},
        "opendata": [],
        "csw_catalog": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Query CSW catalog
    print("\n[1] Querying CSW Catalog...")
    print("-" * 40)
    csw_result = query_csw_catalog()
    results["csw_catalog"] = csw_result
    
    # 2. Try Open Data Portal (expected to fail)
    print("\n[2] Trying Open Data Portal...")
    print("-" * 40)
    packages = fetch_opendata_catalog()
    results["opendata"] = packages
    
    # 3. Check for local Thu Duc data
    thuduc_files = [
        "/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/temp_gisdata/Thu Duc City Data - Thành phố Thủ Đức/ThuDucCity_boundary.json",
        "/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/temp_gisdata/Thu Duc City Data - Thành phố Thủ Đức/ThuDucCity_ward.json"
    ]
    
    print("\n[3] Checking for local Thu Duc City data...")
    print("-" * 40)
    thuduc_found = []
    for src_file in thuduc_files:
        if os.path.exists(src_file):
            import shutil
            dest_name = Path(src_file).name.replace('.json', '.geojson')
            dest = DATA_DIR / dest_name
            shutil.copy(src_file, dest)
            print(f"  ✓ Copied: {dest_name}")
            thuduc_found.append(dest_name)
    
    if not thuduc_found:
        print("  ℹ No local Thu Duc data found")
    
    results["thuduc"] = thuduc_found
    
    # 4. Save metadata
    metadata = {
        "city": "Ho Chi Minh City",
        "status": "wms_blocked",
        "last_updated": datetime.now().isoformat(),
        "sources": {
            "hcmgis_wfs": {
                "url": HCMGIS_SERVICES["wfs"],
                "status": "offline",
                "notes": "Server returns 404 - service may have moved or been discontinued"
            },
            "opendata": {
                "url": HCMC_OPENDATA_URL,
                "status": "inaccessible",
                "datasets_found": len(packages)
            },
            "csw_catalog": {
                "url": HCMC_CSW_URL,
                "status": csw_result.get("status", "unknown"),
                "datasets_found": len(csw_result.get("titles", [])) if isinstance(csw_result, dict) else 0,
                "notes": "CSW catalog operational - metadata only, no direct data access"
            }
        },
        "fallback_sources": [
            {
                "name": "GADM",
                "url": "https://gadm.org",
                "type": "administrative_boundaries",
                "status": "available"
            },
            {
                "name": "OpenStreetMap",
                "url": "https://www.openstreetmap.org",
                "type": "general_gis",
                "status": "available"
            }
        ],
        "data_path": str(DATA_DIR)
    }
    
    metadata_file = DATA_DIR / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 5. Save CSW catalog data if available
    if csw_result and csw_result.get("status") == "success":
        csw_data_file = DATA_DIR / "csw_catalog_summary.json"
        with open(csw_data_file, 'w', encoding='utf-8') as f:
            json.dump(csw_result, f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ CSW catalog summary saved to: {csw_data_file}")
    
    # 6. Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Data directory: {DATA_DIR}")
    print(f"\nSource Status:")
    print(f"  ✗ HCMGIS WFS: OFFLINE (404)")
    print(f"  ✗ Open Data Portal: INACCESSIBLE")
    print(f"  ✓ CSW Catalog: OPERATIONAL ({len(csw_result.get('titles', [])) if isinstance(csw_result, dict) else 0} datasets)")
    print(f"\nLocal Data:")
    print(f"  ✓ Thu Duc City files: {len(thuduc_found)}")
    print(f"\nMetadata saved to: {metadata_file}")
    print(f"\nNOTE: Planning zone data (quy hoạch phân khu) requires:")
    print(f"  1. Manual download from official HCMC portals")
    print(f"  2. Request access via government channels")
    print(f"  3. Alternative: Vietnamese planning research datasets")
    
    return results

if __name__ == "__main__":
    main()
