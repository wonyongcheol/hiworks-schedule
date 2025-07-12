# 설치 및 실행 가이드

## 🐍 Python 설치

### 1. Python 다운로드
- [Python 공식 웹사이트](https://www.python.org/downloads/)에서 최신 버전 다운로드
- **Python 3.8 이상** 권장 (3.11 또는 3.12 추천)

### 2. 설치 시 주의사항
- ✅ **"Add Python to PATH"** 체크박스 반드시 선택
- ✅ **"Install for all users"** 선택 (관리자 권한으로 설치)

### 3. 설치 확인
```bash
# 명령 프롬프트 또는 PowerShell에서
python --version
# 또는
py --version
```

## 📦 의존성 설치

### 1. 가상환경 생성 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 설치 확인
```bash
python -c "import PyQt6; print('PyQt6 설치됨')"
python -c "import selenium; print('Selenium 설치됨')"
```

## 🚀 프로그램 실행

### 1. 기본 실행
```bash
python src/main.py
```

### 2. 디버그 모드 실행
```bash
python -u src/main.py
```

### 3. 가상환경에서 실행
```bash
# 가상환경 활성화 후
venv\Scripts\activate
python src/main.py
```

## 🔧 문제 해결

### Python이 인식되지 않는 경우
1. **PATH 확인**
   ```bash
   echo $env:PATH  # PowerShell
   echo %PATH%     # CMD
   ```

2. **Python 재설치**
   - 기존 Python 제거
   - "Add Python to PATH" 옵션으로 재설치

3. **수동 PATH 추가**
   ```
   C:\Users\[사용자명]\AppData\Local\Programs\Python\Python3x\
   C:\Users\[사용자명]\AppData\Local\Programs\Python\Python3x\Scripts\
   ```

### 패키지 설치 오류
1. **pip 업그레이드**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **개별 패키지 설치**
   ```bash
   pip install PyQt6
   pip install selenium
   pip install webdriver-manager
   ```

3. **관리자 권한으로 설치**
   - PowerShell을 관리자 권한으로 실행
   - 패키지 재설치

### Chrome 브라우저 관련
1. **Chrome 브라우저 설치**
   - [Chrome 공식 웹사이트](https://www.google.com/chrome/)에서 다운로드

2. **ChromeDriver 자동 설치**
   - `webdriver-manager`가 자동으로 처리
   - 수동 설치가 필요한 경우 [ChromeDriver 다운로드](https://chromedriver.chromium.org/)

## 📋 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 이상
- **RAM**: 4GB 이상
- **저장공간**: 1GB 이상

### 권장 사항
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.11 또는 3.12
- **RAM**: 8GB 이상
- **저장공간**: 2GB 이상
- **인터넷**: 안정적인 연결

## 🎯 첫 실행 가이드

1. **프로그램 실행**
   ```bash
   python src/main.py
   ```

2. **GUI 창 확인**
   - 현대적인 다크 테마 창이 나타남
   - "하이웍스 스케줄 관리자" 제목 확인

3. **웹 접속 테스트**
   - "하이웍스 접속" 버튼 클릭
   - Chrome 브라우저가 자동으로 열림
   - 하이웍스 로그인 페이지로 이동

4. **페이지 정보 확인**
   - 페이지 정보가 실시간으로 표시됨
   - 로그 메시지 확인

## 🔍 디버깅

### 로그 확인
```bash
# 로그 파일 위치
logs/hiworks_schedule_YYYYMMDD.log
```

### 콘솔 출력 확인
```bash
python -u src/main.py 2>&1 | tee output.log
```

### 모듈 테스트
```bash
# 설정 모듈 테스트
python -c "from src.config.settings import settings; print(settings.get('hiworks.login_url'))"

# 로거 테스트
python -c "from src.utils.logger import logger; logger.info('테스트 메시지')"
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 버전 (`python --version`)
2. 설치된 패키지 (`pip list`)
3. 로그 파일 내용
4. 오류 메시지 전체 내용 