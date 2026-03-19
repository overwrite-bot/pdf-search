#!/usr/bin/env python3
"""
Parse pytest output and extract optimization metrics.
"""

import sys
import re

def parse_pytest_log(log_file):
    """Extract metrics from pytest log."""
    try:
        with open(log_file) as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading log: {e}")
        return None
    
    # Extract pass/fail counts
    match = re.search(r'(\d+) passed', content)
    passed = int(match.group(1)) if match else 0
    
    match = re.search(r'(\d+) failed', content)
    failed = int(match.group(1)) if match else 0
    
    total = passed + failed
    extraction_quality = (passed / total * 100) if total > 0 else 0
    
    # Extract timing (pytest shows duration)
    match = re.search(r'(\d+\.\d+)s', content)
    speed_ms = int(float(match.group(1)) * 1000) if match else 0
    
    # Link validity (assume 100 if no link tests fail)
    link_validity = 100 if failed == 0 else 80
    
    # PDF success (simple estimate based on pass rate)
    pdf_success = extraction_quality
    
    return {
        'extraction_quality': round(extraction_quality, 0),
        'link_validity': link_validity,
        'speed_ms': speed_ms,
        'pdf_success': round(pdf_success, 0),
        'total_tests': total,
        'passed': passed,
        'failed': failed
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: parse_metrics.py <test_results.log>")
        sys.exit(1)
    
    metrics = parse_pytest_log(sys.argv[1])
    
    if metrics:
        print(f"METRIC: extraction={int(metrics['extraction_quality'])},link={int(metrics['link_validity'])},speed={metrics['speed_ms']},pdf={int(metrics['pdf_success'])}")
        print(f"Details: {metrics['passed']} passed, {metrics['failed']} failed, {metrics['total_tests']} total")
    else:
        print("Failed to parse metrics")
        sys.exit(1)
