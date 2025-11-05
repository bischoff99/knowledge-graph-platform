#!/usr/bin/env python3
"""
Test Result Parser for Knowledge Graph Auto-Updates
Parses pytest/vitest output and updates entity observations
"""

import re
import sys
from datetime import datetime
from pathlib import Path


class TestResultParser:
    def __init__(self):
        self.results = {}
    
    def parse_pytest_output(self, output):
        """Parse pytest output for test statistics"""
        # Example: "108 passed, 3 failed in 6.64s"
        pattern = r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?.*?in\s+([\d.]+)s'
        match = re.search(pattern, output)
        
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2)) if match.group(2) else 0
            duration = float(match.group(3))
            total = passed + failed
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            self.results = {
                'passed': passed,
                'failed': failed,
                'total': total,
                'pass_rate': pass_rate,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            return True
        return False
    
    def generate_observation(self, project_name="EasyPost MCP Project"):
        """Generate observation string for MCP memory"""
        if not self.results:
            return None
        
        obs = []
        obs.append(f"Meta:last_tested:{self.results['timestamp'][:10]}")
        obs.append(f"Health:Test pass rate:{self.results['pass_rate']:.1f}% ({self.results['passed']}/{self.results['total']})")
        obs.append(f"Performance:Test duration:{self.results['duration']:.2f}s")
        
        # Trend analysis
        if self.results['pass_rate'] >= 97:
            obs.append("Health:Test status:Excellent")
        elif self.results['pass_rate'] >= 90:
            obs.append("Health:Test status:Good")
        else:
            obs.append("Health:Test status:Needs attention")
        
        return obs
    
    def should_update(self, prev_pass_rate):
        """Check if update is significant enough to record"""
        if not self.results:
            return False
        
        # Update if:
        # 1. Pass rate changed by >2%
        # 2. Tests failed where none failed before
        # 3. It's been >7 days since last update
        
        current_rate = self.results['pass_rate']
        return abs(current_rate - prev_pass_rate) > 2.0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test-result-parser.py <pytest_output_file>")
        print("Example: pytest tests/ -v > output.txt && python test-result-parser.py output.txt")
        sys.exit(1)
    
    parser = TestResultParser()
    with open(sys.argv[1]) as f:
        output = f.read()
    
    if parser.parse_pytest_output(output):
        obs = parser.generate_observation()
        print("Parsed test results:")
        for o in obs:
            print(f"  {o}")
    else:
        print("Could not parse test results")
