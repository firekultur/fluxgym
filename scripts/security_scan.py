#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def which(tool: str) -> bool:
    return shutil.which(tool) is not None


def write_json(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    reports_dir = os.path.join(repo_root, "security_reports", timestamp)
    ensure_directory(reports_dir)

    print("✅ Security scan started")
    print(f"📁 Reports directory: {reports_dir}")

    summary: List[str] = []
    install_hints: List[str] = []

    # 1) Bandit - Python security linter
    if which("bandit"):
        print("▶ Running bandit (Python security linter)...")
        code, out, err = run_command(["bandit", "-r", repo_root, "-f", "json", "-q"])
        bandit_path = os.path.join(reports_dir, "bandit.json")
        try:
            data = json.loads(out or "{}")
        except json.JSONDecodeError:
            data = {"error": "Failed to parse bandit output", "raw": out}
        write_json(bandit_path, data)
        summary.append(f"bandit: exit={code}, issues={(len(data.get('results', [])) if isinstance(data, dict) else 'unknown')} -> {bandit_path}")
    else:
        summary.append("bandit: not installed")
        install_hints.append("pixi add bandit")

    # 2) pip-audit - dependency vulnerabilities
    if which("pip-audit"):
        print("▶ Running pip-audit (dependency vulnerabilities)...")
        args = ["pip-audit", "-f", "json"]
        req_file = os.path.join(repo_root, "requirements.txt")
        if os.path.exists(req_file):
            args += ["-r", req_file]
        code, out, err = run_command(args, cwd=repo_root)
        pa_path = os.path.join(reports_dir, "pip_audit.json")
        try:
            data = json.loads(out or "{}")
        except json.JSONDecodeError:
            data = {"error": "Failed to parse pip-audit output", "raw": out}
        write_json(pa_path, data)
        # pip-audit returns non-zero when vulns found; don't treat as fatal
        issues = 0
        if isinstance(data, list):
            for item in data:
                issues += len(item.get("vulns", []))
        summary.append(f"pip-audit: exit={code}, vulns={issues} -> {pa_path}")
    else:
        summary.append("pip-audit: not installed")
        install_hints.append("pixi add pip-audit")

    # 3) safety - alternative dependency vulnerability checker
    if which("safety"):
        print("▶ Running safety (dependency vulnerabilities)...")
        req_file = os.path.join(repo_root, "requirements.txt")
        args = ["safety", "check", "--json"]
        if os.path.exists(req_file):
            args += ["-r", req_file]
        code, out, err = run_command(args, cwd=repo_root)
        safety_path = os.path.join(reports_dir, "safety.json")
        try:
            data = json.loads(out or "{}")
        except json.JSONDecodeError:
            data = {"error": "Failed to parse safety output", "raw": out}
        write_json(safety_path, data)
        issues = len(data) if isinstance(data, list) else data.get("vulnerability_count", "unknown")
        summary.append(f"safety: exit={code}, issues={issues} -> {safety_path}")
    else:
        summary.append("safety: not installed")
        install_hints.append("pixi add safety")

    # 4) semgrep - static analysis with security rules
    if which("semgrep"):
        print("▶ Running semgrep (static analysis)...")
        # Use the CI default ruleset; keep going on errors
        code, out, err = run_command(["semgrep", "--config", "p/ci", "--json", repo_root])
        semgrep_path = os.path.join(reports_dir, "semgrep.json")
        try:
            data = json.loads(out or "{}")
        except json.JSONDecodeError:
            data = {"error": "Failed to parse semgrep output", "raw": out}
        write_json(semgrep_path, data)
        issues = len(data.get("results", [])) if isinstance(data, dict) else "unknown"
        summary.append(f"semgrep: exit={code}, findings={issues} -> {semgrep_path}")
    else:
        summary.append("semgrep: not installed")
        install_hints.append("pixi add semgrep")

    # 5) detect-secrets - secrets scanning
    if which("detect-secrets"):
        print("▶ Running detect-secrets (secrets scan)...")
        code, out, err = run_command(["detect-secrets", "scan", "--all-files", "--json"], cwd=repo_root)
        ds_path = os.path.join(reports_dir, "detect_secrets.json")
        try:
            data = json.loads(out or "{}")
        except json.JSONDecodeError:
            data = {"error": "Failed to parse detect-secrets output", "raw": out}
        write_json(ds_path, data)
        issues = 0
        if isinstance(data, dict):
            results = data.get("results", {})
            for _, findings in results.items():
                issues += len(findings)
        summary.append(f"detect-secrets: exit={code}, findings={issues} -> {ds_path}")
    else:
        summary.append("detect-secrets: not installed")
        install_hints.append("pixi add detect-secrets")

    # Write summary
    summary_path = os.path.join(reports_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Security scan summary\n")
        f.write("======================\n\n")
        for line in summary:
            f.write(f"- {line}\n")
        if install_hints:
            f.write("\nTools missing (install suggestions):\n")
            for hint in install_hints:
                f.write(f"- {hint}\n")

    print("\n🧾 Summary:")
    for line in summary:
        print(f"- {line}")
    if install_hints:
        print("\nSome tools were not installed. You can add them to your Pixi env:")
        for hint in install_hints:
            print(f"  • {hint}")

    print(f"\n📄 Full summary: {summary_path}")
    print("✅ Security scan complete")
    # Always exit 0 so the scan is informative, not blocking
    return 0


if __name__ == "__main__":
    sys.exit(main())


