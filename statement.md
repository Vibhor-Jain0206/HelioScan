# HelioScan: Problem Statement & Engineering Specification

**Coursework Project:** Computer Vision (CS480 / Flipped Course Project)  
**Student Name:** Vibhor Jain  
**Registration Number:** 24BAI10742  
**Institution:** School of Computing Science and Engineering, VIT Bhopal University  
**System Name:** HelioScan (Aerial Photovoltaic Panel Defect Detection & IEC 62446-3 Degradation Severity Mapping)  

---

## 1. Background & Motivation
Utility-scale solar power generation is pivotal to global clean energy transitions. A typical 100 MW solar plant comprises over 250,000 photovoltaic modules spanning hundreds of hectares. Over operational lifespans exceeding 25 years, PV modules are constantly exposed to thermal cycling, UV radiation, hail impacts, mechanical vibrations, and dust accumulation.

These stressors induce various physical and electrical degradation modes:
1. **Thermal Hot-Spots:** High-resistance localized solder joints or internal short-circuits dissipate energy as intense heat instead of generating electricity, causing glass cracking and permanent module destruction.
2. **Silicon Micro-cracks:** Sub-millimeter hairline fractures that sever electrical fingers, reducing effective cell area and escalating into hotspots.
3. **Bypass Diode Failures:** Open or short-circuit failures in junction box diodes that take entire sub-module cell strings offline.
4. **Potential-Induced Degradation (PID):** High negative voltages relative to ground cause sodium ion migration from glass into silicon, resulting in massive output decay across entire panel strings.
5. **Soiling and Foreign Occlusion:** Avian droppings, dust crusting, and leaf debris that reduce irradiance and induce reverse-bias thermal stress.

Traditional inspection relies on manual handheld thermography surveys or sporadic walking patrols. This approach is slow, dangerous for field operators, prohibitively expensive, and subjective. Two human inspectors frequently score the exact same defective panel inconsistently.

**HelioScan** bridges this critical infrastructure gap through an automated, reproducible, headless Computer Vision pipeline. Designed to ingest aerial thermographic and RGB images captured from unmanned aerial vehicles (UAVs), HelioScan isolates individual solar modules, pinpoints defects with sub-pixel localization, computes an objective mathematical severity score ($0-100$), calculates an **IEC 62446-3 Module Degradation Index (MDI: $0-100$)**, and exports actionable maintenance telemetry without requiring a graphical desktop environment.

---

## 2. Project Objectives
1. **Multi-Class PV Anomaly Localization:** Accurately segment and identify five distinct solar defect classes: *Hotspot*, *Microcrack*, *PID*, *Soiling*, and *Diode_Failure*.
2. **Deterministic Severity Quantification:** Eliminate subjective visual estimation by applying an analytical equation combining defect area fraction, thermal differential ($\Delta T$), busbar electrical proximity, and category hazard weighting.
3. **Standards-Compliant Degradation Indexing:** Aggregate multi-defect telemetry into a global Module Degradation Index (MDI) structured upon the international **IEC 62446-3** standard for photovoltaic infrared thermography.
4. **Zero-GUI Headless Architecture:** Ensure the complete system operates reliably from terminal CLI environments on headless cloud instances and embedded drone companion computers (e.g., NVIDIA Jetson, Raspberry Pi) without X11/Wayland dependencies.
5. **Standardized Machine Telemetry:** Export annotated inspection images with HUD overlays alongside structured JSON telemetry and CSV engineering logs for seamless integration into enterprise SCADA and GIS asset databases.

---

## 3. Scope & System Boundaries
- **Input Modalities:** High-resolution 2D monocular RGB and radiometric/calibrated thermographic images (JPG, PNG) captured from UAV nadir or oblique perspectives.
- **Operating Conditions:** Daylight solar irradiance conditions ($> 600\,\text{W/m}^2$) aligned with IEC thermographic inspection standards.
- **Exclusions:** Real-time UAV flight path stabilization and motorized gimbal control (treated as upstream hardware sensor layers).

---

## 4. Target Users
- **Solar Farm Asset Operators:** Operations & Maintenance (O&M) teams conducting monthly drone inspections across utility-scale arrays.
- **Commercial Drone Inspection Pilots:** Professional UAV service providers delivering automated inspection analytics to infrastructure clients.
- **Asset Integrity & Warranty Engineers:** Quality assurance specialists verifying compliance against manufacturer degradation warranties.
- **SCADA Integration Engineers:** Renewable energy software engineers automating plant health monitoring pipelines.

---

## 5. High-Level System Features
- **Adaptive LAB-CLAHE Enhancement:** Compensates for varying solar angle, lens glare, and ambient haze.
- **Bilateral Edge-Preserving Denoising:** Eliminates sensor noise while preserving wafer boundary and micro-fracture gradients.
- **Multi-Class Morphological Defect Detector:** Combines directional morphological structuring kernels with adaptive intensity clustering.
- **Non-Maximum Suppression (NMS):** Eliminates redundant overlapping bounding boxes using IoU thresholding.
- **IEC 62446-3 Health Categorization:** Automatically maps MDI scores into four operational tiers: *Normal*, *Scheduled Maintenance*, *High Priority*, and *Critical Emergency Replacement*.
- **Comprehensive Headless HUD Overlay:** Embeds diagnostic thermal false-color mapping, corner-bracket bounding boxes, and performance telemetry directly onto images.
