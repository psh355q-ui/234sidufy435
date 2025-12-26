"""
Log Reader for Debugging Agent

Reads and aggregates logs from all agent skills.

Usage:
    python log_reader.py --days 1 --categories system,war-room
    python log_reader.py --agent signal-consolidation --days 7
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

# Base log directory
LOGS_DIR = Path(__file__).parent.parent.parent.parent / "logs"


class LogReader:
    """Read and aggregate agent logs"""
    
    def __init__(self, days: int = 1, categories: List[str] = None, agent: str = None):
        """
        Initialize log reader
        
        Args:
            days: Number of days to look back
            categories: Filter by categories (e.g., ["system", "war-room"])
            agent: Filter by specific agent name
        """
        self.days = days
        self.categories = categories or []
        self.agent = agent
        self.cutoff_date = datetime.now() - timedelta(days=days)
        
    def read_logs(self) -> Dict[str, Any]:
        """
        Read all logs and aggregate statistics
        
        Returns:
            {
                "agents": [...],
                "total_executions": int,
                "total_errors": int,
                "time_range": str,
                "executions": [...],
                "errors": [...],
                "performance": [...]
            }
        """
        print(f"🔍 Reading logs from: {LOGS_DIR}")
        print(f"   Days: {self.days}, Categories: {self.categories or 'all'}")
        
        if not LOGS_DIR.exists():
            print(f"❌ Logs directory not found: {LOGS_DIR}")
            return self._empty_result()
        
        executions = []
        errors = []
        performance = []
        agents_found = set()
        
        # Scan all categories
        for category_dir in LOGS_DIR.iterdir():
            if not category_dir.is_dir():
                continue
            
            # Filter by category
            if self.categories and category_dir.name not in self.categories:
                continue
            
            print(f"\n📂 Category: {category_dir.name}")
            
            # Scan all agents in category
            for agent_dir in category_dir.iterdir():
                if not agent_dir.is_dir():
                    continue
                
                # Filter by agent
                if self.agent and agent_dir.name != self.agent:
                    continue
                
                agent_name = f"{category_dir.name}/{agent_dir.name}"
                agents_found.add(agent_name)
                
                print(f"   📊 Agent: {agent_name}")
                
                # Read execution logs
                exec_logs = self._read_jsonl_files(agent_dir, "execution")
                executions.extend(exec_logs)
                print(f"      Executions: {len(exec_logs)}")
                
                # Read error logs
                error_logs = self._read_jsonl_files(agent_dir, "errors")
                errors.extend(error_logs)
                print(f"      Errors: {len(error_logs)}")
                
                # Read performance logs
                perf_logs = self._read_jsonl_files(agent_dir, "performance")
                performance.extend(perf_logs)
                print(f"      Performance: {len(perf_logs)}")
        
        print(f"\n✅ Total: {len(agents_found)} agents, {len(executions)} executions, {len(errors)} errors")
        
        return {
            "agents": sorted(list(agents_found)),
            "total_executions": len(executions),
            "total_errors": len(errors),
            "total_performance": len(performance),
            "time_range": f"{self.cutoff_date.date()} to {datetime.now().date()}",
            "executions": executions,
            "errors": errors,
            "performance": performance
        }
    
    def _read_jsonl_files(self, agent_dir: Path, log_type: str) -> List[Dict]:
        """
        Read JSONL files matching pattern
        
        Args:
            agent_dir: Agent directory path
            log_type: "execution", "errors", or "performance"
        
        Returns:
            List of log entries
        """
        logs = []
        
        # Find matching files (e.g., execution-2025-12-26.jsonl)
        for log_file in agent_dir.glob(f"{log_type}-*.jsonl"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        log_entry = json.loads(line)
                        
                        # Filter by date
                        timestamp = datetime.fromisoformat(log_entry.get('timestamp', ''))
                        if timestamp >= self.cutoff_date:
                            logs.append(log_entry)
            
            except Exception as e:
                print(f"      ⚠️ Error reading {log_file.name}: {e}")
        
        return logs
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "agents": [],
            "total_executions": 0,
            "total_errors": 0,
            "total_performance": 0,
            "time_range": f"{self.cutoff_date.date()} to {datetime.now().date()}",
            "executions": [],
            "errors": [],
            "performance": []
        }
    
    def get_statistics(self, logs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate detailed statistics
        
        Args:
            logs_data: Output from read_logs()
        
        Returns:
            Detailed statistics
        """
        executions = logs_data["executions"]
        errors = logs_data["errors"]
        
        # Execution statistics
        exec_by_agent = defaultdict(int)
        exec_by_status = defaultdict(int)
        total_duration = 0
        
        for log in executions:
            exec_by_agent[log.get('agent', 'unknown')] += 1
            exec_by_status[log.get('status', 'UNKNOWN')] += 1
            total_duration += log.get('duration_ms', 0)
        
        # Error statistics
        error_by_agent = defaultdict(int)
        error_by_type = defaultdict(int)
        error_by_impact = defaultdict(int)
        
        for log in errors:
            error_by_agent[log.get('agent', 'unknown')] += 1
            error_type = log.get('error', {}).get('type', 'Unknown')
            error_by_type[error_type] += 1
            error_by_impact[log.get('impact', 'UNKNOWN')] += 1
        
        # Error rate by agent
        error_rates = {}
        for agent in logs_data["agents"]:
            exec_count = exec_by_agent.get(agent, 0)
            error_count = error_by_agent.get(agent, 0)
            if exec_count > 0:
                error_rates[agent] = error_count / (exec_count + error_count)
            elif error_count > 0:
                error_rates[agent] = 1.0  # All failures
            else:
                error_rates[agent] = 0.0
        
        return {
            "execution_stats": {
                "by_agent": dict(exec_by_agent),
                "by_status": dict(exec_by_status),
                "avg_duration_ms": total_duration / len(executions) if executions else 0
            },
            "error_stats": {
                "by_agent": dict(error_by_agent),
                "by_type": dict(error_by_type),
                "by_impact": dict(error_by_impact)
            },
            "error_rates": error_rates,
            "summary": {
                "total_agents": len(logs_data["agents"]),
                "total_executions": logs_data["total_executions"],
                "total_errors": logs_data["total_errors"],
                "overall_error_rate": logs_data["total_errors"] / (logs_data["total_executions"] + logs_data["total_errors"]) if (logs_data["total_executions"] + logs_data["total_errors"]) > 0 else 0
            }
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Read agent logs")
    parser.add_argument("--days", type=int, default=1, help="Days to look back (default: 1)")
    parser.add_argument("--categories", type=str, help="Comma-separated categories (e.g., system,war-room)")
    parser.add_argument("--agent", type=str, help="Specific agent name")
    parser.add_argument("--output", type=str, default="logs_summary.json", help="Output file")
    parser.add_argument("--stats", action="store_true", help="Include detailed statistics")
    
    args = parser.parse_args()
    
    # Parse categories
    categories = args.categories.split(",") if args.categories else None
    
    # Read logs
    reader = LogReader(days=args.days, categories=categories, agent=args.agent)
    logs_data = reader.read_logs()
    
    # Add statistics if requested
    if args.stats:
        stats = reader.get_statistics(logs_data)
        logs_data["statistics"] = stats
        
        print("\n" + "="*70)
        print("📊 Statistics Summary")
        print("="*70)
        print(f"Overall Error Rate: {stats['summary']['overall_error_rate']:.1%}")
        print(f"\nError Rates by Agent:")
        for agent, rate in sorted(stats['error_rates'].items(), key=lambda x: -x[1]):
            print(f"  {agent}: {rate:.1%}")
    
    # Save output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(logs_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    print(f"   Agents: {len(logs_data['agents'])}")
    print(f"   Executions: {logs_data['total_executions']}")
    print(f"   Errors: {logs_data['total_errors']}")


if __name__ == "__main__":
    main()
