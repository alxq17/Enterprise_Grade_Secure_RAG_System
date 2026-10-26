import os
import glob
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from tabulate import tabulate
from src.core.logging import app_logger


class EvaluationReporter:
    """
    Evaluation Reporter:
    - Exports detailed per-query evaluation data to CSV
    - Exports summary metrics (Recall, MRR, Faithfulness, Relevance)
    - Automatically discovers prior baseline to detect quality regressions (> 5% drop)
    - Formats reports into terminal tables
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_latest_summary_report(self) -> Optional[Dict[str, float]]:
        """Look for the most recent summary report to compare as baseline."""
        pattern = os.path.join(self.output_dir, "eval_summary_*.json")
        summary_files = sorted(glob.glob(pattern))
        if not summary_files:
            return None
        # Return the last one before current run
        latest_file = summary_files[-1]
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            app_logger.warning(f"[Reporter] Failed to read previous baseline {latest_file}: {e}")
            return None

    def export_summary(
        self,
        metrics: Dict[str, Any],
        details: List[Dict[str, Any]],
        gate_thresholds: Optional[Dict[str, float]] = None,
    ) -> Tuple[str, bool]:
        """
        Exports CSV reports and verifies against quality gates & regressions.
        Returns (report_path, is_passed).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        detail_path = os.path.join(self.output_dir, f"eval_details_{timestamp}.csv")
        summary_path = os.path.join(self.output_dir, f"eval_summary_{timestamp}.json")

        # 1. Export per-query detail CSV
        if details:
            df_details = pd.DataFrame(details)
            df_details.to_csv(detail_path, index=False, encoding="utf-8")

        # 2. Check previous baseline for regression detection
        prev_baseline = self._get_latest_summary_report()

        # 3. Save current summary
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 4. Build table & evaluate quality gates
        default_gates = {
            "mean_recall@5": 0.70,
            "mean_mrr": 0.65,
            "faithfulness": 0.80,
            "answer_relevancy": 0.75,
        }
        gates = gate_thresholds or default_gates

        table_data = []
        is_passed = True
        gate_failures = []

        for metric_name, current_val in metrics.items():
            gate_val = gates.get(metric_name)
            prev_val = prev_baseline.get(metric_name) if prev_baseline else None

            # Calculate regression vs baseline
            if prev_val is not None and isinstance(current_val, (int, float)):
                diff = current_val - prev_val
                diff_str = f"{diff:+.4f}"
                if diff < -0.05:  # Regression exceeds 5%
                    is_passed = False
                    gate_failures.append(f"{metric_name} regressed by {diff:.4f} (> 5% drop vs baseline)")
            else:
                diff_str = "N/A"

            # Check threshold gate
            status = "PASS"
            if gate_val is not None and isinstance(current_val, (int, float)):
                if current_val < gate_val:
                    status = f"FAIL (< {gate_val})"
                    is_passed = False
                    gate_failures.append(f"{metric_name} ({current_val}) < Gate ({gate_val})")
                else:
                    status = f"PASS (>= {gate_val})"

            table_data.append([
                metric_name,
                f"{current_val:.4f}" if isinstance(current_val, float) else str(current_val),
                status,
                diff_str,
            ])

        print("\n" + "=" * 70)
        print("          VERIRAG QUANTITATIVE EVALUATION REPORT")
        print("=" * 70)
        print(tabulate(table_data, headers=["Metric", "Score", "Quality Gate", "vs Baseline"], tablefmt="grid"))
        print(f"\n[Detail CSV] {detail_path}")
        print(f"[Summary JSON] {summary_path}")

        if not is_passed:
            app_logger.error(f"[Reporter] Quality gate failed: {'; '.join(gate_failures)}")
        else:
            app_logger.info("[Reporter] All quality gates passed successfully!")

        print("=" * 70 + "\n")
        return detail_path, is_passed