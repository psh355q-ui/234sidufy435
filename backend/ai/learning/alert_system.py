"""
Agent Performance Alert System

Phase 25.4: Self-Learning Feedback Loop
Date: 2025-12-23

Sends alerts for low-performing or overconfident agents.
"""

import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentAlertSystem:
    """
    Alert system for agent performance issues

    Alert Types:
        - LOW_PERFORMER: Accuracy < 50%
        - CRITICAL_PERFORMER: Accuracy < 45%
        - OVERCONFIDENT: Confidence gap > 20%
        - HIGH_OVERCONFIDENT: Confidence gap > 30%
    """

    def __init__(self):
        """Initialize Alert System"""
        self.alerts_sent = []

    def check_and_send_alerts(
        self,
        low_performers: List[Dict],
        overconfident: List[Dict]
    ) -> List[Dict]:
        """
        Check performance issues and send alerts

        Args:
            low_performers: List of low-performing agents
            overconfident: List of overconfident agents

        Returns:
            List of alerts sent
        """
        alerts = []

        # Low performer alerts
        for agent in low_performers:
            alert = self._create_low_performer_alert(agent)
            self._send_alert(alert)
            alerts.append(alert)

        # Overconfident alerts
        for agent in overconfident:
            alert = self._create_overconfident_alert(agent)
            self._send_alert(alert)
            alerts.append(alert)

        self.alerts_sent.extend(alerts)
        return alerts

    def _create_low_performer_alert(self, agent: Dict) -> Dict:
        """
        Create alert for low-performing agent

        Args:
            agent: Agent performance data

        Returns:
            Alert dictionary
        """
        severity = agent["severity"]
        agent_name = agent["agent_name"]
        accuracy = agent["accuracy"]
        total_votes = agent["total_votes"]

        return {
            "type": "LOW_PERFORMER",
            "severity": severity,
            "agent_name": agent_name,
            "title": f"Low Performing Agent: {agent_name}",
            "message": (
                f"Agent '{agent_name}' has low accuracy: {accuracy:.1%}\n"
                f"Total votes: {total_votes}\n"
                f"Severity: {severity.upper()}\n\n"
                f"⚠️ Action required: Review agent logic or reduce weight"
            ),
            "metrics": {
                "accuracy": accuracy,
                "total_votes": total_votes,
            },
            "timestamp": datetime.now().isoformat()
        }

    def _create_overconfident_alert(self, agent: Dict) -> Dict:
        """
        Create alert for overconfident agent

        Args:
            agent: Agent performance data

        Returns:
            Alert dictionary
        """
        severity = agent["severity"]
        agent_name = agent["agent_name"]
        accuracy = agent["accuracy"]
        avg_confidence = agent["avg_confidence"]
        confidence_gap = agent["confidence_gap"]

        return {
            "type": "OVERCONFIDENT",
            "severity": severity,
            "agent_name": agent_name,
            "title": f"Overconfident Agent: {agent_name}",
            "message": (
                f"Agent '{agent_name}' is overconfident:\n"
                f"Confidence: {avg_confidence:.1%}\n"
                f"Accuracy: {accuracy:.1%}\n"
                f"Gap: {confidence_gap:+.1%}\n\n"
                f"🎭 Agent is overestimating its predictions"
            ),
            "metrics": {
                "accuracy": accuracy,
                "confidence": avg_confidence,
                "gap": confidence_gap,
            },
            "timestamp": datetime.now().isoformat()
        }

    def _send_alert(self, alert: Dict) -> None:
        """
        Send alert (log + future: Slack/Email)

        Args:
            alert: Alert dictionary
        """
        severity = alert["severity"]
        title = alert["title"]
        message = alert["message"]

        # Log alert
        if severity == "critical":
            logger.error(f"🚨 CRITICAL ALERT: {title}\n{message}")
        elif severity in ["high", "warning"]:
            logger.warning(f"⚠️ WARNING: {title}\n{message}")
        else:
            logger.info(f"ℹ️ INFO: {title}\n{message}")

        # TODO: Send to Slack
        # self._send_slack_alert(alert)

        # TODO: Send to Email
        # self._send_email_alert(alert)

    def _send_slack_alert(self, alert: Dict) -> None:
        """
        Send alert to Slack

        Args:
            alert: Alert dictionary
        """
        # Placeholder for Slack integration
        logger.info(f"📱 Slack alert: {alert['title']}")
        pass

    def _send_email_alert(self, alert: Dict) -> None:
        """
        Send alert via Email

        Args:
            alert: Alert dictionary
        """
        # Placeholder for Email integration
        logger.info(f"📧 Email alert: {alert['title']}")
        pass

    def get_alerts_summary(self) -> Dict:
        """
        Get summary of alerts sent

        Returns:
            Summary dictionary
        """
        total_alerts = len(self.alerts_sent)
        by_type = {}
        by_severity = {}

        for alert in self.alerts_sent:
            alert_type = alert["type"]
            severity = alert["severity"]

            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_alerts": total_alerts,
            "by_type": by_type,
            "by_severity": by_severity,
            "alerts": self.alerts_sent
        }


# ============================================================================
# Standalone Function
# ============================================================================

def send_performance_alerts(
    low_performers: List[Dict],
    overconfident: List[Dict]
) -> List[Dict]:
    """
    Send performance alerts (standalone function)

    Args:
        low_performers: List of low-performing agents
        overconfident: List of overconfident agents

    Returns:
        List of alerts sent
    """
    alert_system = AgentAlertSystem()
    return alert_system.check_and_send_alerts(low_performers, overconfident)


if __name__ == "__main__":
    """Test alert system"""
    logging.basicConfig(level=logging.INFO)

    # Mock data
    low_performers = [
        {
            "agent_name": "risk",
            "accuracy": 0.48,
            "total_votes": 50,
            "avg_confidence": 0.65,
            "severity": "warning"
        },
        {
            "agent_name": "macro",
            "accuracy": 0.42,
            "total_votes": 45,
            "avg_confidence": 0.70,
            "severity": "critical"
        }
    ]

    overconfident = [
        {
            "agent_name": "news",
            "accuracy": 0.55,
            "avg_confidence": 0.80,
            "confidence_gap": 0.25,
            "total_votes": 60,
            "severity": "medium"
        }
    ]

    # Send alerts
    print("\n" + "=" * 80)
    print("🚨 Sending Performance Alerts")
    print("=" * 80)

    alert_system = AgentAlertSystem()
    alerts = alert_system.check_and_send_alerts(low_performers, overconfident)

    # Summary
    print("\n📊 Alert Summary:")
    print("-" * 80)
    summary = alert_system.get_alerts_summary()
    print(f"Total alerts: {summary['total_alerts']}")
    print(f"By type: {summary['by_type']}")
    print(f"By severity: {summary['by_severity']}")
    print("-" * 80)
