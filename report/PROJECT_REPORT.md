# HelioScan: Complete Project Report Document
**Course:** Computer Vision (CS480 / Flipped Course Project, VIT Bhopal University)  
**Author:** Vibhor Jain | **Registration Number:** 24BAI10742  
**Repository:** https://github.com/Vibhor-Jain0206/HelioScan  
**Submission Date:** September 18, 2026  

---

## COVER PAGE DETAILS
- **Project Title:** HelioScan: Drone-Based Photovoltaic Panel Defect Detection & IEC 62446-3 Degradation Severity Mapping
- **Subtitle:** A Modular, Zero-GUI Headless Computer Vision Engineering System
- **Candidate Name:** Vibhor Jain
- **Registration Number:** 24BAI10742
- **Institution:** School of Computing Science and Engineering, VIT Bhopal University
- **Course:** Computer Vision (CS480 / Flipped Course)
- **Repository:** https://github.com/Vibhor-Jain0206/HelioScan
- **Submission Date:** September 18, 2026

---

## 1. INTRODUCTION
Utility-scale photovoltaic (PV) power systems represent the premier pillar of global clean energy transitions. A typical 100 MW solar plant occupies over 250 hectares and comprises upwards of 250,000 discrete photovoltaic modules. Over multi-decade operational lifecycles, PV modules endure continuous environmental exposure, including cyclic diurnal thermal stress, ultraviolet radiation embrittlement, mechanical hail impact, and atmospheric particulate soiling. 

These environmental stresses induce insidious physical wafer fractures, localized solder shunts (hotspots), sub-string bypass diode failures, and Potential-Induced Degradation (PID). Traditional operations and maintenance (O&M) protocols rely on manual handheld thermography surveys or walking patrols. Such manual approaches are hazardous to personnel in high-voltage fields, subjective, infrequent (often once every 2–3 years per string), and economically unsustainable.

HelioScan introduces a completely automated, headless Computer Vision pipeline engineered specifically for aerial thermographic and optical imagery captured by unmanned aerial vehicles (UAVs). The system isolates individual solar modules, pinpoints defects with sub-pixel localization, computes an objective mathematical severity score (0–100), calculates an IEC 62446-3 Module Degradation Index (MDI), and exports actionable maintenance telemetry without requiring an active graphical desktop server.

---

## 2. PROBLEM STATEMENT
Photovoltaic degradation modes substantially degrade solar array power output and, if uncorrected, induce catastrophic thermal runaway that poses serious fire hazards. Existing commercial computer vision inspection solutions suffer from three fundamental limitations:
1. **Rigid GUI Dependencies:** Most tools require interactive desktop environments, precluding autonomous execution on drone companion computers (e.g. NVIDIA Jetson) or headless cloud processing clusters.
2. **Subjective Heuristic Scoring:** Conventional scoring relies on arbitrary color thresholding without physical grounding in surface area, thermal differentials, or electrical busbar proximity.
3. **High False Positive Rates:** Normal structural cell grid lines and reflective metallic busbars frequently trigger false microcrack and soiling alarms, eroding operator trust.

HelioScan resolves this technical bottleneck by providing an automated, reproducible, and zero-GUI Computer Vision pipeline that suppresses structural wafer artifacts, computes physical defect severity ($S_i \in [0, 100]$), determines international standard condition ratings, and streams structured telemetry directly to utility SCADA systems.

---

## 3. FUNCTIONAL REQUIREMENTS
- **FR-1 (Ingestion & Preprocessing):** Ingests monocular BGR/thermal images, validates dimensional integrity ($\ge 32\times 32$), enhances contrast using LAB-color space CLAHE (L-channel clip limit 2.5), applies bilateral edge-preserving smoothing, and rectifies quadrilateral module perspective via homography.
- **FR-2 (Multi-Class Defect Detection):** Accurately detects and classifies five defect categories (Hotspots, Microcracks, PID, Soiling, Diode Failures) using adaptive thermal thresholding, directional morphological structuring, and Non-Maximum Suppression (NMS IoU = 0.40).
- **FR-3 (Deterministic Severity Formulation):** Computes physical severity scores ($S_i \in [0, 100]$) combining relative area fraction, calibrated temperature delta ($\Delta T$), and internal busbar electrical proximity.
- **FR-4 (IEC 62446-3 Degradation Indexing & Health Triage):** Aggregates multi-defect telemetry into a global Module Degradation Index (MDI: 0–100) and issues automated maintenance dispatch recommendations (Tiers 1 to 4).
- **FR-5 (Headless HUD Rendering & Multi-Format Telemetry Export):** Generates OpenCV visual overlays with high-tech corner brackets and telemetry banners headlessly, exporting structured JSON and CSV engineering records.

---

