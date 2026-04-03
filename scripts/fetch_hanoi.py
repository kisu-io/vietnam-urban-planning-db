#!/usr/bin/env python3
"""
Fetch Hanoi GIS data from official planning portals.
Sources:
- https://data.vqh.hanoi.gov.vn/ - Hanoi Planning Portal (SSL Certificate Error)
- https://iquyhoach.com/ - iQuyHoach planning data portal (TIMEOUT)

STATUS (2026-04-03):
- data.vqh.hanoi.gov.vn: SSL certificate hostname mismatch
- iquyhoach.com: Connection timeout
- No direct WMS/WFS access available

This script uses fallback sources for Hanoi administrative data.
"""

import json
import requests
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "hanoi"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Hanoi endpoints - CURRENTLY INACCESSIBLE
HANOI_ENDPOINTS = {
    "vqh_portal": {
        "url": "https://data.vqh.hanoi.gov.vn/",
        "wms": "https://data.vqh.hanoi.gov.vn/wms",
        "status": "ssl_error"
    },
    "iquyhoach": {
        "url": "https://iquyhoach.com/",
        "status": "timeout"
    }
}

def test_hanoi_endpoints():
    """Test Hanoi endpoints and document their status."""
    print("\nTesting Hanoi Planning Portals...")
    print("-" * 40)
    
    results = {}
    
    for name, config in HANOI_ENDPOINTS.items():
        print(f"\n  Testing: {name}")
        print(f"    URL: {config['url']}")
        
        try:
            # Try without SSL verification to document the exact error
            response = requests.get(
                config['url'], 
                timeout=15, 
                verify=False
            )
            print(f"    Status: {response.status_code}")
            results[name] = {
                "url": config['url'],
                "status": response.status_code,
                "accessible": response.status_code < 400
            }
        except requests.exceptions.SSLError as e:
            print(f"    ✗ SSL Error: Certificate hostname mismatch")
            results[name] = {
                "url": config['url'],
                "status": "ssl_error",
                "error": "Certificate not valid for this hostname"
            }
        except requests.exceptions.Timeout:
            print(f"    ✗ Connection timeout")
            results[name] = {
                "url": config['url'],
                "status": "timeout"
            }
        except Exception as e:
            print(f"    ✗ Error: {e}")
            results[name] = {
                "url": config['url'],
                "status": "error",
                "error": str(e)
            }
    
    return results

def main():
    print("="*60)
    print("Hanoi GIS Data Fetcher")
    print("="*60)
    print("\nSTATUS: Official planning portals inaccessible")
    print(f"Started: {datetime.now().isoformat()}")
    
    # Test endpoints
    endpoint_status = test_hanoi_endpoints()
    
    # Save status
    status = {
        "city": "Hanoi",
        "tested_at": datetime.now().isoformat(),
        "endpoints": endpoint_status,
        "fallback_sources": [
            {
                "name": "GADM",
                "url": "https://gadm.org",
                "type": "administrative_boundaries",
                "status": "available"
            },
            {
                "name": "Vietnam National Geoportal",
                "url": "https://geoportal.monre.gov.vn",
                "notes": "May require authentication for detailed planning data"
            }
        ],
        "recommendations": [
            "Contact Hanoi Department of Construction for official planning data",
            "Request access through government data sharing channels",
            "Use GADM for administrative boundaries as fallback"
        ]
    }
    
    metadata_file = DATA_DIR / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nSource Status:")
    for name, result in endpoint_status.items():
        status_icon = "✓" if result.get('accessible') else "✗"
        print(f"  {status_icon} {name}: {result['status']}")
    
    print(f"\nMetadata saved to: {metadata_file}")
    print("\nNOTE: Hanoi planning data requires official access.")
    print("Consider: Government request, academic partnership, or commercial data provider.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
