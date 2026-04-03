# Vietnam Urban Planning Database

A comprehensive database of Vietnam's urban planning and administrative boundary data, with focus on major cities and planning zones.

## 🎯 Goal

Create a centralized, open-source repository for Vietnam urban planning data including:
- Full administrative boundaries (country, provinces, districts, wards)
- Planning zone data (quy hoạch phân khu) where accessible
- Road red-line data (chỉ giới đường đỏ) where available
- ETL scripts for data harvesting and updates

## 📁 Repository Structure

```
vietnam-urban-planning-db/
├── data/
│   ├── administrative/          # National admin boundaries
│   │   ├── provinces.geojson  # 63 provinces
│   │   ├── districts.geojson  # 710 districts
│   │   └── wards.geojson      # ~11,000 wards/communes
│   ├── ho-chi-minh-city/      # HCMC specific data
│   ├── hanoi/                 # Hanoi specific data
│   ├── haiphong/              # Hai Phong data
│   ├── da-nang/               # Da Nang data
│   ├── binh-duong/            # Binh Duong data
│   ├── vung-tau/              # Vung Tau data
│   ├── can-tho/               # Can Tho data
│   └── phu-quoc/              # Phu Quoc data
├── scripts/
│   ├── fetch_boundaries.py    # Download admin boundaries
│   ├── fetch_hcmgis.py        # HCMC specific fetcher
│   ├── fetch_hanoi.py         # Hanoi specific fetcher
│   ├── fetch_other_cities.py  # Other cities fetcher
│   └── sync_all.py            # Master sync script
├── metadata/
│   └── sources.json             # Data sources metadata
├── README.md
└── CONTRIBUTING.md
```

## 🗺️ Data Coverage

### Administrative Boundaries

| Level | Count | Source | Status |
|-------|-------|--------|--------|
| Country | 1 | GADM 4.1 | ✓ Available |
| Provinces | 63 | GADM 4.1 | ✓ Available |
| Districts | 710 | GADM 4.1 | ✓ Available |
| Wards | ~11,000 | GADM 4.1 | ✓ Available |

### Cities Coverage

| City | Administrative | Planning Zones | Notes |
|------|---------------|----------------|-------|
| **Ho Chi Minh City** | ✓ Thu Duc data | ⚠️ Portal access limited | HCMGIS WFS requires auth |
| **Hanoi** | ✓ 30 districts | ⚠️ VQH Portal SSL error | iQuyHoach portal accessible |
| **Hai Phong** | ✓ 15 districts | ❌ Not available | Need to explore local sources |
| **Da Nang** | ✓ 7 districts | ⚠️ Portal not tested | Open Data portal exists |
| **Binh Duong** | ✓ 9 districts | ❌ Not available | Major industrial hub |
| **Can Tho** | ✓ 9 districts | ⚠️ Portal not tested | Mekong Delta hub |
| **Vung Tau** | ✓ 7 districts | ❌ Not available | Coastal/oil & gas city |
| **Phu Quoc** | ✓ (Kiên Giang) | ❌ Not available | Island SEZ |

## 🚀 Quick Start

### Prerequisites

```bash
pip install requests geopandas
```

### Download All Data

```bash
# Run individual fetch scripts
python scripts/fetch_boundaries.py    # Admin boundaries
python scripts/fetch_hcmgis.py        # HCMC data
python scripts/fetch_hanoi.py         # Hanoi data
python scripts/fetch_other_cities.py  # Other cities

# Or run everything
python scripts/sync_all.py
```

### Using the Data

```python
import geopandas as gpd

# Load provinces
provinces = gpd.read_file('data/administrative/provinces.geojson')
print(f"Loaded {len(provinces)} provinces")

# Load HCMC Thu Duc data
thuduc = gpd.read_file('data/ho-chi-minh-city/ThuDucCity_boundary.geojson')
```

## 📊 Data Sources

### Primary Sources

1. **GADM (Global Administrative Areas)** - https://gadm.org
   - Version 4.1
   - License: Free for academic/non-commercial use
   - Coverage: Complete Vietnam admin boundaries

2. **HCMGIS Portal** - https://hcmgis.vn/
   - Official HCMC GIS platform
   - Status: WFS requires authentication
   - Contains: Planning zones, roads, land use

3. **adminvsrm/GISData** - https://github.com/adminvsrm/GISData
   - Community-contributed Vietnam GIS data
   - Includes: Thu Duc City data, pre/post 2025 boundaries

### Secondary Sources

- **Hanoi VQH Portal**: https://data.vqh.hanoi.gov.vn/ (SSL issues)
- **iQuyHoach**: https://iquyhoach.com/ (Accessible)
- **HCMC Open Data**: https://opendata.hochiminhcity.gov.vn/ (Timeout issues)

## 📝 Known Gaps & Limitations

### Planning Data Accessibility

Most Vietnamese government GIS portals have the following challenges:

1. **Authentication Required**: Many WFS/WMS services need API keys
2. **Network Restrictions**: Some portals only accessible from Vietnam IPs
3. **SSL/Certificate Issues**: Some official portals have misconfigured certificates
4. **Data Format**: Planning data often in proprietary formats (AutoCAD, local GIS software)

### What's Missing

- Detailed planning zones (quy hoạch phân khu) for most cities
- Road red-line data (chỉ giới đường đỏ)
- Land use planning maps
- Detailed urban development plans

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas

1. **HCMC**: Access HCMGIS with proper credentials
2. **Hanoi**: Resolve VQH portal SSL issues
3. **Other Cities**: Find and document local GIS portals
4. **Planning Data**: Convert CAD files to GeoJSON where possible

## 📄 License

- **GADM Data**: Free for academic and non-commercial use
- **Repository Scripts**: MIT License
- **Contributed Data**: See individual file metadata

## 🔗 Related Resources

- [GADM](https://gadm.org) - Global Administrative Areas
- [HCMGIS](https://hcmgis.vn/) - HCMC GIS Portal
- [Vietnam GIS Community](https://github.com/adminvsrm/GISData)

## 📞 Contact

For questions or data contributions, please open an issue or pull request.

---

**Note**: This is a community-driven project. Official government data may have restrictions. Always verify licensing for your specific use case.
