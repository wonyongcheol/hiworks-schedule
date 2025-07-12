import json
import os
import sys
from typing import Dict, Any


def get_app_config_dir():
    """애플리케이션 설정 디렉토리를 반환합니다."""
    # 실행파일인지 확인
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행파일인 경우
        app_dir = os.path.dirname(sys.executable)
    else:
        # 일반 Python 스크립트인 경우
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # src/config에서 상위로 이동
        app_dir = os.path.dirname(os.path.dirname(app_dir))
    
    return app_dir


class Settings:
    """애플리케이션 설정을 관리하는 클래스"""
    
    def __init__(self, config_file: str = ""):
        if not config_file:
            app_dir = get_app_config_dir()
            self.config_file = os.path.join(app_dir, "config.json")
        else:
            self.config_file = config_file
            
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일을 로드합니다."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"설정 파일 로드 중 오류: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정을 반환합니다."""
        return {
            "hiworks": {
                "login_url": "https://login.office.hiworks.com/",
                "timeout": 30,
                "retry_count": 3
            },
            "gui": {
                "theme": "dark",
                "window_size": [1200, 800],
                "auto_login": False
            },
            "data": {
                "export_path": "./data/exports/",
                "auto_save": True,
                "excel_format": "xlsx"
            },
            "logging": {
                "level": "INFO",
                "file_path": "./logs/"
            }
        }
    
    def save_config(self):
        """설정을 파일에 저장합니다."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 파일 저장 중 오류: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값을 가져옵니다."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """설정 값을 설정합니다."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()


# 전역 설정 인스턴스
settings = Settings() 