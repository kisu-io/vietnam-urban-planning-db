#!/usr/bin/env python3
"""
Test Vietnam urban planning WMS endpoints
Tries multiple approaches including direct HTTP requests
"""

import requests
import json
from urllib.parse import urlencode, parse_qsl, urlparse
from datetime import datetime

# Test results log
results = {
    "timestamp": datetime.now().isoformat(),
    "endpoints_tested": [],
    "wms_responses": [],
    "findings": []
}

# WMS Endpoints to test
ENDPOINTS = [
    # TP.HCM - Official Geoportal
    {
        "name": "HCMC Geoportal (WMS)",
        "url": "https://geoportal-stnmt.tphcm.gov.vn/wms",
        "type": "wms"
    },
    {
        "name": "HCMC Geoportal (CSW)",
        "url": "https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw",
        "type": "csw"
    },
    # Hanoi
    {
        "name": "Hanoi Planning Portal (WMS)",
        "url": "https://data.vqh.hanoi.gov.vn/wms",
        "type": "wms"
    },
    # HCMGIS Alternative
    {
        "name": "HCMGIS GeoServer (WMS)",
        "url": "https://hcmgis.vn/geoserver/wms",
        "type": "wms"
    },
    {
        "name": "HCMGIS GeoServer (WFS)",
        "url": "https://hcmgis.vn/geoserver/wfs",
        "type": "wfs"
    },
    # Alternative HCMC endpoints
    {
        "name": "HCMC Portal Alternative",
        "url": "https://stnmt.tphcm.gov.vn/wms",
        "type": "wms"
    },
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
}

def test_endpoint(endpoint, timeout=30):
    """Test a single endpoint with multiple WMS requests."""
    base_url = endpoint["url"]
    name = endpoint["name"]
    service_type = endpoint["type"]
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {base_url}")
    print(f"Type: {service_type}")
    print('='*60)
    
    result = {
        "name": name,
        "url": base_url,
        "type": service_type,
        "tests": []
    }
    
    # Test 1: Simple GET to base URL
    try:
        print(f"\n[1] Simple GET to base URL...")
        response = requests.get(base_url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"    Final URL: {response.url}")
        result["tests"].append({
            "test": "simple_get",
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type'),
            "final_url": response.url,
            "length": len(response.content)
        })
        
        if response.status_code == 200:
            snippet = response.text[:500] if len(response.text) > 0 else "[empty]"
            print(f"    Response snippet: {snippet[:200]}...")
    except Exception as e:
        print(f"    Error: {e}")
        result["tests"].append({"test": "simple_get", "error": str(e)})
    
    # Test 2: WMS GetCapabilities
    if service_type in ['wms', 'wfs']:
        try:
            print(f"\n[2] WMS GetCapabilities...")
            params = {
                'service': 'WMS' if service_type == 'wms' else 'WFS',
                'request': 'GetCapabilities',
                'version': '1.1.1'
            }
            response = requests.get(base_url, params=params, headers=HEADERS, timeout=timeout)
            print(f"    Status: {response.status_code}")
            print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            test_result = {
                "test": "getcapabilities_1.1.1",
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type')
            }
            
            if response.status_code == 200:
                if 'xml' in response.headers.get('Content-Type', '').lower():
                    snippet = response.text[:800]
                    print(f"    Response (first 500 chars): {snippet[:500]}...")
                    # Check for WMS/WFS keywords
                    if 'WMS_Capabilities' in response.text or 'WFS_Capabilities' in response.text:
                        print(f"    ✓ Valid WMS/WFS Capabilities response!")
                        test_result["valid_capabilities"] = True
                else:
                    print(f"    Response: {response.text[:300]}...")
            
            result["tests"].append(test_result)
        except Exception as e:
            print(f"    Error: {e}")
            result["tests"].append({"test": "getcapabilities_1.1.1", "error": str(e)})
    
    # Test 3: WMS 1.3.0 GetCapabilities
    if service_type == 'wms':
        try:
            print(f"\n[3] WMS 1.3.0 GetCapabilities...")
            params = {
                'service': 'WMS',
                'request': 'GetCapabilities',
                'version': '1.3.0'
            }
            response = requests.get(base_url, params=params, headers=HEADERS, timeout=timeout)
            print(f"    Status: {response.status_code}")
            print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            result["tests"].append({
                "test": "getcapabilities_1.3.0",
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type')
            })
        except Exception as e:
            print(f"    Error: {e}")
            result["tests"].append({"test": "getcapabilities_1.3.0", "error": str(e)})
    
    # Test 4: CSW GetCapabilities for CSW endpoints
    if service_type == 'csw':
        try:
            print(f"\n[2] CSW GetCapabilities...")
            params = {
                'service': 'CSW',
                'request': 'GetCapabilities'
            }
            response = requests.get(base_url, params=params, headers=HEADERS, timeout=timeout)
            print(f"    Status: {response.status_code}")
            print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            if response.status_code == 200:
                print(f"    Response: {response.text[:500]}...")
            result["tests"].append({
                "test": "csw_getcapabilities",
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type')
            })
        except Exception as e:
            print(f"    Error: {e}")
            result["tests"].append({"test": "csw_getcapabilities", "error": str(e)})
    
    return result

def test_tile_endpoints():
    """Test common tile/WMTS patterns."""
    print(f"\n{'='*60}")
    print("Testing tile/WMTS endpoints")
    print('='*60)
    
    tile_endpoints = [
        "https://geoportal-stnmt.tphcm.gov.vn/geoserver/gwc/service/wmts",
        "https://geoportal-stnmt.tphcm.gov.vn/geoserver/wms",
        "https://thongtinquyhoach.hochiminhcity.gov.vn/tiles",
        "https://thongtinquyhoach.hochiminhcity.gov.vn/geoserver/wms",
    ]
    
    results = []
    for url in tile_endpoints:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, headers=HEADERS, timeout=20)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            results.append({
                "url": url,
                "status": response.status_code,
                "content_type": response.headers.get('Content-Type'),
                "accessible": response.status_code == 200
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"url": url, "error": str(e), "accessible": False})
    
    return results

def main():
    print("="*60)
    print("VIETNAM URBAN PLANNING WMS ENDPOINT TEST")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    all_results = []
    
    # Test all WMS/WFS/CSW endpoints
    for endpoint in ENDPOINTS:
        result = test_endpoint(endpoint)
        all_results.append(result)
    
    # Test tile/WMTS endpoints
    tile_results = test_tile_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    working_endpoints = []
    blocked_endpoints = []
    
    for r in all_results:
        for test in r.get("tests", []):
            if test.get("status_code") == 200:
                working_endpoints.append({
                    "name": r["name"],
                    "url": r["url"],
                    "test": test["test"]
                })
            elif "error" in test or test.get("status_code") in [403, 401]:
                blocked_endpoints.append({
                    "name": r["name"],
                    "url": r["url"],
                    "issue": test.get("error") or f"HTTP {test.get('status_code')}"
                })
    
    print(f"\nWorking endpoints found: {len(working_endpoints)}")
    for w in working_endpoints:
        print(f"  ✓ {w['name']} - {w['test']}")
    
    print(f"\nBlocked endpoints: {len(blocked_endpoints)}")
    for b in blocked_endpoints:
        print(f"  ✗ {b['name']}: {b['issue']}")
    
    # Save results
    summary = {
        "timestamp": datetime.now().isoformat(),
        "working_endpoints": working_endpoints,
        "blocked_endpoints": blocked_endpoints,
        "all_tests": all_results,
        "tile_tests": tile_results
    }
    
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nFull results saved to: test_results.json")

if __name__ == "__main__":
    main()
