import json
import os
import base64
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

def get_app_data_dir():
    """애플리케이션 데이터 디렉토리를 반환합니다."""
    # 실행파일인지 확인
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행파일인 경우
        # 실행파일이 있는 디렉토리를 기준으로 data 폴더 생성
        app_dir = os.path.dirname(sys.executable)
        logger.info(f"실행파일 모드 - 실행파일 경로: {sys.executable}")
        logger.info(f"실행파일 모드 - 앱 디렉토리: {app_dir}")
    else:
        # 일반 Python 스크립트인 경우
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # src/utils에서 상위로 이동
        app_dir = os.path.dirname(os.path.dirname(app_dir))
        logger.info(f"Python 스크립트 모드 - 앱 디렉토리: {app_dir}")
    
    data_dir = os.path.join(app_dir, "data")
    logger.info(f"데이터 디렉토리: {data_dir}")
    return data_dir

class CredentialManager:
    """암호화된 자격 증명을 관리하는 클래스"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            self.data_dir = get_app_data_dir()
        else:
            self.data_dir = data_dir
            
        self.credentials_file = os.path.join(self.data_dir, "credentials.enc")
        self.key_file = os.path.join(self.data_dir, "key.enc")
        
        # 데이터 디렉토리 생성
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            logger.info(f"데이터 디렉토리: {self.data_dir}")
        except Exception as e:
            logger.error(f"데이터 디렉토리 생성 실패: {e}")
            # 실패 시 현재 작업 디렉토리 사용
            self.data_dir = "data"
            self.credentials_file = os.path.join(self.data_dir, "credentials.enc")
            self.key_file = os.path.join(self.data_dir, "key.enc")
            os.makedirs(self.data_dir, exist_ok=True)
        
        # 암호화 키 초기화
        self._initialize_key()
    
    def _initialize_key(self):
        """암호화 키를 초기화하거나 로드합니다."""
        if os.path.exists(self.key_file):
            # 기존 키 로드
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            # 새 키 생성
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def save_credentials(self, username, password, auto_login=False):
        """자격 증명을 암호화하여 저장합니다."""
        try:
            logger.info(f"자격 증명 저장 시도: username={username}, auto_login={auto_login}")
            logger.info(f"데이터 디렉토리: {self.data_dir}")
            logger.info(f"자격 증명 파일 경로: {self.credentials_file}")
            
            credentials = {
                'username': username,
                'password': password,
                'auto_login': auto_login
            }
            
            # JSON으로 직렬화 후 암호화
            json_data = json.dumps(credentials, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            
            logger.info(f"암호화 완료, 파일에 저장 중...")
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"자격 증명이 저장되었습니다. 사용자: {username}")
            logger.info(f"저장된 파일 크기: {len(encrypted_data)} bytes")
            return True
            
        except Exception as e:
            logger.error(f"자격 증명 저장 실패: {e}")
            logger.error(f"예외 타입: {type(e).__name__}")
            import traceback
            logger.error(f"상세 스택 트레이스: {traceback.format_exc()}")
            return False
    
    def load_credentials(self):
        """저장된 자격 증명을 로드합니다."""
        try:
            logger.info(f"자격 증명 로드 시도")
            logger.info(f"자격 증명 파일 경로: {self.credentials_file}")
            
            if not os.path.exists(self.credentials_file):
                logger.info("자격 증명 파일이 존재하지 않습니다.")
                return None
            
            logger.info(f"자격 증명 파일 크기: {os.path.getsize(self.credentials_file)} bytes")
            
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            logger.info(f"암호화된 데이터 읽기 완료, 복호화 중...")
            
            # 복호화 후 JSON 파싱
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode('utf-8'))
            
            logger.info(f"자격 증명을 로드했습니다. 사용자: {credentials['username']}")
            logger.info(f"자동 로그인 설정: {credentials.get('auto_login', False)}")
            return credentials
            
        except Exception as e:
            logger.error(f"자격 증명 로드 실패: {e}")
            logger.error(f"예외 타입: {type(e).__name__}")
            import traceback
            logger.error(f"상세 스택 트레이스: {traceback.format_exc()}")
            return None
    
    def delete_credentials(self):
        """저장된 자격 증명을 삭제합니다."""
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                logger.info("저장된 자격 증명이 삭제되었습니다.")
                return True
            return False
            
        except Exception as e:
            logger.error(f"자격 증명 삭제 실패: {e}")
            return False
    
    def has_saved_credentials(self):
        """저장된 자격 증명이 있는지 확인합니다."""
        return os.path.exists(self.credentials_file)
    
    def get_auto_login_status(self):
        """자동 로그인 설정 상태를 반환합니다."""
        credentials = self.load_credentials()
        if credentials:
            return credentials.get('auto_login', False) 