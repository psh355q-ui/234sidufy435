"""
데이터 수집 모니터링 스크립트

실시간으로 데이터 수집 진행 상황을 모니터링합니다.

Author: AI Trading System
Date: 2025-12-28
"""

import sys
import os
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent.parent
root_path = backend_path.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(backend_path))

import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.WARNING)  # 모니터 출력만 표시


class CollectionMonitor:
    """
    데이터 수집 진행 상황 모니터
    
    기능:
    - 실시간 진행률 표시
    - ETA 계산
    - 통계 대시보드
    - 최근 에러 표시
    """
    
    def __init__(self, task_name: str = "14day_collection", refresh_interval: int = 5):
        self.task_name = task_name
        self.refresh_interval = refresh_interval
    
    async def get_progress(self) -> dict:
        """DB에서 진행 상황 조회"""
        # TODO: 실제 DB 조회 구현
        # 현재는 mock 데이터
        
        import random
        
        # 시뮬레이션: 진행 중인 상태
        total_items = 1008  # 3 tickers × 24 hours × 14 days
        items_processed = random.randint(100, 500)
        progress_pct = (items_processed / total_items) * 100
        
        total_cycles = 336  # 24 hours × 14 days
        current_cycle = random.randint(50, 150)
        successful_cycles = current_cycle - random.randint(0, 2)
        failed_cycles = current_cycle - successful_cycles
        
        # ETA 계산
        if items_processed > 0:
            elapsed_hours = random.uniform(5, 10)
            rate_per_hour = items_processed / elapsed_hours
            remaining_items = total_items - items_processed
            eta_hours = remaining_items / rate_per_hour
            eta = datetime.now() + timedelta(hours=eta_hours)
        else:
            eta = None
        
        return {
            "task_name": self.task_name,
            "status": "running",
            "progress_pct": progress_pct,
            "items_processed": items_processed,
            "items_total": total_items,
            "current_cycle": current_cycle,
            "total_cycles": total_cycles,
            "successful_cycles": successful_cycles,
            "failed_cycles": failed_cycles,
            "success_rate": (successful_cycles / max(current_cycle, 1)) * 100,
            "avg_collection_time": round(random.uniform(2.0, 3.5), 1),
            "last_update": datetime.now(),
            "eta": eta,
            "recent_errors": [
                f"사이클 {random.randint(1, current_cycle)}: NVDA FinViz 타임아웃 (재시도 성공)"
            ] if random.random() > 0.7 else []
        }
    
    def display_dashboard(self, progress: dict):
        """대시보드 출력"""
        # 화면 클리어 (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("14일 데이터 수집 모니터".center(80))
        print("=" * 80)
        print()
        
        print(f"작업명: {progress['task_name']}")
        print(f"상태: {progress['status']}")
        print(f"진행률: {progress['progress_pct']:.1f}% ({progress['items_processed']:,} / {progress['items_total']:,} 항목)")
        
        if progress['eta']:
            eta_str = progress['eta'].strftime('%Y-%m-%d %H:%M:%S')
            remaining = progress['eta'] - datetime.now()
            days = remaining.days
            hours = remaining.seconds // 3600
            print(f"예상 완료: {eta_str} ({days}일 {hours}시간 후)")
        else:
            print(f"예상 완료: 계산 중...")
        
        print()
        print(f"현재 사이클: {progress['current_cycle']} / {progress['total_cycles']}")
        print(f"성공률: {progress['success_rate']:.1f}% ({progress['successful_cycles']} / {progress['current_cycle']})")
        print(f"실패한 사이클: {progress['failed_cycles']}")
        print(f"평균 수집 시간: {progress['avg_collection_time']}초/사이클")
        
        print()
        print(f"마지막 업데이트: {progress['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 다음 사이클 계산 (예시)
        if progress['current_cycle'] < progress['total_cycles']:
            next_cycle = datetime.now() + timedelta(hours=1)
            time_to_next = next_cycle - datetime.now()
            minutes = time_to_next.seconds // 60
            seconds = time_to_next.seconds % 60
            print(f"다음 사이클: {next_cycle.strftime('%Y-%m-%d %H:%M:%S')} ({minutes}분 {seconds}초 후)")
        
        # 최근 에러
        if progress['recent_errors']:
            print()
            print("최근 에러:")
            for error in progress['recent_errors'][-5:]:  # 최근 5개만
                print(f"  - {error}")
        
        print()
        print("=" * 80)
        print(f"새로고침: {self.refresh_interval}초마다 자동 업데이트 (Ctrl+C로 종료)")
        print("=" * 80)
    
    async def start(self):
        """모니터링 시작"""
        print("데이터 수집 모니터 시작...")
        print(f"작업명: {self.task_name}")
        print(f"새로고침 간격: {self.refresh_interval}초")
        print()
        
        try:
            while True:
                # 진행 상황 조회
                progress = await self.get_progress()
                
                # 대시보드 표시
                self.display_dashboard(progress)
                
                # 완료 확인
                if progress['status'] == 'completed':
                    print("\n✅ 데이터 수집 완료!")
                    break
                
                # 대기
                await asyncio.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n모니터 종료")


def main():
    """메인 엔트리 포인트"""
    parser = argparse.ArgumentParser(description="Data Collection Monitor")
    
    parser.add_argument(
        "--task-name",
        default="14day_collection",
        help="Task name to monitor (default: 14day_collection)"
    )
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )
    
    args = parser.parse_args()
    
    monitor = CollectionMonitor(
        task_name=args.task_name,
        refresh_interval=args.refresh_interval
    )
    
    asyncio.run(monitor.start())


if __name__ == "__main__":
    main()
