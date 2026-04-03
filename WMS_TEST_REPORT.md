# Vietnam Urban Planning WMS Test Report

**Date:** 2026-04-03
**Tested by:** Subagent mr-robot-wms-harvest
**Repository:** /home/saul-ai/.openclaw/workspace/vietnam-urban-planning-db/

## Executive Summary

WMS/WFS harvesting of Vietnam urban planning data (quy hoạch phân khu) **was not successful** via automated methods. Official Vietnamese government WMS/WFS endpoints are either:
- **Offline** (returning 404)
- **SSL certificate errors** (hostname mismatches)
- **Connection timeouts**

**One working endpoint found:** HCMC Geoportal CSW (Catalog Service for Web) - but this provides metadata only, not actual spatial data.

---

## Tested Endpoints

### 1. Ho Chi Minh City

#### HCMC Geoportal (CSW) - WORKING ✓
- **URL:** `https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw`
- **Status:** Operational
- **Service:** CSW (Catalog Service for Web)
- **Capabilities:** GetCapabilities, GetRecords, DescribeRecord
- **Data Access:** Metadata only - no direct geospatial data
- **Notes:** This is a metadata catalog, not a data service. Can discover what datasets exist but cannot download them.

#### HCMC Geoportal (WMS) - BLOCKED ✗
- **URL:** `https://geoportal-stnmt.tphcm.gov.vn/wms`
- **Status:** 404 Not Found
- **Tested:**
  - Direct GET: 404
  - WMS GetCapabilities 1.1.1: 404
  - WMS GetCapabilities 1.3.0: 404
- **Notes:** WMS endpoint may be at a different path or require authentication

#### HCMGIS GeoServer (WMS/WFS) - OFFLINE ✗
- **URL:** `https://hcmgis.vn/geoserver/wms` and `/wfs`
- **Status:** 404 Not Found
- **Notes:** HCMGIS GeoServer appears to be offline or relocated. The hcmgis.vn site returns 404 for all /geoserver paths.

#### Alternative HCMC Portals - OFFLINE ✗
- `https://stnmt.tphcm.gov.vn/wms` - DNS resolution failed
- `https://thongtinquyhoach.hochiminhcity.gov.vn/api` - 404
- `https://thongtinquyhoach.hochiminhcity.gov.vn/geoserver/*` - 404

---

### 2. Hanoi

#### Hanoi Planning Portal (WMS) - SSL ERROR ✗
- **URL:** `https://data.vqh.hanoi.gov.vn/wms`
- **Status:** SSL Certificate Verification Failed
- **Error:** Certificate hostname mismatch - certificate not valid for 'data.vqh.hanoi.gov.vn'
- **Notes:** Server likely uses a certificate for a different domain. Would require `--no-verify-ssl` equivalent, which is a security risk.

#### iQuyHoach Portal - TIMEOUT ✗
- **URL:** `https://iquyhoach.com/`
- **Status:** Connection timeout
- **Notes:** Portal unresponsive

---

## What Was Tested

### WMS/WFS Endpoints
- Direct `/wms` and `/wfs` paths
- GeoServer-specific paths (`/geoserver/wms`, `/geoserver/wfs`, `/geoserver/ows`)
- With and without version parameters (1.1.1, 1.3.0)
- GetCapabilities requests

### CSW Endpoint
- Successfully accessed CSW catalog
- Can retrieve metadata records
- Found dataset titles and identifiers
- Cannot download actual geospatial data

### Alternative Approaches
- WMTS tile services - 404
- CKAN API for open data portals - Inaccessible
- ArcGIS REST endpoints - Not found
- Direct tile URLs - 404

---

## Findings

### What Works
1. **HCMC CSW Catalog** - Metadata discovery only
2. **GADM** - Administrative boundaries (fallback)
3. **Local data files** - Thu Duc City data from previous imports

### What's Blocked
1. All WMS/WFS endpoints for direct data access
2. Open data CKAN APIs
3. Alternative portal APIs

### Root Causes
1. **Server misconfiguration** - WMS endpoints return 404, suggesting paths may have changed
2. **SSL certificate issues** - Hanoi portal has invalid certificate
3. **Service relocation** - HCMGIS appears offline
4. **Access restrictions** - Vietnam government data often requires official access

---

## Recommendations

### Immediate Actions
1. **Document the CSW metadata** - Extract and catalog what's available
2. **Update fetch scripts** - Reflect current status (offline/inaccessible)
3. **Use fallback sources** - GADM for administrative boundaries

### Short-term
1. **Manual data acquisition** - Request official planning data via government channels
2. **Academic partnership** - Partner with Vietnamese universities for data access
3. **QGIS HCMGIS plugin** - Examine source code for actual working endpoints
4. **Contact MONRE** - Ministry of Natural Resources and Environment for official access

### Long-term
1. **Build scraping pipeline** - For publicly viewable planning maps (with permission)
2. **Community contribution** - OpenStreetMap imports where legally allowed
3. **Alternative data sources** - Research commercial providers (e.g., Esri Vietnam, local GIS companies)

---

## Files Updated

1. `metadata/sources.json` - Added WMS testing results
2. `scripts/fetch_hcmgis.py` - Updated to reflect offline status
3. `scripts/fetch_hanoi.py` - Updated to reflect inaccessible status
4. `test_results.json` - Detailed endpoint test results
5. `test_wms_endpoints.py` - Testing script
6. `test_alternatives.py` - Alternative approach testing

---

## Appendix: CSW Catalog Sample

The working CSW endpoint (`https://geoportal-stnmt.tphcm.gov.vn/geonetwork/srv/eng/csw`) returns metadata records including:
- Dataset titles
- Identifiers (UUIDs)
- Abstracts
- Temporal/spatial extent
- Service links (which are typically the 404 WMS endpoints)

This confirms data exists but the actual geospatial services are not publicly accessible.

---

**End of Report**
