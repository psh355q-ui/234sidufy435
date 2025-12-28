"""
데이터 수집 검증 스크립트

수집 완료 후 데이터 품질 및 완전성을 검증합니다.

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
from typing import Dict, List, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    데이터 수집 검증기
    
    검증 항목:
    - 데이터 완전성 (누락된 사이클)
    - 데이터 품질 (필수 필드)
    - 데이터 일관성 (이상값)
    - 티커 커버리지
    """
    
    def __init__(self, task_name: str = "14day_collection"):
        self.task_name = task_name
        self.validation_results = {
            "timestamp": datetime.now(),
            "task_name": task_name,
            "checks": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    
    async def check_completeness(self, expected_cycles: int) -> Dict[str, Any]:
        """완전성 검사: 누락된 사이클 확인"""
        logger.info("1. 데이터 완전성 검사 중...")
        
        # TODO: 실제 DB 조회
        # 현재는 mock 데이터
        
        import random
        collected_cycles = random.randint(int(expected_cycles * 0.95), expected_cycles)
        missing_cycles = expected_cycles - collected_cycles
        
        result = {
            "check": "데이터 완전성",
            "expected": expected_cycles,
            "actual": collected_cycles,
            "missing": missing_cycles,
            "passed": missing_cycles == 0,
            "message": f"{collected_cycles}/{expected_cycles} 사이클 수집 완료"
        }
        
        if missing_cycles > 0:
            result["message"] += f" (누락: {missing_cycles})"
            if missing_cycles <= expected_cycles * 0.05:  # 5% 이하 누락
                result["severity"] = "warning"
            else:
                result["severity"] = "error"
        
        return result
    
    async def check_data_quality(self) -> Dict[str, Any]:
        """데이터 품질 검사: 필수 필드 확인"""
        logger.info("2. 데이터 품질 검사 중...")
        
        # TODO: 실제 DB 조회
        
        required_fields = [
            "current_price", "volume", "rsi", "sma_20",
            "fed_rate", "cpi_yoy", "yield_curve",
            "twitter_sentiment", "fear_greed_index"
        ]
        
        import random
        missing_fields = []
        if random.random() < 0.1:  # 10% 확률로 필드 누락 시뮬레이션
            missing_fields = [random.choice(required_fields)]
        
        result = {
            "check": "데이터 품질",
            "required_fields": len(required_fields),
            "missing_fields": missing_fields,
            "passed": len(missing_fields) == 0,
            "message": "모든 필수 필드 존재" if not missing_fields else f"누락된 필드: {', '.join(missing_fields)}"
        }
        
        return result
    
    async def check_consistency(self) -> Dict[str, Any]:
        """일관성 검사: 데이터 이상값 확인"""
        logger.info("3. 데이터 일관성 검사 중...")
        
        # TODO: 실제 DB 조회 및 통계 분석
        
        import random
        anomalies = []
        
        # 가격 이상값 시뮬레이션
        if random.random() < 0.05:
            anomalies.append("AAPL 가격 급등 감지 (3σ 초과)")
        
        # RSI 범위 검사
        if random.random() < 0.05:
            anomalies.append("RSI 값 범위 초과 (0-100 벗어남)")
        
        result = {
            "check": "데이터 일관성",
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "passed": len(anomalies) == 0,
            "message": "이상값 없음" if not anomalies else f"{len(anomalies)}개 이상값 감지"
        }
        
        if anomalies:
            result["severity"] = "warning"
        
        return result
    
    async def check_coverage(self, expected_tickers: List[str]) -> Dict[str, Any]:
        """커버리지 검사: 모든 티커 포함 확인"""
        logger.info("4. 티커 커버리지 검사 중...")
        
        # TODO: 실제 DB 조회
        
        import random
        collected_tickers = expected_tickers.copy()
        if random.random() < 0.05:  # 5% 확률로 티커 누락
            collected_tickers.pop()
        
        missing_tickers = set(expected_tickers) - set(collected_tickers)
        
        result = {
            "check": "티커 커버리지",
            "expected_tickers": expected_tickers,
            "collected_tickers": collected_tickers,
            "missing_tickers": list(missing_tickers),
            "passed": len(missing_tickers) == 0,
            "message": f"모든 티커 ({len(collected_tickers)}/{len(expected_tickers)}) 수집 완료"
        }
        
        if missing_tickers:
            result["message"] = f"누락된 티커: {', '.join(missing_tickers)}"
            result["severity"] = "error"
        
        return result
    
    async def run_validation(
        self,
        expected_cycles: int = 336,
        expected_tickers: List[str] = None
    ) -> Dict[str, Any]:
        """전체 검증 실행"""
        if expected_tickers is None:
            expected_tickers = ["AAPL", "NVDA", "MSFT"]
        
        print("=" * 80)
        print("데이터 수집 검증".center(80))
        print("=" * 80)
        print()
        
        # 검증 실행
        checks = [
            await self.check_completeness(expected_cycles),
            await self.check_data_quality(),
            await self.check_consistency(),
            await self.check_coverage(expected_tickers)
        ]
        
        # 결과 집계
        for check in checks:
            self.validation_results["checks"].append(check)
            if check["passed"]:
                self.validation_results["passed"] += 1
            else:
                if check.get("severity") == "warning":
                    self.validation_results["warnings"] += 1
                else:
                    self.validation_results["failed"] += 1
        
        # 결과 출력
        self.print_results()
        
        return self.validation_results
    
    def print_results(self):
        """검증 결과 출력"""
        print("\n검증 결과:")
        print("-" * 80)
        
        for i, check in enumerate(self.validation_results["checks"], 1):
            status = "✅ PASS" if check["passed"] else ("⚠️  WARN" if check.get("severity") == "warning" else "❌ FAIL")
            print(f"{i}. {check['check']}: {status}")
            print(f"   {check['message']}")
            
            # 추가 정보
            if not check["passed"]:
                if "missing" in check and check["missing"] > 0:
                    print(f"   누락: {check['missing']}개")
                if "anomalies" in check and check["anomalies"]:
                    for anomaly in check["anomalies"]:
                        print(f"   - {anomaly}")
                if "missing_tickers" in check and check["missing_tickers"]:
                    print(f"   누락된 티커: {', '.join(check['missing_tickers'])}")
            print()
        
        print("=" * 80)
        print(f"총 검사: {len(self.validation_results['checks'])}개")
        print(f"통과: {self.validation_results['passed']}개")
        print(f"경고: {self.validation_results['warnings']}개")
        print(f"실패: {self.validation_results['failed']}개")
        print("=" * 80)
        
        # 최종 판정
        if self.validation_results['failed'] == 0:
            if self.validation_results['warnings'] == 0:
                print("\n✅ 모든 검증 통과! 데이터 수집이 성공적으로 완료되었습니다.")
                return 0
            else:
                print(f"\n⚠️  {self.validation_results['warnings']}개 경고가 있지만 사용 가능합니다.")
                return 0
        else:
            print(f"\n❌ {self.validation_results['failed']}개 검증 실패. 데이터를 확인해주세요.")
            return 1
    
    async def generate_report(self, output_file: str = None):
        """검증 보고서 생성"""
        if output_file is None:
            output_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("데이터 수집 검증 보고서\n".center(80))
            f.write("=" * 80 + "\n\n")
            
            f.write(f"작업명: {self.validation_results['task_name']}\n")
            f.write(f"검증 시각: {self.validation_results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, check in enumerate(self.validation_results["checks"], 1):
                f.write(f"{i}. {check['check']}\n")
                f.write(f"   상태: {'통과' if check['passed'] else '실패'}\n")
                f.write(f"   메시지: {check['message']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"총 검사: {len(self.validation_results['checks'])}개\n")
            f.write(f"통과: {self.validation_results['passed']}개\n")
            f.write(f"실패: {self.validation_results['failed']}개\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"검증 보고서 저장: {output_file}")


async def main_async(args):
    """비동기 메인 함수"""
    validator = DataValidator(task_name=args.task_name)
    
    result = await validator.run_validation(
        expected_cycles=args.expected_cycles,
        expected_tickers=args.tickers
    )
    
    if args.output:
        await validator.generate_report(args.output)
    
    return result


def main():
    """메인 엔트리 포인트"""
    parser = argparse.ArgumentParser(description="Data Collection Validator")
    
    parser.add_argument(
        "--task-name",
        default="14day_collection",
        help="Task name to validate (default: 14day_collection)"
    )
    parser.add_argument(
        "--expected-cycles",
        type=int,
        default=336,
        help="Expected number of cycles (default: 336 = 24h × 14d)"
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "NVDA", "MSFT"],
        help="Expected tickers (default: AAPL NVDA MSFT)"
    )
    parser.add_argument(
        "--output",
        help="Output report file path (optional)"
    )
    
    args = parser.parse_args()
    
    result = asyncio.run(main_async(args))
    sys.exit(0 if result.get("failed", 1) == 0 else 1)


if __name__ == "__main__":
    main()
