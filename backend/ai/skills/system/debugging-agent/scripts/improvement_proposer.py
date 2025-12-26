"""
Improvement Proposer for Debugging Agent

Generates improvement proposals from detected patterns.

Calculates confidence score using 5 metrics:
1. Error Reproducibility (30%)
2. Historical Success (25%)
3. Impact Clarity (20%)
4. Root Cause Evidence (15%)
5. Solution Simplicity (10%)

Usage:
    python improvement_proposer.py --input patterns.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class ImprovementProposer:
    """Generate improvement proposals"""
    
    def __init__(self, patterns_data: Dict[str, Any]):
        """
        Initialize proposer
        
        Args:
            patterns_data: Output from pattern_detector.py
        """
        self.patterns = patterns_data.get("patterns", [])
        self.summary = patterns_data.get("summary", {})
        
        # Proposals directory - separate from runtime logs
        self.proposals_dir = Path(__file__).parent.parent.parent.parent / "debugging" / "proposals"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_proposals(self) -> List[str]:
        """
        Generate proposals for all patterns
        
        Returns:
            List of proposal file paths
        """
        proposal_files = []
        
        print(f"🔧 Generating proposals for {len(self.patterns)} patterns...")
        
        for i, pattern in enumerate(self.patterns, 1):
            print(f"\n{i}. {pattern['type']} - {pattern['agent']} ({pattern['priority']})")
            
            # Generate proposal
            proposal = self._create_proposal(pattern)
            
            # Save to file
            filename = self._get_proposal_filename(pattern)
            filepath = self.proposals_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(proposal)
            
            proposal_files.append(str(filepath))
            print(f"   💾 Saved: {filename}")
        
        return proposal_files
    
    def _create_proposal(self, pattern: Dict[str, Any]) -> str:
        """
        Create markdown proposal for a pattern
        
        Args:
            pattern: Pattern dictionary
        
        Returns:
            Markdown proposal text
        """
        # Calculate confidence
        confidence = self._calculate_confidence(pattern)
        
        # Generate proposal based on type
        if pattern["type"] == "high_error_rate":
            return self._proposal_high_error_rate(pattern, confidence)
        elif pattern["type"] == "recurring_error":
            return self._proposal_recurring_error(pattern, confidence)
        elif pattern["type"] == "performance_degradation":
            return self._proposal_performance_degradation(pattern, confidence)
        elif pattern["type"] == "api_rate_limit":
            return self._proposal_api_rate_limit(pattern, confidence)
        else:
            return self._proposal_generic(pattern, confidence)
    
    def _proposal_high_error_rate(self, pattern: Dict[str, Any], confidence: float) -> str:
        """Generate proposal for high error rate"""
        agent = pattern["agent"]
        error_rate = pattern["error_rate"]
        executions = pattern["executions"]
        errors = pattern["errors"]
        
        return f"""# Improvement Proposal: Fix High Error Rate in {agent}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: {agent}  
**Priority**: {pattern["priority"]}  
**Confidence**: {confidence:.0%}

---

## 🔍 Issue Summary

**Pattern Detected**: High Error Rate

**Error Rate**: {error_rate:.1%} ({errors} errors / {executions + errors} total)

**Impact**: 
- {agent} is experiencing high failure rate
- Successful operations: {executions}
- Failed operations: {errors}
- User experience severely degraded

---

## 📊 Root Cause Analysis

**Evidence**:
1. Error rate ({error_rate:.1%}) exceeds threshold (5%)
2. Pattern consistent across recent executions
3. {"CRITICAL" if error_rate > 0.5 else "HIGH"} priority issue affecting reliability

**Likely Causes**:
- Database connection issues
- Missing required arguments in function calls
- API endpoint changes
- Environment configuration problems

---

## 💡 Proposed Solution

### Step 1: Investigate Error Logs

Check the specific error messages in:
```bash
cat backend/ai/skills/logs/{agent.replace('/', '/')}/errors-*.jsonl
```

### Step 2: Common Fixes

**Option A: Missing Arguments**
- Review recent code changes to {agent}
- Check for new required parameters
- Update function calls with missing arguments

**Option B: Connection Issues**
- Verify database connection strings
- Check API credentials
- Test network connectivity

**Option C: Configuration**
- Review environment variables
- Check .env file for missing values
- Verify service dependencies

**Confidence**: {confidence:.0%}

---

## 🧪 Verification Plan

1. Read error logs to identify specific error types
2. Apply appropriate fix based on error messages
3. Re-run {agent} operations
4. Monitor error rate for 24 hours
5. Target: Error rate < 5%

---

## 📝 Risk Assessment

**Risk Level**: {"HIGH" if error_rate > 0.5 else "MEDIUM"}

**Potential Issues**:
- Fix may not address all error types
- May require multiple iterations
- Downtime during testing

**Rollback Plan**:
- Revert code changes if errors persist
- Monitor logs continuously
- Document all changes

---

## 🎯 Confidence Breakdown

- Error Reproducibility: {self._score_reproducibility(pattern):.0%}
- Historical Success: {self._score_historical_success(pattern):.0%}
- Impact Clarity: {self._score_impact_clarity(pattern):.0%}
- Root Cause Evidence: {self._score_root_cause_evidence(pattern):.0%}
- Solution Simplicity: {self._score_solution_simplicity(pattern):.0%}

**Overall Confidence**: {confidence:.0%}

---

**Next Steps**: Review error logs and apply appropriate fix.
"""
    
    def _proposal_recurring_error(self, pattern: Dict[str, Any], confidence: float) -> str:
        """Generate proposal for recurring error"""
        agent = pattern["agent"]
        error_type = pattern["error_type"]
        count = pattern["count"]
        
        return f"""# Improvement Proposal: Fix Recurring {error_type} in {agent}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: {agent}  
