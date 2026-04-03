#!/usr/bin/env python3
"""
Deep dive into the working CSW endpoint
And try other potential data sources
"""

import requests
import json
import re
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/xml',
}

CSW_URL = "https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw"

def csw_get_all_records():
    """Get all records from CSW catalog"""
    
    # Simple GetRecords request
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    service="CSW" version="2.0.2" resultType="results"
    maxRecords="100">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>summary</csw:ElementSetName>
    </csw:Query>
</csw:GetRecords>"""
    
    try:
        response = requests.post(CSW_URL, data=xml, headers=HEADERS, timeout=30)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def csw_describe_record():
    """Get the record schema description"""
    params = {
        'service': 'CSW',
        'request': 'DescribeRecord'
    }
    try:
        response = requests.get(CSW_URL, params=params, headers=HEADERS, timeout=30)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def parse_csw_response(xml_text):
    """Extract useful info from CSW response"""
    
    # Look for dataset titles
    titles = re.findall(r'&lt;dc:title[^&gt;]*&gt;([^&lt;]+)&lt;/dc:title&gt;', xml_text)
    identifiers = re.findall(r'&lt;dc:identifier[^&gt;]*&gt;([^&lt;]+)&lt;/dc:identifier&gt;', xml_text)
    
    # Look for WMS/WFS URLs
    urls = re.findall(r'(https?://[^\s<>"]+)', xml_text)
    
    return {
        "titles": list(set(titles))[:20],
        "identifiers": list(set(identifiers))[:20],
        "urls": list(set([u for u in urls if 'geoportal' in u or 'hcm' in u.lower()]))[:10]
    }

def test_opendata_portals():
    """Test various Vietnam open data portals"""
    print("\n" + "="*60)
    print("Testing Vietnam Open Data Portals")
    print("="*60)
    
    portals = [
        {
            "name": "HCMC Open Data (CKAN)",
            "url": "https://opendata.hochiminhcity.gov.vn/api/3/action/package_list",
            "type": "ckan"
        },
        {
            "name": "Vietnam Geoportal",
            "url": "https://geoportal.monre.gov.vn/api/3/action/package_list",
            "type": "ckan"
        },
        {
            "name": "Hanoi Open Data",
            "url": "https://opendata.hanoi.gov.vn/api/3/action/package_list",
            "type": "ckan"
        }
    ]
    
    results = []
    for portal in portals:
        try:
            print(f"\nTrying: {portal['name']}")
            print(f"  URL: {portal['url']}")
            response = requests.get(portal['url'], timeout=20)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('result'):
                        count = len(data['result'])
                        print(f"  ✓ Found {count} datasets")
                        results.append({
                            "name": portal['name'],
                            "url": portal['url'],
                            "status": 200,
                            "datasets_count": count,
                            "sample": data['result'][:5]
                        })
                    else:
                        results.append({"name": portal['name'], "status": 200, "accessible": True})
                except:
                    results.append({"name": portal['name'], "status": 200, "accessible": True})
            else:
                results.append({"name": portal['name'], "status": response.status_code})
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"name": portal['name'], "error": str(e)})
    
    return results

def test_arcgis_services():
    """Test for ArcGIS REST services"""
    print("\n" + "="*60)
    print("Testing ArcGIS REST endpoints")
    print("="*60)
    
    arcgis_urls = [
        "https://services.arcgis.com/rest/services",
        "https://geoportal-stnmt.tphcm.gov.vn/arcgis/rest",
        "https://hcmgis.vn/arcgis/rest",
    ]
    
    results = []
    for url in arcgis_urls:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            print(f"  Status: {response.status_code}")
            
            if 'rest' in response.text.lower() or 'arcgis' in response.text.lower():
                print(f"  ✓ ArcGIS response detected")
            
            results.append({
                "url": url,
                "status": response.status_code,
                "has_arcgis": 'arcgis' in response.text.lower()[:2000]
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

def main():
    print("="*60)
    print("DEEP DIVE - CSW AND ALTERNATIVE DATA SOURCES")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Test CSW endpoint
    print("\n" + "="*60)
    print("CSW Endpoint Analysis")
    print("="*60)
    
    print("\n[1] Getting CSW records...")
    records_xml = csw_get_all_records()
    print(f"Response length: {len(records_xml)} characters")
    
    # Parse the response
    parsed = parse_csw_response(records_xml)
    
    print(f"\n[2] Parsed Results:")
    print(f"  Titles found: {len(parsed['titles'])}")
    for t in parsed['titles'][:10]:
        print(f"    - {t}")
    
    print(f"\n  Identifiers found: {len(parsed['identifiers'])}")
    for i in parsed['identifiers'][:5]:
        print(f"    - {i[:50]}...")
    
    print(f"\n  URLs found: {len(parsed['urls'])}")
    for u in parsed['urls']:
        print(f"    - {u}")
    
    # Save the raw CSW response
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/csw_records_raw.xml', 'w', encoding='utf-8') as f:
        f.write(records_xml)
    print(f"\n✓ Raw CSW response saved to: csw_records_raw.xml")
    
    # Test other data sources
    opendata_results = test_opendata_portals()
    arcgis_results = test_arcgis_services()
    
    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "csw_endpoint": CSW_URL,
        "csw_parsed": parsed,
        "opendata_tests": opendata_results,
        "arcgis_tests": arcgis_results
    }
    
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/deep_dive_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"CSW records found: {len(parsed['titles'])}")
    print(f"Working open data portals: {sum(1 for r in opendata_results if r.get('status') == 200)}")
    print(f"Working ArcGIS endpoints: {sum(1 for r in arcgis_results if r.get('status') == 200)}")
    print(f"\nFull results saved to: deep_dive_results.json")

if __name__ == "__main__":
    main()
