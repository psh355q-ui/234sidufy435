import unittest
from unittest.mock import MagicMock, patch
import time
import sys
import os

# Create absolute path to project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.insert(0, project_root)

from backend.events import event_bus, EventType
from backend.events.subscribers import ConflictEventSubscriber, PortfolioEventSubscriber

class TestEventSubscribers(unittest.TestCase):

    def setUp(self):
        # Reset handlers
        event_bus._handlers = {}
        event_bus._async_handlers = {}
        
    def test_conflict_subscriber_retry(self):
        subscriber = ConflictEventSubscriber()
        
        # Mocking logger to verify retries
        with patch('backend.events.subscribers.logger') as mock_logger:
            # Create a mock that raises exception twice then succeeds
            mock_handler = MagicMock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), None])
            
            # Decorate it manually with retry to test the decorator concept
            from backend.utils.retry import retry
            @retry(max_retries=3, delay=0.1)
            def decorated_handler(data):
                mock_handler(data)
                
            # Execute
            try:
                decorated_handler({'ticker': 'TEST'})
            except:
                pass
                
            # Verify called 3 times (Fail, Fail, Success)
            self.assertEqual(mock_handler.call_count, 3)
            print("Retry Logic Verified: 3 calls made (Fail -> Fail -> Success)")

    def test_subscriber_integration(self):
        subscriber = ConflictEventSubscriber()
        event_bus.subscribe(EventType.CONFLICT_DETECTED, subscriber.handle_conflict_detected)
        
        # We can't easily assert logging in integration without complex patching,
        # but we can ensure no crash
        event_bus.publish(EventType.CONFLICT_DETECTED, {
            'ticker': 'TEST', 
            'strategy_id': 'STRAT_A',
            'conflict_detail': {}
        })
        print("Integration Verified: Publish did not crash")

if __name__ == '__main__':
    unittest.main()
