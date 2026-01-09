import json
from pathlib import Path
from datetime import datetime


def save_report(report: dict, report_dir: Path):
    report_dir.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = report_dir / f"{report['input']}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)