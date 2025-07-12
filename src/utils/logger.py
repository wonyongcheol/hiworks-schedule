import logging
import os
from datetime import datetime
from typing import Optional
from config.settings import settings


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
        log_path = settings.get("logging.file_path", "./logs/")
        if log_path and not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        
        if log_path:
            log_file = os.path.join(log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
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