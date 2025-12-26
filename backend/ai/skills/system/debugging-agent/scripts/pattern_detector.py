"""
Pattern Detector for Debugging Agent

Detects problematic patterns in agent logs.

Patterns:
- Recurring errors (3+ same type in 24h)
- Performance degradation (>2x baseline)
- High error rate (>5%)
- API rate limits (5+ errors)

Usage:
    python pattern_detector.py --input logs_summary.json --output patterns.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict


class PatternDetector:
    """Detect patterns in agent logs"""
    
    def __init__(self, logs_data: Dict[str, Any]):
        """
        Initialize pattern detector
        
        Args:
            logs_data: Output from log_reader.py
        """
        self.logs_data = logs_data
        self.executions = logs_data.get("executions", [])
        self.errors = logs_data.get("errors", [])
        self.performance = logs_data.get("performance", [])
    
    def detect_all_patterns(self) -> Dict[str, Any]:
        """
        Detect all patterns
        
        Returns:
            {
                "patterns": [...],
                "summary": {...}
            }
        """
        patterns = []
        
        # Pattern A: Recurring Errors
        recurring = self.detect_recurring_errors()
        patterns.extend(recurring)
        print(f"✅ Recurring errors: {len(recurring)}")
        
        # Pattern B: Performance Degradation
        perf_issues = self.detect_performance_degradation()
        patterns.extend(perf_issues)
        print(f"✅ Performance degradation: {len(perf_issues)}")
        
        # Pattern C: High Error Rate
        high_error_rates = self.detect_high_error_rate()
        patterns.extend(high_error_rates)
        print(f"✅ High error rates: {len(high_error_rates)}")
        
        # Pattern D: API Rate Limits
        rate_limits = self.detect_api_rate_limits()
        patterns.extend(rate_limits)
        print(f"✅ API rate limits: {len(rate_limits)}")
        
        # Pattern E: Mock Data Usage 🆕
        mock_usage = self.detect_mock_data_usage()
        patterns.extend(mock_usage)
        print(f"✅ Mock data usage: {len(mock_usage)}")
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        patterns.sort(key=lambda p: priority_order.get(p["priority"], 99))
        
        return {
            "patterns": patterns,
            "summary": {
                "total_patterns": len(patterns),
                "by_type": self._count_by_type(patterns),
                "by_priority": self._count_by_priority(patterns),
                "agents_affected": list(set(p["agent"] for p in patterns))
            }
        }
    
    def detect_recurring_errors(self) -> List[Dict[str, Any]]:
        """
        Detect recurring errors (3+ in 24h)
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Group errors by agent and error type
        error_groups = defaultdict(list)
        
        for error in self.errors:
            agent = error.get("agent", "unknown")
            error_type = error.get("error", {}).get("type", "Unknown")
            key = f"{agent}::{error_type}"
            error_groups[key].append(error)
        
        # Check for recurring errors
        cutoff = datetime.now() - timedelta(hours=24)
        
        for key, error_list in error_groups.items():
            agent, error_type = key.split("::")
            
            # Filter to last 24h
            recent_errors = [
                e for e in error_list 
                if datetime.fromisoformat(e.get("timestamp", "")) >= cutoff
            ]
            
            if len(recent_errors) >= 3:
                # Get first and last occurrence
                timestamps = sorted([
                    datetime.fromisoformat(e.get("timestamp", "")) 
                    for e in recent_errors
                ])
                
                # Determine impact
                impacts = [e.get("impact", "UNKNOWN") for e in recent_errors]
                max_impact = self._get_max_impact(impacts)
                
                patterns.append({
                    "type": "recurring_error",
                    "agent": agent,
                    "error_type": error_type,
                    "count": len(recent_errors),
                    "impact": max_impact,
                    "priority": "HIGH" if max_impact in ["CRITICAL", "HIGH"] else "MEDIUM",
                    "first_seen": timestamps[0].isoformat(),
                    "last_seen": timestamps[-1].isoformat(),
                    "sample_error": recent_errors[0].get("error", {}),
                    "details": f"{error_type} occurred {len(recent_errors)} times in 24h"
                })
        
        return patterns
    
    def detect_performance_degradation(self) -> List[Dict[str, Any]]:
        """
        Detect performance degradation (>2x baseline)
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Group executions by agent
        exec_by_agent = defaultdict(list)
        
        for execution in self.executions:
            agent = execution.get("agent", "unknown")
            duration = execution.get("duration_ms", 0)
            exec_by_agent[agent].append(duration)
        
        # Check each agent
        for agent, durations in exec_by_agent.items():
            if len(durations) < 3:  # Need enough data
                continue
            
            # Calculate baseline (median of first half)
            sorted_durations = sorted(durations)
            half_point = len(sorted_durations) // 2
            baseline = sorted_durations[half_point] if half_point > 0 else sorted_durations[0]
            
            # Check recent executions
            recent = durations[-3:]  # Last 3
            avg_recent = sum(recent) / len(recent)
            
            if avg_recent > baseline * 2:
                patterns.append({
                    "type": "performance_degradation",
                    "agent": agent,
                    "baseline_ms": baseline,
                    "recent_avg_ms": int(avg_recent),
                    "degradation_factor": round(avg_recent / baseline, 2) if baseline > 0 else 0,
                    "priority": "MEDIUM",
                    "details": f"Performance degraded from {baseline}ms to {int(avg_recent)}ms"
                })
        
        return patterns
    
    def detect_high_error_rate(self) -> List[Dict[str, Any]]:
        """
        Detect high error rate (>5%)
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Count by agent
        exec_by_agent = defaultdict(int)
        error_by_agent = defaultdict(int)
        
        for execution in self.executions:
            agent = execution.get("agent", "unknown")
            exec_by_agent[agent] += 1
        
        for error in self.errors:
            agent = error.get("agent", "unknown")
            error_by_agent[agent] += 1
        
        # Calculate error rates
        for agent in set(list(exec_by_agent.keys()) + list(error_by_agent.keys())):
            exec_count = exec_by_agent.get(agent, 0)
            error_count = error_by_agent.get(agent, 0)
            total = exec_count + error_count
            
            if total == 0:
                continue
            
            error_rate = error_count / total
            
            if error_rate > 0.05:  # >5%
                priority = "CRITICAL" if error_rate > 0.5 else "HIGH"
                
                patterns.append({
                    "type": "high_error_rate",
                    "agent": agent,
                    "error_rate": round(error_rate, 3),
                    "executions": exec_count,
                    "errors": error_count,
                    "priority": priority,
                    "details": f"Error rate {error_rate:.1%} ({error_count}/{total})"
                })
        
        return patterns
    
    def detect_api_rate_limits(self) -> List[Dict[str, Any]]:
        """
        Detect API rate limit errors (5+ occurrences)
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Search for rate limit related errors
        rate_limit_keywords = ["rate limit", "too many requests", "429", "quota exceeded"]
        
        # Group by agent
        rate_limit_errors = defaultdict(list)
        
        for error in self.errors:
            agent = error.get("agent", "unknown")
            error_msg = error.get("error", {}).get("message", "").lower()
            
            if any(keyword in error_msg for keyword in rate_limit_keywords):
                rate_limit_errors[agent].append(error)
        
        # Check counts
        cutoff = datetime.now() - timedelta(hours=24)
        
        for agent, error_list in rate_limit_errors.items():
            # Filter to last 24h
            recent = [
                e for e in error_list
                if datetime.fromisoformat(e.get("timestamp", "")) >= cutoff
            ]
            
            if len(recent) >= 5:
                timestamps = sorted([
                    datetime.fromisoformat(e.get("timestamp", ""))
                    for e in recent
                ])
                
                patterns.append({
                    "type": "api_rate_limit",
                    "agent": agent,
                    "count": len(recent),
                    "priority": "HIGH",
                    "first_seen": timestamps[0].isoformat(),
                    "last_seen": timestamps[-1].isoformat(),
                    "sample_error": recent[0].get("error", {}),
                    "details": f"API rate limit hit {len(recent)} times in 24h"
                })
        
        return patterns
    
    def detect_mock_data_usage(self) -> List[Dict[str, Any]]:
        """
        🆕 Detect usage of mock/test data instead of real production data
        
        This pattern helps agents avoid debugging with fake data.
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Check execution logs for mock data indicators
        mock_by_agent = defaultdict(list)
        
        for execution in self.executions:
            agent = execution.get("agent", "unknown")
            input_data = execution.get("input", {})
            
            # Check for mock flags in input parameters
            mock_indicators = [
                ("use_mock", True),
                ("mock_data", True),
                ("use_mock_consensus", True),
                ("use_real_data", False),  # False means using mock
            ]
            
            for key, bad_value in mock_indicators:
                if input_data.get(key) == bad_value:
                    mock_by_agent[agent].append({
                        "timestamp": execution.get("timestamp", ""),
                        "task_id": execution.get("task_id"),
                        "mock_flag": f"{key}={bad_value}",
                        "input": input_data
                    })
                    break  # Don't count same execution multiple times
        
        # Create patterns for agents using mock data
        for agent, mock_usages in mock_by_agent.items():
            if len(mock_usages) > 0:
                # Get total executions for this agent
                agent_execs = [e for e in self.executions if e.get("agent") == agent]
                total = len(agent_execs)
                mock_count = len(mock_usages)
                mock_pct = (mock_count / total * 100) if total > 0 else 0
                
                priority = "HIGH" if mock_count > 5 or mock_pct > 50 else "MEDIUM"
                
                patterns.append({
                    "type": "mock_data_usage",
                    "agent": agent,
                    "mock_usage_count": mock_count,
                    "total_executions": total,
                    "mock_percentage": round(mock_pct, 1),
                    "priority": priority,
                    "sample_usages": mock_usages[:3],  # First 3 examples
                    "details": f"Agent using mock/test data in {mock_count} executions ({mock_pct:.1f}%)"
                })
        
        return patterns
    
    def _get_max_impact(self, impacts: List[str]) -> str:
        """Get maximum impact from list"""
        impact_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
        return min(impacts, key=lambda i: impact_order.get(i, 99))
    
    def _count_by_type(self, patterns: List[Dict]) -> Dict[str, int]:
        """Count patterns by type"""
        counts = defaultdict(int)
        for p in patterns:
            counts[p["type"]] += 1
        return dict(counts)
    
    def _count_by_priority(self, patterns: List[Dict]) -> Dict[str, int]:
        """Count patterns by priority"""
        counts = defaultdict(int)
        for p in patterns:
            counts[p["priority"]] += 1
        return dict(counts)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Detect patterns in agent logs")
    parser.add_argument("--input", type=str, default="logs_summary.json", help="Input file from log_reader")
    parser.add_argument("--output", type=str, default="patterns.json", help="Output file")
    
    args = parser.parse_args()
    
    # Load logs data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        print(f"   Run log_reader.py first to generate logs_summary.json")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        logs_data = json.load(f)
    
    print(f"📊 Analyzing {logs_data['total_executions']} executions, {logs_data['total_errors']} errors...")
    print()
    
    # Detect patterns
    detector = PatternDetector(logs_data)
    result = detector.detect_all_patterns()
    
    # Display summary
    print("\n" + "="*70)
    print("🔍 Pattern Detection Summary")
    print("="*70)
    print(f"Total Patterns: {result['summary']['total_patterns']}")
    print(f"\nBy Type:")
    for pattern_type, count in result['summary']['by_type'].items():
        print(f"  {pattern_type}: {count}")
    print(f"\nBy Priority:")
    for priority, count in result['summary']['by_priority'].items():
        print(f"  {priority}: {count}")
    print(f"\nAffected Agents: {len(result['summary']['agents_affected'])}")
    for agent in result['summary']['agents_affected']:
        print(f"  - {agent}")
    
    # Save output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")


if __name__ == "__main__":
    main()
