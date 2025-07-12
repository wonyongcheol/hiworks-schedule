#!/usr/bin/env python3
"""
하이웍스 스케줄 관리자 - 메인 실행 파일
"""

import sys
import os
from pathlib import Path

# 현재 파일의 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # 절대 import로 변경
    from gui.main_window import main as gui_main
    from utils.logger import logger
    from config.settings import settings
    
    def main():
        """메인 함수"""
        try:
            logger.info("하이웍스 스케줄 관리자를 시작합니다.")
            
            # 설정 로드 확인
            logger.info("설정을 로드했습니다.")
            
            # GUI 애플리케이션 시작
            gui_main()
            
        except KeyboardInterrupt:
            logger.info("사용자에 의해 프로그램이 중단되었습니다.")
        except Exception as e:
            logger.critical(f"프로그램 실행 중 치명적 오류 발생: {e}")
            sys.exit(1)
        finally:
            logger.info("프로그램을 종료합니다.")

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import 오류: {e}")
    print("Python 경로:", sys.path)
    sys.exit(1)
except Exception as e:
    print(f"오류 발생: {e}")
    sys.exit(1) 