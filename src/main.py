#!/usr/bin/env python3
"""
하이웍스 스케줄 관리자 - 메인 실행 파일
"""

import sys
import os
import traceback
import datetime
from pathlib import Path

# 로그 파일 경로 설정
def get_error_log_path():
    if getattr(sys, 'frozen', False):
        # 실행파일일 때
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(app_dir)
    log_dir = os.path.join(app_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "error.log")

ERROR_LOG_PATH = get_error_log_path()

# 로그 파일 설정
def setup_logging():
    """로깅 설정"""
    try:
        with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(f"=== 하이웍스 스케줄러 시작 로그 ===\n")
            f.write(f"시작 시간: {datetime.datetime.now()}\n")
            f.write(f"Python 버전: {sys.version}\n")
            f.write(f"실행 경로: {os.getcwd()}\n")
            f.write(f"sys.path: {sys.path}\n")
            f.write("=" * 50 + "\n")
    except Exception as e:
        print(f"로그 파일 생성 실패: {e}")

# 전역 예외 처리
def excepthook(exc_type, exc_value, exc_tb):
    """전역 예외 처리"""
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n=== 예외 발생 ===\n")
            f.write(f"발생 시간: {datetime.datetime.now()}\n")
            f.write(f"예외 타입: {exc_type.__name__}\n")
            f.write(f"예외 메시지: {exc_value}\n")
            f.write("상세 스택 트레이스:\n")
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
            f.write("=" * 50 + "\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")
    sys.exit(1)

# 로깅 설정 및 예외 처리 등록
setup_logging()
sys.excepthook = excepthook

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
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n=== Import 오류 ===\n")
            f.write(f"발생 시간: {datetime.datetime.now()}\n")
            f.write(f"Import 오류: {e}\n")
            f.write(f"Python 경로: {sys.path}\n")
            f.write("=" * 50 + "\n")
    except:
        pass
    print(f"Import 오류: {e}")
    print("Python 경로:", sys.path)
    sys.exit(1)
except Exception as e:
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n=== 일반 오류 ===\n")
            f.write(f"발생 시간: {datetime.datetime.now()}\n")
            f.write(f"오류: {e}\n")
            f.write("상세 스택 트레이스:\n")
            traceback.print_exception(type(e), e, e.__traceback__, file=f)
            f.write("=" * 50 + "\n")
    except:
        pass
    print(f"오류 발생: {e}")
    sys.exit(1) 