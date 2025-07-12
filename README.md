# 하이웍스 스케줄 관리자

하이웍스(Hiworks) 웹사이트에 로그인하여 스케줄 데이터를 수집하고, 카테고리별로 관리하며, 엑셀로 내보낼 수 있는 윈도우 프로그램입니다.

## 📋 주요 기능

- **자동 로그인/자격 증명 저장**: 안전하게 암호화 저장, 자동 로그인 지원
- **PyQt6 기반 현대적 GUI**: 다크/라이트 테마, 반응형 레이아웃, datepicker
- **Selenium 자동화**: 하이웍스 2단계 로그인, 일정 JSON 추출
- **카테고리별 일정 분류**: schedule, spacial, lunar, birthday 등 탭으로 구분
- **일정 테이블/JSON 동시 제공**: 탭 전환으로 표/원본 JSON 확인
- **엑셀로 저장**: 현재 보이는 카테고리별 일정 테이블을 xlsx로 저장
- **실행파일 빌드 지원**: PyInstaller로 단일 exe 생성 가능

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 프로그램 실행
```bash
python src/main.py
```

### 3. 실행파일(배포용 EXE) 만들기
#### (권장) python.org 공식 Python 사용
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --collect-all PyQt6 --paths=src src/main.py
```
- dist/main.exe 생성됨
- chromedriver.exe, config.json, resources/ 등 외부 파일도 dist 폴더에 복사 필요

#### (Microsoft Store Python은 권장하지 않음)
- 빌드/실행에 문제가 많으니 공식 Python 사용 권장

## 🎯 사용법

1. **로그인**: 아이디/비밀번호 입력, 자격 증명 저장/자동 로그인 선택 가능
2. **날짜 선택**: datepicker로 시작/종료일 지정(기본: 이번달)
3. **요청**: 일정 JSON을 받아오고, 카테고리별로 표로 정리
4. **탭 전환**: 테이블/JSON, 카테고리별 일정 전환 가능
5. **엑셀로 저장**: 각 카테고리별 표 아래 '엑셀로 저장' 버튼으로 xlsx 저장

## 🛠️ 기술 스택
- **GUI**: PyQt6
- **웹 자동화**: Selenium WebDriver, ChromeDriver
- **데이터 처리**: pandas
- **설정/로그**: JSON, Python logging

## ⚠️ 배포/실행 주의사항
- **chromedriver.exe**: dist/main.exe와 같은 폴더에 반드시 복사
- **config.json, resources/**: 필요한 리소스/설정 파일도 dist 폴더에 복사
- **PyQt6 DLL/리소스**: --collect-all PyQt6 옵션으로 빌드 권장
- **공식 Python 사용 권장**: Microsoft Store Python은 빌드/실행에 문제 많음

## 📦 프로젝트 구조(일부)
```
hiworks-schedule/
├── src/
│   ├── main.py
│   ├── gui/
│   ├── scraper/
│   ├── config/
│   └── ...
├── resources/
├── data/
├── dist/
├── requirements.txt
├── config.json
└── README.md
```

## 📝 변경 이력(주요)
- datepicker 도입, 자동 로그인, 카테고리별 탭, 엑셀 저장, 실행파일 빌드법 등 최신화