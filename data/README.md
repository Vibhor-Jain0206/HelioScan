# HelioScan Dataset & Sample Data Specification

This directory contains benchmark and synthetic evaluation datasets for validating the HelioScan photovoltaic defect detection pipeline.

## 1. Defect Taxonomy

The dataset captures five critical defect classes commonly encountered during aerial thermographic and optical unmanned aerial vehicle (UAV) solar farm surveys:

| Class ID | Class Name | Physical Origin | Visual Characteristics | Severity Weight ($w_c$) |
|:---|:---|:---|:---|:---:|
| 0 | `Hotspot` | Localized cell shunt / localized short circuit | High-temperature thermal radiant bloom ($\Delta T > 15^\circ\text{C}$) | 1.30 |
| 1 | `Microcrack` | Mechanical stress / hail impact / thermal cycling | Hairline fractures propagating across silicon wafer grain | 1.15 |
| 2 | `PID` | High system voltage potential leakage | String-wide cell gradient darkening and thermal elevation | 1.40 |
| 3 | `Soiling` | Dust deposition, bird droppings, foliage shade | Localized optical attenuation and diffuse heating patterns | 0.85 |
| 4 | `Diode_Failure`| Junction box bypass diode open/short circuit | Full 1/3 or 2/3 module sub-string thermal band heating | 1.50 |

## 2. Directory Layout

```
data/
├── README.md
└── sample/
    ├── clean_module_01.jpg       # Baseline defect-free polycrystalline PV module
    ├── hotspot_01.jpg            # Single cell localized thermal hotspot
    ├── hotspot_02.jpg            # Multi-cell severe thermal hotspot cluster
    ├── microcrack_01.jpg         # Propagating branching micro-fractures
    ├── soiling_01.jpg            # Localized avian soiling & dirt cluster
    ├── diode_failure_01.jpg      # Open bypass diode ribbon heating
    └── annotations.json          # COCO-style ground-truth bounding boxes and classifications
```

## 3. Ground Truth Annotation Schema

Annotations in `annotations.json` conform to standard computer vision benchmark formats:

```json
{
  "image_id": "hotspot_01.jpg",
  "width": 640,
  "height": 512,
  "defects": [
    {
      "category": "Hotspot",
      "bbox": [260, 190, 85, 80],
      "area_pixels": 6800,
      "temp_delta_celsius": 24.5,
      "severity_score": 72.4
    }
  ]
}
```
