#!/usr/bin/env python3
"""
Try alternative approaches to access Vietnam planning data
"""

import requests
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://thongtinquyhoach.hochiminhcity.gov.vn/',
}

def test_thongtinquyhoach_api():
    """Test the HCMC planning information portal for APIs"""
    print("="*60)
    print("Testing thongtinquyhoach.hochiminhcity.gov.vn")
    print("="*60)
    
    results = []
    
    # Common API patterns
    api_endpoints = [
        "https://thongtinquyhoach.hochiminhcity.gov.vn/api",
        "https://thongtinquyhoach.hochiminhcity.gov.vn/api/v1",
        "https://thongtinquyhoach.hochiminhcity.gov.vn/geoserver/rest",
        "https://thongtinquyhoach.hochiminhcity.gov.vn/maps",
    ]
    
    for url in api_endpoints:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Final URL: {response.url}")
            results.append({
                "url": url,
                "status": response.status_code,
                "content_type": response.headers.get('Content-Type'),
                "accessible": response.status_code < 400
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

def test_hcmgis_alternatives():
    """Try different HCMGIS endpoints"""
    print("\n" + "="*60)
    print("Testing HCMGIS alternative endpoints")
    print("="*60)
    
    results = []
    
    # HCMGIS possible patterns
    endpoints = [
        "https://hcmgis.vn/geoserver/ows",
        "https://hcmgis.vn/geoserver/web",
        "https://hcmgis.vn/geoserver/rest",
        "https://hcmgis.vn/gis",
        "https://hcmgis.vn/portal",
        "https://hcmgis.vn/arcgis",
        "https://www.hcmgis.vn/geoserver/wms",
    ]
    
    for url in endpoints:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            print(f"  Status: {response.status_code}")
            
            # Check if this is a GeoServer page
            if 'GeoServer' in response.text[:1000] or 'geoserver' in response.text[:1000].lower():
                print(f"  ✓ GeoServer detected!")
            
            results.append({
                "url": url,
                "status": response.status_code,
                "final_url": response.url,
                "has_geoserver": 'GeoServer' in response.text[:2000]
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

def test_wms_v2_endpoints():
    """Try WMS endpoints with different versions and parameters"""
    print("\n" + "="*60)
    print("Testing WMS with various parameter combinations")
    print("="*60)
    
    # Try with different path patterns
    wms_patterns = [
        {
            "name": "HCMC GeoServer direct",
            "url": "https://geoportal-stnmt.tphcm.gov.vn/geoserver/wms",
            "params": {"service": "WMS", "request": "GetCapabilities"}
        },
        {
            "name": "HCMC GeoServer with workspace",
            "url": "https://geoportal-stnmt.tphcm.gov.vn/geoserver/stnmt/wms",
            "params": {"service": "WMS", "request": "GetCapabilities"}
        },
        {
            "name": "HCMC GeoServer ows",
            "url": "https://geoportal-stnmt.tphcm.gov.vn/geoserver/ows",
            "params": {"service": "WMS", "request": "GetCapabilities"}
        },
        {
            "name": "Hanoi iQuyhoach (alternative)",
            "url": "https://iquyhoach.com/api/v1/wms",
            "params": {"service": "WMS", "request": "GetCapabilities"}
        },
    ]
    
    results = []
    for pattern in wms_patterns:
        try:
            print(f"\nTrying: {pattern['name']}")
            print(f"  URL: {pattern['url']}")
            response = requests.get(
                pattern['url'], 
                params=pattern['params'], 
                headers=HEADERS, 
                timeout=20,
                verify=False  # Try without SSL verification for some
            )
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                print(f"  ✓ Response received")
                print(f"  Preview: {response.text[:200]}...")
            
            results.append({
                "name": pattern['name'],
                "url": pattern['url'],
                "status": response.status_code,
                "success": response.status_code == 200 and 'WMS' in response.text[:500]
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"name": pattern['name'], "error": str(e)})
    
    return results

def test_direct_wmts_tiles():
    """Try to access WMTS tiles directly"""
    print("\n" + "="*60)
    print("Testing WMTS tile access")
    print("="*60)
    
    results = []
    
    # Try common tile URL patterns
    wmts_patterns = [
        "https://geoportal-stnmt.tphcm.gov.vn/geoserver/gwc/service/wmts?REQUEST=GetCapabilities",
        "https://geoportal-stnmt.tphcm.gov.vn/geoserver/gwc/service/tms/1.0.0",
    ]
    
    for url in wmts_patterns:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=HEADERS, timeout=20)
            print(f"  Status: {response.status_code}")
            
            results.append({
                "url": url,
                "status": response.status_code,
                "accessible": response.status_code == 200
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

def main():
    print("="*60)
    print("ALTERNATIVE APPROACHES FOR VIETNAM PLANNING DATA")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Disable SSL warnings for testing
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test all alternative approaches
    all_results = {
        "thongtinquyhoach_api": test_thongtinquyhoach_api(),
        "hcmgis_alternatives": test_hcmgis_alternatives(),
        "wms_v2": test_wms_v2_endpoints(),
        "wmts_tiles": test_direct_wmts_tiles()
    }
    
    # Save results
    summary = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }
    
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/alternative_tests.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    # Check for any successes
    successes = []
    for category, results in all_results.items():
        for r in results:
            if r.get('status') == 200 or r.get('accessible') == True:
                successes.append({
                    "category": category,
                    "url": r.get('url') or r.get('name'),
                    "details": r
                })
    
    print(f"\nWorking endpoints: {len(successes)}")
    for s in successes:
        print(f"  ✓ {s['category']}: {s['url']}")
    
    print(f"\nFull results saved to: alternative_tests.json")

if __name__ == "__main__":
    main()
