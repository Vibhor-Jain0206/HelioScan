"""
Benchmark evaluation script assessing HelioScan against ground-truth annotations.
Calculates Precision, Recall, F1-Score, mean IoU, and inference latency.
"""

import argparse
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import PipelineConfig
from src.pipeline import HelioPipeline
from src.metrics import evaluate_detections


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate HelioScan on annotated benchmark dataset")
    parser.add_argument("--data", type=str, default="data/sample", help="Directory containing sample images & annotations.json")
    parser.add_argument("--output", type=str, default="outputs/benchmark_results.json", help="Path to save evaluation summary JSON")
    parser.add_argument("--iou", type=float, default=0.40, help="IoU match threshold (default: 0.40)")
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = Path(args.data)
    anno_file = data_dir / "annotations.json"

    if not anno_file.exists():
        print(f"[-] Ground-truth annotation file not found: {anno_file}")
        sys.exit(1)

    with open(anno_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    cfg = PipelineConfig(export_hud=False, export_json=False, export_csv=False)
    pipeline = HelioPipeline(cfg)

    all_gt_count = 0
    all_pred_count = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    ious = []
    latencies = []

    print("=" * 82)
    print(" HELIOSCAN BENCHMARK EVALUATION // GROUND-TRUTH VALIDATION")
    print("=" * 82)
    print(f"{'IMAGE':<22} | {'GT':<4} | {'PRED':<4} | {'PRECISION':<10} | {'RECALL':<8} | {'F1':<8} | {'TIME(ms)':<8}")
    print("-" * 82)

    image_results = []

    for entry in ground_truth:
        img_name = entry["image_id"]
        gt_defects = entry["defects"]
        img_path = data_dir / img_name

        if not img_path.exists():
            continue

        t0 = time.perf_counter()
        res = pipeline.process_image(str(img_path))
        latency = (time.perf_counter() - t0) * 1000.0
        latencies.append(latency)

        preds = [s.defect for s in res.report.severities]

        metrics = evaluate_detections(gt_defects, preds, iou_thresh=args.iou)
        all_gt_count += len(gt_defects)
        all_pred_count += len(preds)
        total_tp += metrics["tp"]
        total_fp += metrics["fp"]
        total_fn += metrics["fn"]
        if metrics["mean_iou"] > 0:
            ious.append(metrics["mean_iou"])

        print(f"{img_name:<22} | {len(gt_defects):<4} | {len(preds):<4} | {metrics['precision']:<10.3f} | {metrics['recall']:<8.3f} | {metrics['f1']:<8.3f} | {latency:<8.1f}")

        image_results.append({
            "image": img_name,
            "ground_truth_count": len(gt_defects),
            "predicted_count": len(preds),
            "metrics": metrics,
            "latency_ms": round(latency, 2)
        })

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
    mean_iou = sum(ious) / len(ious) if ious else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    fps = 1000.0 / avg_latency if avg_latency > 0 else 0.0

    print("=" * 82)
    print(" OVERALL BENCHMARK PERFORMANCE METRICS")
    print("=" * 82)
    print(f" Total Ground-Truth Defects: {all_gt_count}")
    print(f" Total Predicted Defects:    {all_pred_count}")
    print(f" True Positives (TP):        {total_tp}")
    print(f" False Positives (FP):       {total_fp}")
    print(f" False Negatives (FN):       {total_fn}")
    print(f" Global Precision:           {overall_precision * 100:.2f}%")
    print(f" Global Recall:              {overall_recall * 100:.2f}%")
    print(f" Global F1-Score:            {overall_f1 * 100:.2f}%")
    print(f" Mean IoU:                   {mean_iou:.3f}")
    print(f" Average Latency:            {avg_latency:.2f} ms / frame ({fps:.1f} FPS on CPU)")
    print("=" * 82)

    summary = {
        "benchmark_summary": {
            "total_images": len(ground_truth),
            "total_gt_defects": all_gt_count,
            "total_predictions": all_pred_count,
            "true_positives": total_tp,
            "false_positives": total_fp,
            "false_negatives": total_fn,
            "precision": round(overall_precision, 4),
            "recall": round(overall_recall, 4),
            "f1_score": round(overall_f1, 4),
            "mean_iou": round(mean_iou, 4),
            "average_latency_ms": round(avg_latency, 2),
            "frames_per_second": round(fps, 1)
        },
        "per_image_results": image_results
    }

    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[+] Benchmark summary saved to: {out_file}")


if __name__ == "__main__":
    main()
