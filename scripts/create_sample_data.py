"""
Generates realistic synthetic aerial thermographic and optical solar panel imagery
with calibrated defects for benchmarking the HelioScan pipeline.
"""

from pathlib import Path
import json
import cv2
import numpy as np


def create_base_solar_panel(width: int = 640, height: int = 512) -> np.ndarray:
    """Generates baseline polycrystalline silicon panel with busbars and cell grid."""
    base = np.zeros((height, width, 3), dtype=np.uint8)
    base[:, :] = (85, 55, 30)

    noise = np.random.normal(0, 4, (height, width, 3)).astype(np.int16)
    panel = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    cv2.rectangle(panel, (0, 0), (width - 1, height - 1), (180, 180, 190), 8)
    cv2.rectangle(panel, (8, 8), (width - 9, height - 9), (40, 40, 45), 2)

    cell_w = (width - 24) // 10
    cell_h = (height - 24) // 6

    for c in range(11):
        x = 12 + c * cell_w
        cv2.line(panel, (x, 12), (x, height - 12), (30, 30, 35), 1)

    for r in range(7):
        y = 12 + r * cell_h
        cv2.line(panel, (12, y), (width - 12, y), (30, 30, 35), 1)

    for c in range(10):
        col_x = 12 + c * cell_w
        for bb in [0.25, 0.50, 0.75]:
            bx = int(col_x + bb * cell_w)
            cv2.line(panel, (bx, 14), (bx, height - 14), (175, 180, 190), 1)

    return panel


def generate_dataset(output_dir: str = "data/sample"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    annotations = []

    clean_img = create_base_solar_panel()
    clean_file = out_path / "clean_module_01.jpg"
    cv2.imwrite(str(clean_file), clean_img)
    annotations.append({
        "image_id": "clean_module_01.jpg",
        "width": 640,
        "height": 512,
        "defects": []
    })

    hotspot1 = create_base_solar_panel()
    cx, cy = 295, 230
    for radius in range(36, 0, -3):
        alpha = (36 - radius) / 36.0
        val_r = int(140 + 115 * alpha)
        val_g = int(50 + 90 * alpha)
        color = (20, val_g, val_r)
        cv2.circle(hotspot1, (cx, cy), radius, color, -1)
    cv2.circle(hotspot1, (cx, cy), 10, (255, 255, 255), -1)

    file_h1 = out_path / "hotspot_01.jpg"
    cv2.imwrite(str(file_h1), hotspot1)
    annotations.append({
        "image_id": "hotspot_01.jpg",
        "width": 640,
        "height": 512,
        "defects": [{
            "category": "Hotspot",
            "bbox": [262, 197, 66, 66],
            "area_pixels": 3420,
            "temp_delta_celsius": 28.4
        }]
    })

    hotspot2 = create_base_solar_panel()
    pts = [(160, 150, 32), (440, 320, 34)]
    h2_defects = []
    for (px, py, pr) in pts:
        for radius in range(pr, 0, -3):
            alpha = (pr - radius) / float(pr)
            val_r = int(140 + 115 * alpha)
            val_g = int(50 + 90 * alpha)
            color = (20, val_g, val_r)
            cv2.circle(hotspot2, (px, py), radius, color, -1)
        cv2.circle(hotspot2, (px, py), 9, (255, 255, 255), -1)
        h2_defects.append({
            "category": "Hotspot",
            "bbox": [px - pr, py - pr, pr * 2, pr * 2],
            "area_pixels": int(np.pi * pr * pr),
            "temp_delta_celsius": 24.2
        })
    file_h2 = out_path / "hotspot_02.jpg"
    cv2.imwrite(str(file_h2), hotspot2)
    annotations.append({
        "image_id": "hotspot_02.jpg",
        "width": 640,
        "height": 512,
        "defects": h2_defects
    })

    crack_img = create_base_solar_panel()
    branch_pts = [
        [(210, 180), (235, 205), (245, 240), (275, 265), (290, 310)],
        [(245, 240), (270, 230), (300, 225)],
        [(275, 265), (280, 290), (310, 305)]
    ]
    for branch in branch_pts:
        for i in range(len(branch) - 1):
            cv2.line(crack_img, branch[i], branch[i+1], (10, 10, 12), 2)
            cv2.line(crack_img, branch[i], branch[i+1], (5, 5, 8), 1)

    file_cr = out_path / "microcrack_01.jpg"
    cv2.imwrite(str(file_cr), crack_img)
    annotations.append({
        "image_id": "microcrack_01.jpg",
        "width": 640,
        "height": 512,
        "defects": [{
            "category": "Microcrack",
            "bbox": [205, 175, 110, 140],
            "area_pixels": 2840,
            "temp_delta_celsius": 4.5
        }]
    })

    soiling_img = create_base_solar_panel()
    dirt_pts = np.array([[330, 200], [390, 190], [420, 240], [385, 275], [340, 260], [315, 225]])
    cv2.fillPoly(soiling_img, [dirt_pts], (45, 95, 120))
    for _ in range(40):
        rx = np.random.randint(320, 415)
        ry = np.random.randint(195, 270)
        rr = np.random.randint(2, 6)
        cv2.circle(soiling_img, (rx, ry), rr, (40, 85, 110), -1)

    file_soil = out_path / "soiling_01.jpg"
    cv2.imwrite(str(file_soil), soiling_img)
    annotations.append({
        "image_id": "soiling_01.jpg",
        "width": 640,
        "height": 512,
        "defects": [{
            "category": "Soiling",
            "bbox": [315, 190, 110, 90],
            "area_pixels": 7200,
            "temp_delta_celsius": 6.0
        }]
    })

    diode_img = create_base_solar_panel()
    sub_band = diode_img[14:498, 205:395].astype(np.int16)
    sub_band[:, :, 2] = np.clip(sub_band[:, :, 2] + 160, 0, 255)
    sub_band[:, :, 1] = np.clip(sub_band[:, :, 1] + 90, 0, 255)
    diode_img[14:498, 205:395] = sub_band.astype(np.uint8)

    file_diode = out_path / "diode_failure_01.jpg"
    cv2.imwrite(str(file_diode), diode_img)
    annotations.append({
        "image_id": "diode_failure_01.jpg",
        "width": 640,
        "height": 512,
        "defects": [{
            "category": "Diode_Failure",
            "bbox": [205, 14, 190, 484],
            "area_pixels": 91960,
            "temp_delta_celsius": 38.5
        }]
    })

    anno_file = out_path / "annotations.json"
    with open(anno_file, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2)

    print(f"Generated 6 calibrated benchmark images and annotations.json at: {out_path}")


if __name__ == "__main__":
    generate_dataset()