**Priority**: {pattern["priority"]}  
**Confidence**: {confidence:.0%}

---

## 🔍 Issue Summary

**Pattern Detected**: Recurring Error

**Error**: `{error_type}`

**Occurrences**: {count} times in 24 hours

**Impact**: Repeated failures affecting {agent} reliability

---

## 📊 Root Cause Analysis

**Evidence**:
- {count} occurrences of same error type
- First seen: {pattern.get('first_seen', 'N/A')}
- Last seen: {pattern.get('last_seen', 'N/A')}

**Sample Error**:
```
{json.dumps(pattern.get('sample_error', {}), indent=2)}
```

---

## 💡 Proposed Solution

1. Locate error source in code
2. Add error handling or fix root cause
3. Test thoroughly
4. Monitor for recurrence

**Confidence**: {confidence:.0%}

---

**Next Steps**: Investigate error stack trace and apply fix.
"""
    
    def _proposal_generic(self, pattern: Dict[str, Any], confidence: float) -> str:
        """Generate generic proposal"""
        return f"""# Improvement Proposal: {pattern['type']}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Pattern**: {pattern['type']}  
**Agent**: {pattern['agent']}  
**Priority**: {pattern['priority']}  
**Confidence**: {confidence:.0%}

---

## 🔍 Details

{json.dumps(pattern, indent=2)}

---

**Next Steps**: Manual investigation required.
"""
    
    def _proposal_performance_degradation(self, pattern: Dict[str, Any], confidence: float) -> str:
        """Generate proposal for performance degradation"""
        # Simplified - could be expanded
        return self._proposal_generic(pattern, confidence)
    
    def _proposal_api_rate_limit(self, pattern: Dict[str, Any], confidence: float) -> str:
        """Generate proposal for API rate limit"""
        # Simplified - could be expanded
        return self._proposal_generic(pattern, confidence)
    
    def _calculate_confidence(self, pattern: Dict[str, Any]) -> float:
        """
        Calculate confidence score using 5 metrics
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        reproducibility = self._score_reproducibility(pattern)
        historical_success = self._score_historical_success(pattern)
        impact_clarity = self._score_impact_clarity(pattern)
        root_cause_evidence = self._score_root_cause_evidence(pattern)
        solution_simplicity = self._score_solution_simplicity(pattern)
        
        confidence = (
            reproducibility * 0.30 +
            historical_success * 0.25 +
            impact_clarity * 0.20 +
            root_cause_evidence * 0.15 +
            solution_simplicity * 0.10
        )
        
        return confidence
    
    def _score_reproducibility(self, pattern: Dict[str, Any]) -> float:
        """Score error reproducibility (30%)"""
        pattern_type = pattern["type"]
        
        if pattern_type == "high_error_rate":
            error_rate = pattern.get("error_rate", 0)
            return error_rate  # High error rate = high reproducibility
        
        elif pattern_type == "recurring_error":
            count = pattern.get("count", 0)
            return min(count / 10.0, 1.0)  # 10+ = 100%
        
        return 0.5  # Default
    
    def _score_historical_success(self, pattern: Dict[str, Any]) -> float:
        """Score based on historical fix success (25%)"""
        # Simplified - in real system, track fix success rate
        # For now, assume moderate success
        return 0.7
    
    def _score_impact_clarity(self, pattern: Dict[str, Any]) -> float:
        """Score impact clarity (20%)"""
        priority = pattern.get("priority", "MEDIUM")
        
        impact_scores = {
            "CRITICAL": 1.0,
            "HIGH": 0.85,
            "MEDIUM": 0.65,
            "LOW": 0.4
        }
        
        return impact_scores.get(priority, 0.5)
    
    def _score_root_cause_evidence(self, pattern: Dict[str, Any]) -> float:
        """Score root cause evidence (15%)"""
        # Check if we have error details
        if "sample_error" in pattern:
            error = pattern["sample_error"]
            has_stack = bool(error.get("stack"))
            has_message = bool(error.get("message"))
            
            if has_stack and has_message:
                return 0.9
            elif has_message:
                return 0.7
        
        # For high_error_rate, we know the rate
        if pattern["type"] == "high_error_rate":
            return 0.6
        
        return 0.3
    
    def _score_solution_simplicity(self, pattern: Dict[str, Any]) -> float:
        """Score solution simplicity (10%)"""
        pattern_type = pattern["type"]
        
        # High error rate often requires investigation
        if pattern_type == "high_error_rate":
            return 0.5  # Moderate complexity
        
        # Recurring errors might be simple fixes
        if pattern_type == "recurring_error":
            return 0.7
        
        return 0.6
    
    def _get_proposal_filename(self, pattern: Dict[str, Any]) -> str:
        """Generate proposal filename"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        agent_safe = pattern["agent"].replace("/", "-")
        pattern_type = pattern["type"]
        
        return f"proposal-{timestamp}-{agent_safe}-{pattern_type}.md"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate improvement proposals")
    parser.add_argument("--input", type=str, default="patterns.json", help="Input file from pattern_detector")
    
    args = parser.parse_args()
    
    # Load patterns
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        print(f"   Run pattern_detector.py first to generate patterns.json")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        patterns_data = json.load(f)
    
    # Generate proposals
    proposer = ImprovementProposer(patterns_data)
    proposal_files = proposer.generate_proposals()
    
    # Summary
    print("\n" + "="*70)
    print("✅ Proposal Generation Complete")
    print("="*70)
    print(f"Generated {len(proposal_files)} proposals")
    print(f"\nProposal files:")
    for filepath in proposal_files:
        print(f"  - {Path(filepath).name}")
    
    print(f"\n📁 Location: {proposer.proposals_dir}")


if __name__ == "__main__":
    main()
