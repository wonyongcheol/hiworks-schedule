import logging
import os
import sys
from datetime import datetime
from typing import Optional
from config.settings import settings


def get_app_log_dir():
    """애플리케이션 로그 디렉토리를 반환합니다."""
    # 실행파일인지 확인
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행파일인 경우
        app_dir = os.path.dirname(sys.executable)
    else:
        # 일반 Python 스크립트인 경우
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # src/utils에서 상위로 이동
        app_dir = os.path.dirname(os.path.dirname(app_dir))
    
    log_dir = os.path.join(app_dir, "logs")
    return log_dir


class Logger:
    """애플리케이션 로깅을 관리하는 클래스"""
    
    def __init__(self, name: str = "hiworks_schedule"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """로거를 설정합니다."""
        logger = logging.getLogger(self.name)
        
        # 이미 핸들러가 설정되어 있으면 중복 설정 방지
        if logger.handlers:
            return logger
        
        # 로그 레벨 설정
        log_level = settings.get("logging.level", "INFO")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 파일 핸들러 설정
        try:
            log_path = get_app_log_dir()
            if not os.path.exists(log_path):
                os.makedirs(log_path, exist_ok=True)
            
            log_file = os.path.join(log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # 로그 파일 생성 실패 시 콘솔만 사용
            print(f"로그 파일 생성 실패: {e}")
        
        return logger
    
    def debug(self, message: str):
        """디버그 로그를 기록합니다."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """정보 로그를 기록합니다."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """경고 로그를 기록합니다."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """에러 로그를 기록합니다."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """치명적 오류 로그를 기록합니다."""
        self.logger.critical(message)
    
    def log_web_action(self, action: str, url: str, status: str = "success", error: Optional[str] = None):
        """웹 액션 로그를 기록합니다."""
        message = f"Web Action: {action} | URL: {url} | Status: {status}"
        if error:
            message += f" | Error: {error}"
        
        if status == "success":
            self.info(message)
        else:
            self.error(message)


# 전역 로거 인스턴스
logger = Logger() 