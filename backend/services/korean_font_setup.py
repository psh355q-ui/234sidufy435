"""
Korean Font Setup for ReportLab

한글 폰트 등록 유틸리티
- 무료 폰트: NanumGothic (구글 폰트)
- Windows 기본 폰트: Malgun Gothic
"""
import os
import logging
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

logger = logging.getLogger(__name__)


def register_korean_fonts():
    """
    한글 폰트 등록
    
    우선순위:
    1. Windows 시스템 폰트 (Malgun Gothic)
    2. 프로젝트 fonts 폴더
    3. Fallback: DejaVu Sans (제한적 한글 지원)
    """
    try:
        # Windows 시스템 폰트 경로
        windows_fonts = Path("C:/Windows/Fonts")
        
        # 맑은 고딕 (Windows 기본 한글 폰트)
        malgun_path = windows_fonts / "malgun.ttf"
        malgun_bold_path = windows_fonts / "malgunbd.ttf"
        
        if malgun_path.exists():
            pdfmetrics.registerFont(TTFont('Korean', str(malgun_path)))
            logger.info("✅ Registered Korean font: Malgun Gothic")
            
            if malgun_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Korean-Bold', str(malgun_bold_path)))
                logger.info("✅ Registered Korean-Bold font: Malgun Gothic Bold")
            else:
                # Bold가 없으면 Regular를 Bold로도 사용
                pdfmetrics.registerFont(TTFont('Korean-Bold', str(malgun_path)))
                logger.warning("⚠️ Using regular font for Korean-Bold")
            
            return True
        
        # Fallback: NanumGothic (프로젝트 폴더)
        project_fonts = Path(__file__).parent.parent.parent / "fonts"
        nanum_path = project_fonts / "NanumGothic.ttf"
        
        if nanum_path.exists():
            pdfmetrics.registerFont(TTFont('Korean', str(nanum_path)))
            logger.info("✅ Registered Korean font: NanumGothic")
            return True
        
        # Fallback: DejaVu Sans (제한적)
        logger.warning("⚠️ No Korean font found. Using DejaVu Sans (limited Korean support)")
        pdfmetrics.registerFont(TTFont('Korean', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('Korean-Bold', 'DejaVuSans-Bold.ttf'))
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to register Korean font: {e}")
        # Fallback to Helvetica (will show boxes for Korean)
        logger.error("Using Helvetica as fallback (Korean text will not display correctly)")
        return False


def get_korean_font_name(bold: bool = False) -> str:
    """
    등록된 한글 폰트 이름 반환
    
    Args:
        bold: Bold 폰트 필요 여부
    
    Returns:
        폰트 이름
    """
    if bold:
        return 'Korean-Bold'
    return 'Korean'


# Auto-register on import
_fonts_registered = False

def ensure_fonts_registered():
    """폰트가 등록되었는지 확인하고 없으면 등록"""
    global _fonts_registered
    if not _fonts_registered:
        register_korean_fonts()
        _fonts_registered = True


# Test function
if __name__ == "__main__":
    print("="*60)
    print("Korean Font Registration Test")
    print("="*60)
    
    success = register_korean_fonts()
    
    if success:
        print("\n✅ Korean font registered successfully!")
        print(f"Font name: {get_korean_font_name()}")
        print(f"Font name (bold): {get_korean_font_name(bold=True)}")
    else:
        print("\n⚠️ Korean font registration failed or using fallback")
    
    # Test PDF generation
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    
    test_style = ParagraphStyle(
        'TestKorean',
        fontName=get_korean_font_name(),
        fontSize=12
    )
    
    doc = SimpleDocTemplate("test_korean_font.pdf", pagesize=A4)
    story = [
        Paragraph("안녕하세요! AI Trading System", test_style),
        Paragraph("한글 테스트: 오늘 시장은 강세였습니다.", test_style),
        Paragraph("숫자 테스트: 1,234.56 원 (+2.5%)", test_style),
    ]
    
    doc.build(story)
    print("\n✅ Test PDF created: test_korean_font.pdf")
    print("Open it to verify Korean text displays correctly!")