## 4. NON-FUNCTIONAL REQUIREMENTS
- **NFR-1 (Performance & Throughput):** Achieves high frame rates ($> 15$ FPS, $< 65$ ms per frame) on commodity multi-core CPUs without requiring dedicated GPU acceleration.
- **NFR-2 (Headless Operability):** Operates 100% headlessly via terminal command line without requiring X11, Wayland, or graphical window managers.
- **NFR-3 (Reliability & Robustness):** Enforces strict error boundaries with custom exception handling for corrupt files, out-of-bound coordinates, and malformed inputs.
- **NFR-4 (Maintainability & Testability):** Modular component architecture with 100% passing automated test suite (23 unit and integration tests) and strict PEP 8 compliance.

---

## 5. SYSTEM ARCHITECTURE
HelioScan is designed as a decoupled, five-stage sequential pipeline:
1. **Stage 1 - Ingestion & Preprocessing:** LAB CLAHE + Bilateral edge-preserving filtering + quadrilateral perspective homography.
2. **Stage 2 - Defect Detection:** Multi-channel morphology + thermal bloom segmentation + Non-Maximum Suppression (NMS).
3. **Stage 3 - Severity Engine:** Deterministic multi-factor mathematical formulation ($S_i \in [0, 100]$).
4. **Stage 4 - Health Analyzer:** IEC 62446-3 Module Degradation Index (MDI) + Health Tiers 1–4.
5. **Stage 5 - Headless HUD & Telemetry:** OpenCV HUD overlay generation + JSON and CSV telemetry export.

*(Figure 1: docs/architecture.png)*

---

## 6. DESIGN DIAGRAMS
- **Workflow Diagram:** Algorithmic Decision Tree & Error Handling *(docs/workflow.png)*
- **Sequence Diagram:** Inter-Module Execution Sequence *(docs/sequence.png)*
- **UML Use Case Diagram:** Roles for Drone Pilot, Plant Engineer, SCADA *(docs/use_case.png)*
- **Component Diagram:** Software Packages & Data Contracts *(docs/component.png)*

### Database / Telemetry Schema
| Field Name | Type | Format / Range | Description |
|:---|:---|:---|:---|
| image_stem | String | Alphanumeric | Unique inspection image identifier |
| defect_id | Integer | 1..N | Per-image enumerated defect index |
| category | Enum | DefectClass | Hotspot, Microcrack, Soiling, Diode_Failure |
| confidence | Float | 0.0 – 1.0 | Detection certainty score |
| bbox_[x,y,w,h] | Integer | Pixels | Defect localization coordinates |
| temp_delta_c | Float | °Celsius | Calibrated thermal differential ($\Delta T$) |
| severity_score | Float | 0.0 – 100.0 | Deterministic mathematical severity |
| module_mdi | Float | 0.0 – 100.0 | IEC 62446-3 Module Degradation Index |
| health_tier | Enum | Tier 1–4 | Operational maintenance dispatch tier |

---

## 7. DESIGN DECISIONS & RATIONALE
1. **CIELAB Color Space CLAHE vs. RGB Equalization:** RGB histogram equalization corrupts chromatic color balance and creates false thermal artifacts. Equalizing solely the Lightness ($L$) channel in CIELAB space enhances subtle thermal blooms while preserving color integrity.
2. **Bilateral Filtering vs. Gaussian Blur:** Gaussian smoothing destroys narrow wafer microcracks. Bilateral filtering preserves sharp spatial edge gradients while eliminating high-frequency sensor noise.
3. **1D Column Smoothing for Busbar Suppression:** Photovoltaic cells feature thin 1-pixel busbar ribbons that mimic diode failure heating spikes. 1D horizontal averaging across column means eliminates narrow 1-pixel spikes while capturing genuine sub-module heating bands.
4. **Zero-GUI Headless Architecture:** Eliminating GUI window dependencies ensures reliable deployment across drone companion computers (NVIDIA Jetson, Raspberry Pi) and headless cloud servers.

---

## 8. IMPLEMENTATION DETAILS & MATHEMATICAL FORMULATION
### A. Defect Severity Formulation ($S_i$)
$$S_i = \min\left(100.0, \, w_c \cdot \left(\alpha \cdot \frac{A_i}{A_{\text{cell}}} \cdot 100 + \beta \cdot \frac{\Delta T_i}{\Delta T_{\max}} \cdot 100 + \gamma \cdot P_{\text{busbar}}\right)\right)$$
- $w_c$: Hazard weight (Diode Failure: 1.50, PID: 1.40, Hotspot: 1.30, Microcrack: 1.15, Soiling: 0.85).
- $A_i / A_{\text{cell}}$: Relative defect area fraction (Weight $\alpha = 0.35$).
- $\Delta T_i / \Delta T_{\max}$: Calibrated thermal delta (Weight $\beta = 0.45$).
- $P_{\text{busbar}}$: Proximity to internal electrical busbars (Weight $\gamma = 0.20$).

### B. IEC 62446-3 Module Degradation Index (MDI)
$$\text{MDI} = \max\left(0.0, \, 100.0 - (0.60 \cdot \max(S_i) + 0.40 \cdot \overline{S_i}) \cdot (1 + 0.12 \cdot (N - 1))\right)$$
Estimated power loss: $P_{\text{loss}} = (100.0 - \text{MDI}) \cdot 0.68\,\%$.

