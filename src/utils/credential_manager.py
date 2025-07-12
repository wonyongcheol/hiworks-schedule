import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """암호화된 자격 증명을 관리하는 클래스"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.credentials_file = os.path.join(data_dir, "credentials.enc")
        self.key_file = os.path.join(data_dir, "key.enc")
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
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
            credentials = {
                'username': username,
                'password': password,
                'auto_login': auto_login
            }
            
            # JSON으로 직렬화 후 암호화
            json_data = json.dumps(credentials, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"자격 증명이 저장되었습니다. 사용자: {username}")
            return True
            
        except Exception as e:
            logger.error(f"자격 증명 저장 실패: {e}")
            return False
    
    def load_credentials(self):
        """저장된 자격 증명을 로드합니다."""
        try:
            if not os.path.exists(self.credentials_file):
                return None
            
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            # 복호화 후 JSON 파싱
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode('utf-8'))
            
            logger.info(f"자격 증명을 로드했습니다. 사용자: {credentials['username']}")
            return credentials
            
        except Exception as e:
            logger.error(f"자격 증명 로드 실패: {e}")
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