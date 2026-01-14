"""
Simple Retry Decorator
Utilities

작성일: 2026-01-12
"""

import time
import functools
import logging

logger = logging.getLogger(__name__)

def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    데코레이터: 예외 발생 시 재시도
    
    Args:
        max_retries (int): 최대 재시도 횟수
        delay (int): 초기 대기 시간 (초)
        backoff (int): 대기 시간 증가 배수
        exceptions (tuple): 재시도할 예외 타입들
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = max_retries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    msg = f"⚠️ [RETRY] {func.__name__} failed: {e}. Retrying in {mdelay}s..."
                    logger.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator
