#!/usr/bin/env python3
"""
Query CSW catalog and explore available datasets
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

CSW_URL = "https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/xml',
    'Content-Type': 'application/xml'
}

def csw_getcapabilities():
    """Get CSW capabilities"""
    params = {
        'service': 'CSW',
        'request': 'GetCapabilities'
    }
    response = requests.get(CSW_URL, params=params, headers=HEADERS, timeout=30)
    return response.text

def csw_getrecords(start=1, max=10):
    """Query for records (datasets)"""
    
    # CSW GetRecords request (ISO 19139/19115 metadata)
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:gmd="http://www.isotc211.org/2005/gmd"
    service="CSW"
    version="2.0.2"
    resultType="results"
    startPosition="{start}"
    maxRecords="{max}">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
    </csw:Query>
</csw:GetRecords>"""
    
    try:
        response = requests.post(
            CSW_URL,
            data=xml_payload,
            headers=HEADERS,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

def csw_getrecords_by_keyword(keyword):
    """Search for records by keyword (e.g., 'quy hoạch', 'planning')"""
    
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gmd="http://www.isotc211.org/2005/gmd"
    service="CSW"
    version="2.0.2"
    resultType="results"
    maxRecords="20">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>summary</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\\">
                    <ogc:PropertyName>AnyText</ogc:PropertyName>
                    <ogc:Literal>*{keyword}*</ogc:Literal>
                </ogc:PropertyIsLike>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>"""
    
    try:
        response = requests.post(
            CSW_URL,
            data=xml_payload,
            headers=HEADERS,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

def parse_records(xml_text):
    """Parse CSW response to extract record info"""
    try:
        root = ET.fromstring(xml_text)
        
        # Define namespaces
        ns = {
            'csw': 'http://www.opengis.net/cat/csw/2.0.2',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dct': 'http://purl.org/dc/terms/',
            'gmd': 'http://www.isotc211.org/2005/gmd'
        }
        
        records = []
        
        # Try different record formats
        for record in root.findall('.//csw:Record', ns):
            title = record.find('.//dc:title', ns)
            identifier = record.find('.//dc:identifier', ns)
            abstract = record.find('.//dct:abstract', ns)
            
            records.append({
                'title': title.text if title is not None else 'N/A',
                'identifier': identifier.text if identifier is not None else 'N/A',
                'abstract': abstract.text if abstract is not None else 'N/A'
            })
        
        # Also try ISO metadata format
        for md in root.findall('.//gmd:MD_Metadata', ns):
            title_elem = md.find('.//gmd:title/gco:CharacterString', {**ns, 'gco': 'http://www.isotc211.org/2005/gco'})
            if title_elem is not None:
                records.append({
                    'title': title_elem.text,
                    'identifier': 'ISO record',
                    'abstract': 'See full XML'
                })
        
        return records
    except Exception as e:
        return [{'error': str(e), 'raw': xml_text[:500]}]

def main():
    print("="*60)
    print("HCMC GEOPORTAL CSW CATALOG EXPLORER")
    print("="*60)
    
    # 1. Get capabilities
    print("\n[1] Getting CSW Capabilities...")
    caps = csw_getcapabilities()
    print(f"Response length: {len(caps)} chars")
    
    # Parse to see what operations are supported
    if 'GetRecords' in caps:
        print("✓ GetRecords operation supported")
    if 'GetRecordById' in caps:
        print("✓ GetRecordById operation supported")
    
    # 2. Get all records
    print("\n[2] Querying for datasets...")
    records_xml = csw_getrecords(start=1, max=20)
    
    # 3. Parse and display
    records = parse_records(records_xml)
    print(f"\nFound {len(records)} records:")
    for i, rec in enumerate(records[:10], 1):
        print(f"\n  {i}. {rec.get('title', 'N/A')}")
        print(f"     ID: {rec.get('identifier', 'N/A')[:50]}...")
        if rec.get('abstract') and rec['abstract'] != 'N/A':
            print(f"     Abstract: {rec['abstract'][:100]}...")
    
    # 4. Search for planning-related records
    print("\n[3] Searching for 'quy hoạch' (planning) records...")
    planning_xml = csw_getrecords_by_keyword('quy hoạch')
    planning_records = parse_records(planning_xml)
    print(f"Found {len(planning_records)} planning-related records")
    
    # 5. Save raw responses for analysis
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/csw_all_records.xml', 'w') as f:
        f.write(records_xml)
    
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/csw_planning_records.xml', 'w') as f:
        f.write(planning_xml)
    
    print("\n[4] Saved raw XML responses for analysis:")
    print("    - csw_all_records.xml")
    print("    - csw_planning_records.xml")
    
    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "csw_endpoint": CSW_URL,
        "total_records_found": len(records),
        "planning_records_found": len(planning_records),
        "records": records
    }
    
    import json
    with open('/home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/csw_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Summary saved to: csw_summary.json")

if __name__ == "__main__":
    main()