### C. Operational Health Tiers
- **Tier 1: Optimal (MDI $\ge 85.0$):** Nominal condition. Continue routine UAV flights.
- **Tier 2: Degraded ($70.0 \le \text{MDI} < 85.0$):** Moderate degradation. Schedule washing/re-inspection within 30 days.
- **Tier 3: Compromised ($50.0 \le \text{MDI} < 70.0$):** High severity. Dispatch field technician to test bypass diodes.
- **Tier 4: Critical ($\text{MDI} < 50.0$):** Emergency. Immediate string isolation and panel replacement (Fire Risk).

---

## 9. EXPERIMENTAL BENCHMARK & RESULTS
### Detection Performance Summary
| Image Name | Ground Truth | Predicted | Precision | Recall | F1-Score | Latency (ms) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| clean_module_01.jpg | 0 | 0 | 1.000 | 1.000 | 1.000 | 225.4 |
| hotspot_01.jpg | 1 | 1 | 1.000 | 1.000 | 1.000 | 25.3 |
| hotspot_02.jpg | 2 | 2 | 1.000 | 1.000 | 1.000 | 25.9 |
| microcrack_01.jpg | 1 | 1 | 1.000 | 1.000 | 1.000 | 32.7 |
| soiling_01.jpg | 1 | 1 | 1.000 | 1.000 | 1.000 | 28.7 |
| diode_failure_01.jpg | 1 | 1 | 1.000 | 1.000 | 1.000 | 26.8 |
| **OVERALL SUMMARY** | **6** | **6** | **100.0%** | **100.0%** | **100.0%** | **60.8 ms avg** |

- **Mean Intersection over Union (IoU):** 0.759
- **Processing Latency:** 60.8 ms / frame (>16 FPS on CPU)

*(Figure: outputs/hotspot_01_hud.jpg and outputs/diode_failure_01_hud.jpg)*

---

## 10. TESTING APPROACH & QUALITY ASSURANCE
The test suite is automated via pytest, containing 25 comprehensive tests:
- `test_preprocessing.py` (7 tests): File loading, dimensions, CLAHE, bilateral filter, ROI extraction.
- `test_detector.py` (5 tests): Clean module zero false positives, hotspot, soiling, NMS deduplication.
- `test_severity.py` (3 tests): Mathematical severity bounds ($0 \le S_i \le 100$), weighting, tiers.
- `test_analyzer.py` (3 tests): Clean module MDI (100.0), degradation penalties, critical failure alarms.
- `test_metrics.py` (3 tests): Exact and partial IoU, Precision, Recall, F1 calculations.
- `test_pipeline.py` (4 tests): End-to-end single image, batch execution, error handling, and custom outputs.

**Test Execution Result:** `25 passed in 0.78s (100% test pass rate)`

---

## 11. CHALLENGES FACED & SOLUTIONS
1. **Busbar & Grid Line False Positives:** Addressed by implementing directional length filters that suppress straight continuous lines spanning cell boundaries.
2. **Aluminum Frame Glare:** Solved by cropping a 16-pixel internal margin before computing sub-string thermal column averages.
3. **Variable Ambient Irradiance:** Addressed by applying adaptive CLAHE contrast enhancement dynamically in perceptual CIELAB space.

---

## 12. LEARNINGS & KEY TAKEAWAYS
- Mastered advanced OpenCV morphological operations, color space transformations (CIELAB, HSV), and Non-Maximum Suppression.
- Gained hands-on experience translating international civil/electrical engineering standards (IEC 62446-3) into deterministic computer vision algorithms.
- Understood the practical necessity of zero-GUI headless system engineering for autonomous drone computing.

---

## 13. FUTURE ENHANCEMENTS
1. **Edge AI Acceleration:** Quantize backbones to TensorRT / ONNX for real-time onboard inference on NVIDIA Jetson Orin.
2. **3D Digital Twin GIS Integration:** Georeference detected panel anomalies into GPS-tagged aerial orthomosaics for automated robotic cleaning.
3. **Electroluminescence (EL) Modality:** Expand pipeline to support night-time aerial electroluminescence imaging for microscopic micro-crack detection.

---

## 14. REFERENCES
1. International Electrotechnical Commission, *IEC TS 62446-3: Photovoltaic systems - Part 3: Outdoor infrared thermography of modules and plants*, 2017.
2. Bradski, G., *The OpenCV Library*, Dr. Dobb's Journal of Software Tools, 2000.
3. Buerhop, C. et al., *Quality control of PV-modules in the field using infrared thermography*, Progress in Photovoltaics: Research and Applications, 2012.
4. ASTM International, *ASTM D6433: Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys*, 2020.
5. Akram, M. W. et al., *CNN based automatic detection of photovoltaic cell defects in electroluminescence images*, Energy, 2020.
