# Contributing to Vietnam Urban Planning Database

Thank you for your interest in contributing! This document provides guidelines for contributing data, code, and documentation.

## 🎯 How to Contribute

### 1. Data Contributions

We welcome data contributions for:
- Administrative boundary updates
- Planning zone data (quy hoạch phân khu)
- Road red-line data (chỉ giới đường đỏ)
- Official open data from Vietnamese government portals

#### Data Requirements

- **Format**: GeoJSON (preferred), Shapefile, KML
- **Coordinate System**: WGS84 (EPSG:4326) preferred
- **Metadata**: Include source, date, and license information
- **Quality**: Data should be from official or verified sources

#### Data Submission Process

1. **Verify the data source** - ensure it's from an official or reliable source
2. **Check licensing** - confirm the data can be redistributed
3. **Convert to GeoJSON** if needed:
   ```bash
   ogr2ogr -f GeoJSON output.geojson input.shp
   ```
4. **Add metadata** - create/update `metadata.json` in the relevant directory
5. **Submit via Pull Request** with description of the data source

### 2. Code Contributions

#### Adding New Fetch Scripts

When adding a fetch script for a new city or data source:

1. Create a new script in `scripts/` directory
2. Follow the existing script structure:
   - Use Python 3 with standard libraries
   - Include error handling for network issues
   - Save data to appropriate `data/` subdirectory
   - Generate `metadata.json` for the fetched data
3. Update `scripts/sync_all.py` if adding a new city
4. Document the data source in `metadata/sources.json`

#### Script Template

```python
#!/usr/bin/env python3
"""
Fetch [City] GIS data.
Source: [URL]
"""

import json
import requests
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "[city-code]"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_data():
    """Fetch data from source."""
    # Your fetch logic here
    pass

def main():
    print(f"Fetching [City] data...")
    # Implementation
    
    # Save metadata
    metadata = {
        "city": "[City Name]",
        "source": "[Source URL]",
        "last_updated": datetime.now().isoformat()
    }
    with open(DATA_DIR / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    main()
```

### 3. Documentation Contributions

- Fix typos in README or metadata
- Add usage examples
- Improve data source documentation
- Translate documentation to Vietnamese

## 📋 Contribution Checklist

Before submitting a pull request:

- [ ] Data is from a reliable source
- [ ] License allows redistribution
- [ ] GeoJSON files are valid (test with `ogrinfo` or `geopandas`)
- [ ] Metadata is included
- [ ] Code follows existing style
- [ ] No sensitive or private data included
- [ ] README updated if adding new cities/features

## 🔍 Data Verification

### Check GeoJSON Validity

```python
import geopandas as gpd

# Load and verify
gdf = gpd.read_file('data/city/file.geojson')
print(f"CRS: {gdf.crs}")
print(f"Features: {len(gdf)}")
print(f"Columns: {list(gdf.columns)}")
```

### Check for Duplicates

```bash
# Check if file already exists
find data/ -name "*.geojson" -exec basename {} \; | sort | uniq -d
```

## 🐛 Reporting Issues

When reporting data issues:

1. **Data Error**: Include specific feature ID and expected correction
2. **Missing Data**: Describe what data is needed and potential source
3. **Source Broken**: Report if a fetch script fails due to source changes

Template:
```
**Issue Type**: [Data Error / Missing Data / Source Broken]
**Location**: [File or City]
**Description**: 
**Expected**: 
**Actual**: 
**Source**: [If applicable]
```

## 🗣️ Vietnamese Data Sources

### Government Portals

Many Vietnamese government portals use these patterns:
- `[city].gov.vn` - Official city portals
- `data.[city].gov.vn` - Open data portals
- `hcmgis.vn` - HCMC specific
- `iquyhoach.com` - Hanoi planning

### Common Challenges

1. **Authentication**: Many require API keys or login
2. **Vietnamese Encoding**: Ensure UTF-8 is used throughout
3. **VN-2000 Projection**: Official data may use Vietnam's local CRS (EPSG:9210)

### Converting VN-2000 to WGS84

```python
import geopandas as gpd

# Read VN-2000 data
gdf = gpd.read_file('input.shp')

# Convert to WGS84
gdf_wgs84 = gdf.to_crs(epsg=4326)

# Save
gdf_wgs84.to_file('output.geojson', driver='GeoJSON')
```

## 📊 Data Standards

### Required Metadata Fields

```json
{
  "city": "City Name",
  "name_vn": "Vietnamese Name",
  "data_type": "administrative|planning|infrastructure",
  "source": "URL or organization",
  "license": "License type",
  "last_updated": "ISO 8601 date",
  "crs": "EPSG:4326",
  "features_count": 0
}
```

### File Naming Convention

- `{city}_{layer}_{source}.geojson`
- Examples:
  - `hanoi_districts_gadm.geojson`
  - `hochiminh_roads_osm.geojson`
  - `danang_planning_official.geojson`

## 🙏 Acknowledgments

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Release notes
- Repository README

## 📧 Contact

- Open an issue for questions
- Tag with appropriate labels (data-request, bug, enhancement)

---

**Note**: By contributing, you agree that your contributions will be licensed under the same license as the project.
