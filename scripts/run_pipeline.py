"""
HelioScan Command-Line Interface (CLI) Entrypoint
Processes single images or entire batch directories headlessly without GUI dependencies.
"""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import PipelineConfig, DetectorConfig
from src.pipeline import HelioPipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="HelioScan: Automated Aerial PV Defect Detection & IEC 62446-3 Severity Mapping CLI"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", type=str, help="Path to a single inspection image file")
    group.add_argument("--batch", type=str, help="Path to a directory of images for batch inspection")

    parser.add_argument("--output", type=str, default="outputs", help="Directory to save HUD images, JSON, and CSV")
    parser.add_argument("--conf", type=float, default=0.30, help="Confidence threshold for defect detection (default: 0.30)")
    parser.add_argument("--format", type=str, default="json,csv,hud", help="Comma-separated output formats (default: json,csv,hud)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose console progress output")

    return parser.parse_args()


def print_banner():
    banner = """
========================================================================
 HELIOSCAN // Photovoltaic Defect Inspection & IEC 62446-3 Telemetry
 Author: Vibhor Jain | Reg: 24BAI10742 | VIT Bhopal University
========================================================================
    """
    print(banner)


def main():
    args = parse_args()

    if not args.quiet:
        print_banner()

    formats = [f.strip().lower() for f in args.format.split(",")]
    export_json = "json" in formats
    export_csv = "csv" in formats
    export_hud = "hud" in formats

    det_cfg = DetectorConfig(confidence_threshold=args.conf)
    cfg = PipelineConfig(
        detector=det_cfg,
        output_dir=args.output,
        export_json=export_json,
        export_csv=export_csv,
        export_hud=export_hud
    )

    pipeline = HelioPipeline(cfg)

    if args.image:
        if not args.quiet:
            print(f"[*] Processing single image: {args.image}")
        result = pipeline.process_image(args.image)
        if not args.quiet:
            print(f"[+] Complete in {result.execution_time_ms:.1f} ms")
            print(f"    - Module Degradation Index (MDI): {result.report.module_degradation_index:.1f}/100")
            print(f"    - Health Tier: {result.report.health_tier.value}")
            print(f"    - Defects Detected: {result.report.total_defects}")
            print(f"    - Est. Power Loss: {result.report.estimated_power_loss_pct:.1f}%")
            print(f"    - Triage Action: {result.report.recommended_action}")
            if result.hud_path:
                print(f"    - HUD Overlay saved: {result.hud_path}")
            if result.json_path:
                print(f"    - JSON Telemetry saved: {result.json_path}")
            if result.csv_path:
                print(f"    - CSV Defects saved: {result.csv_path}")

    elif args.batch:
        if not args.quiet:
            print(f"[*] Processing batch directory: {args.batch}")
        results = pipeline.process_batch(args.batch)
        if not args.quiet:
            print(f"[+] Processed {len(results)} images in batch.")
            print("=" * 80)
            print(f"{'IMAGE':<24} | {'MDI':<8} | {'TIER':<20} | {'DEFECTS':<8} | {'LATENCY (ms)':<10}")
            print("-" * 80)
            for r in results:
                tier_short = r.report.health_tier.value.split(":")[0]
                print(f"{r.image_name:<24} | {r.report.module_degradation_index:<8.1f} | {tier_short:<20} | {r.report.total_defects:<8} | {r.execution_time_ms:<10.1f}")
            print("=" * 80)
            print(f"[+] All results written to directory: {args.output}")


if __name__ == "__main__":
    main()
