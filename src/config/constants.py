# 애플리케이션 상수 정의

# 하이웍스 관련 상수
HIWORKS_LOGIN_URL = "https://login.office.hiworks.com/"
HIWORKS_DOMAIN = "office.hiworks.com"

# GUI 관련 상수
APP_NAME = "하이웍스 스케줄 관리자"
APP_VERSION = "1.0.0"
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

# 테마 관련 상수
THEME_DARK = "dark"
THEME_LIGHT = "light"

# 파일 확장자
EXCEL_EXTENSIONS = [".xlsx", ".xls"]
CSV_EXTENSIONS = [".csv"]

# 로그 레벨
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# 타임아웃 설정 (초)
DEFAULT_TIMEOUT = 30
LOGIN_TIMEOUT = 60
PAGE_LOAD_TIMEOUT = 30

# 재시도 설정
MAX_RETRY_COUNT = 3
RETRY_DELAY = 2

# 데이터 관련 상수
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_FORMAT = "%H:%M:%S"
DEFAULT_DATETIME_FORMAT = f"{DEFAULT_DATE_FORMAT} {DEFAULT_TIME_FORMAT}"

# 색상 코드 (다크 테마)
DARK_COLORS = {
    "background": "#2b2b2b",
    "surface": "#3c3c3c",
    "primary": "#007acc",
    "secondary": "#6c757d",
    "text": "#ffffff",
    "text_secondary": "#b0b0b0",
    "border": "#555555",
    "error": "#dc3545",
    "success": "#28a745",
    "warning": "#ffc107"
}

# 색상 코드 (라이트 테마)
LIGHT_COLORS = {
    "background": "#f8f9fa",
    "surface": "#ffffff",
    "primary": "#007acc",
    "secondary": "#6c757d",
    "text": "#212529",
    "text_secondary": "#6c757d",
    "border": "#dee2e6",
    "error": "#dc3545",
    "success": "#28a745",
    "warning": "#ffc107"
} 