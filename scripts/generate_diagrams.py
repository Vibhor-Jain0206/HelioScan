"""
Generates high-resolution vector and raster architecture and UML diagrams
(Architecture, Workflow, Sequence, Use Case, Component) in docs/ using Matplotlib.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def setup_canvas(width=12, height=7, title=""):
    fig, ax = plt.subplots(figsize=(width, height), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#0f111a")
    ax.set_facecolor("#0f111a")
    if title:
        ax.text(50, 95, title, color="#00e5ff", fontsize=16, fontweight="bold",
                ha="center", va="center", family="sans-serif")
    return fig, ax


def draw_box(ax, x, y, w, h, title, subtitle="", bg="#1c2030", border="#00e5ff", text_color="#ffffff"):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.5,rounding_size=1.5",
        facecolor=bg, edgecolor=border, linewidth=1.8
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h * 0.62, title, color=text_color, fontsize=10.5,
            fontweight="bold", ha="center", va="center", family="sans-serif")
    if subtitle:
        ax.text(x + w / 2, y + h * 0.32, subtitle, color="#9ea7b8", fontsize=8.5,
                ha="center", va="center", family="sans-serif")


def draw_arrow(ax, x1, y1, x2, y2, color="#00e5ff", label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=1.8, shrinkA=3, shrinkB=3)
    )
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 2, label, color="#ccd6f6",
                fontsize=8.5, ha="center", va="bottom", family="sans-serif")


def generate_architecture_diagram(out_file: str):
    fig, ax = setup_canvas(14, 8, "HelioScan: End-to-End System Architecture (IEC 62446-3)")

    draw_box(ax, 3, 40, 15, 20, "1. Ingestion & Preproc", "LAB CLAHE + Bilateral\nROI Rectification", "#171c2b", "#38ef7d")
    draw_box(ax, 22, 40, 15, 20, "2. Defect Detection", "Multi-class Morphology\nThermal Anomaly + NMS", "#171c2b", "#00d2ff")
    draw_box(ax, 41, 40, 15, 20, "3. Severity Engine", "Area % + ΔT + Busbar\nDeterministic S_i [0-100]", "#171c2b", "#ff9900")
    draw_box(ax, 60, 40, 16, 20, "4. Health Analyzer", "IEC 62446-3 MDI\nTier 1-4 Action Dispatch", "#171c2b", "#ff416c")
    draw_box(ax, 80, 40, 17, 20, "5. Visual & Telemetry", "Headless OpenCV HUD\nJSON + CSV SCADA Export", "#171c2b", "#a18cd1")

    draw_arrow(ax, 18, 50, 22, 50)
    draw_arrow(ax, 37, 50, 41, 50)
    draw_arrow(ax, 56, 50, 60, 50)
    draw_arrow(ax, 76, 50, 80, 50)

    draw_box(ax, 3, 72, 15, 12, "UAV Aerial Drone", "Thermal IR & Optical RGB", "#10141f", "#4facfe")
    draw_arrow(ax, 10.5, 72, 10.5, 60, label="Raw Image")

    draw_box(ax, 72, 12, 12, 14, "JSON Telemetry", "SCADA API Stream", "#10141f", "#38ef7d")
    draw_box(ax, 86, 12, 12, 14, "CSV Audit Log", "Maintenance Records", "#10141f", "#ff9900")
    draw_arrow(ax, 88.5, 40, 78, 26)
    draw_arrow(ax, 88.5, 40, 92, 26)

    ax.text(50, 6, "Standards Compliance: IEC 62446-3 Photovoltaic Thermography | Zero-GUI Headless Architecture",
            color="#6b7c96", fontsize=9.5, ha="center", va="center")

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def generate_workflow_diagram(out_file: str):
    fig, ax = setup_canvas(12, 8, "HelioScan: Process Flow & Decision Pipeline")

    draw_box(ax, 38, 82, 24, 9, "Start Ingestion", "Read Image Path / Batch", "#171c2b", "#38ef7d")
    draw_box(ax, 38, 68, 24, 9, "Validate Integrity", "Check dimensions >= 32px", "#171c2b", "#00d2ff")
    draw_box(ax, 38, 54, 24, 9, "LAB CLAHE & Denoise", "L-channel equalization", "#171c2b", "#00d2ff")
    draw_box(ax, 38, 40, 24, 9, "Multi-Channel Anomaly", "Thermal + Microcrack + Soil", "#171c2b", "#ff9900")
    draw_box(ax, 38, 26, 24, 9, "Calculate MDI & Tiers", "IEC 62446-3 Algorithm", "#171c2b", "#ff416c")
    draw_box(ax, 38, 12, 24, 9, "Export Headless HUD", "Save JPG, JSON, CSV", "#171c2b", "#a18cd1")

    draw_arrow(ax, 50, 82, 50, 77)
    draw_arrow(ax, 50, 68, 50, 63)
    draw_arrow(ax, 50, 54, 50, 49)
    draw_arrow(ax, 50, 40, 50, 35)
    draw_arrow(ax, 50, 26, 50, 21)

    draw_box(ax, 74, 68, 20, 9, "Reject & Log Error", "Corrupt File Exception", "#2c151f", "#ff4b2b")
    draw_arrow(ax, 62, 72.5, 74, 72.5, color="#ff4b2b", label="Invalid")

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def generate_sequence_diagram(out_file: str):
    fig, ax = setup_canvas(13, 8, "HelioScan: Execution Sequence Diagram")

    actors = ["CLI / User", "HelioPipeline", "Preprocessor", "Detector", "SeverityEngine", "IECAnalyzer", "Visualizer"]
    xs = [8, 22, 36, 50, 64, 78, 92]

    for x, act in zip(xs, actors):
        ax.text(x, 88, act, color="#00e5ff", fontsize=9.5, fontweight="bold", ha="center")
        ax.plot([x, x], [12, 85], color="#252b40", linestyle="--", lw=1.2)

    calls = [
        (8, 22, 78, "run_pipeline.py --image", "#38ef7d"),
        (22, 36, 70, "load_and_validate()", "#00d2ff"),
        (36, 22, 64, "preprocessed_bgr", "#6b7c96"),
        (22, 50, 56, "detect(image)", "#00d2ff"),
        (50, 22, 50, "List[DefectDetection]", "#6b7c96"),
        (22, 64, 44, "evaluate_all()", "#ff9900"),
        (64, 22, 38, "List[DefectSeverity]", "#6b7c96"),
        (22, 78, 32, "analyze(severities)", "#ff416c"),
        (78, 22, 26, "ModuleHealthReport", "#6b7c96"),
        (22, 92, 20, "draw_hud() & export", "#a18cd1"),
        (22, 8, 14, "InspectionResult (JSON/CSV)", "#38ef7d")
    ]

    for x1, x2, y, label, color in calls:
        draw_arrow(ax, x1, y, x2, y, color=color, label=label)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def generate_use_case_diagram(out_file: str):
    fig, ax = setup_canvas(12, 8, "HelioScan: UML Use Case Diagram")

    ax.text(12, 65, "Drone Pilot\n(UAV Operator)", color="#38ef7d", fontsize=11, fontweight="bold", ha="center")
    ax.text(12, 28, "Solar Plant\nO&M Engineer", color="#00e5ff", fontsize=11, fontweight="bold", ha="center")

    rect = patches.FancyBboxPatch((28, 10), 66, 75, boxstyle="round,pad=1.0", facecolor="#141824", edgecolor="#3f4a65")
    ax.add_patch(rect)
    ax.text(61, 81, "HelioScan Core System Boundary", color="#a0aec0", fontsize=10, fontweight="bold", ha="center")

    use_cases = [
        (48, 70, "Batch Ingest Drone Imagery"),
        (74, 70, "Perspective Rectification"),
        (48, 50, "Automated Defect Localization"),
        (74, 50, "IEC 62446-3 Severity Scoring"),
        (48, 30, "Render Diagnostic HUD"),
        (74, 30, "Generate Maintenance Triage"),
        (61, 16, "Export Telemetry to SCADA")
    ]

    for ux, uy, utitle in use_cases:
        ellipse = patches.Ellipse((ux, uy), 22, 9, facecolor="#1f2639", edgecolor="#00e5ff", lw=1.4)
        ax.add_patch(ellipse)
        ax.text(ux, uy, utitle, color="#ffffff", fontsize=8.5, ha="center", va="center")

    for ux, uy in [(48, 70), (74, 70), (48, 50)]:
        ax.plot([18, ux - 11], [65, uy], color="#38ef7d", alpha=0.6, lw=1.2)

    for ux, uy in [(48, 50), (74, 50), (48, 30), (74, 30), (61, 16)]:
        ax.plot([18, ux - 11], [28, uy], color="#00e5ff", alpha=0.6, lw=1.2)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def generate_component_diagram(out_file: str):
    fig, ax = setup_canvas(13, 8, "HelioScan: Software Component & Data Flow Architecture")

    draw_box(ax, 5, 55, 25, 25, "Package: src.preprocessing", "PreprocessingEngine\n- apply_clahe_lab()\n- apply_bilateral_filter()\n- extract_module_roi()", "#171c2b", "#38ef7d")
    draw_box(ax, 37, 55, 25, 25, "Package: src.detector", "SolarDefectDetector\n- detect()\n- _detect_thermal_anomalies()\n- _detect_microcracks()\n- apply_nms()", "#171c2b", "#00d2ff")
    draw_box(ax, 70, 55, 25, 25, "Package: src.severity", "SeverityEngine\n- evaluate()\n- evaluate_all()\n- Mathematical S_i Formulation", "#171c2b", "#ff9900")

    draw_box(ax, 20, 15, 27, 25, "Package: src.analyzer", "IECHealthAnalyzer\n- analyze()\n- Module Degradation Index (MDI)\n- HealthTier Classification", "#171c2b", "#ff416c")
    draw_box(ax, 55, 15, 27, 25, "Package: src.visualization", "Visualizer\n- draw_hud()\n- _draw_defect_box()\n- _draw_telemetry_banner()", "#171c2b", "#a18cd1")

    draw_arrow(ax, 30, 67.5, 37, 67.5, label="Clean BGR")
    draw_arrow(ax, 62, 67.5, 70, 67.5, label="Detections")
    draw_arrow(ax, 82.5, 55, 47, 35, label="DefectSeverity")
    draw_arrow(ax, 47, 27.5, 55, 27.5, label="HealthReport")

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def generate_all_diagrams(out_dir: str = "docs"):
    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    print("Generating system architecture diagram...")
    generate_architecture_diagram(str(out_p / "architecture.png"))

    print("Generating workflow diagram...")
    generate_workflow_diagram(str(out_p / "workflow.png"))

    print("Generating sequence diagram...")
    generate_sequence_diagram(str(out_p / "sequence.png"))

    print("Generating use case diagram...")
    generate_use_case_diagram(str(out_p / "use_case.png"))

    print("Generating component diagram...")
    generate_component_diagram(str(out_p / "component.png"))

    print(f"All 5 design diagrams successfully created in: {out_p}")


if __name__ == "__main__":
    generate_all_diagrams()
