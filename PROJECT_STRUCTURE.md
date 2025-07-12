# 하이웍스 스케줄 프로그램 - 프로젝트 구조

## 📋 프로젝트 개요
- **목적**: 하이웍스(https://login.office.hiworks.com/) 로그인 후 스케줄 데이터 수집
- **GUI**: 현대적인 디자인의 윈도우 애플리케이션
- **데이터 처리**: 실시간 조회 및 Excel 저장 기능

## 🏗️ 프로젝트 구조

```
hiworks-schedule/
├── src/
│   ├── main.py                    # 메인 실행 파일
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # 메인 GUI 창 (PyQt6)
│   │   ├── login_dialog.py        # 로그인 다이얼로그
│   │   ├── data_viewer.py         # 데이터 조회 창
│   │   └── styles/
│   │       ├── __init__.py
│   │       ├── dark_theme.py      # 다크 테마 스타일
│   │       └── light_theme.py     # 라이트 테마 스타일
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── hiworks_scraper.py     # 하이웍스 전용 스크래퍼
│   │   ├── login_handler.py       # 로그인 처리 로직
│   │   └── schedule_extractor.py  # 스케줄 데이터 추출
│   ├── data/
│   │   ├── __init__.py
│   │   ├── excel_exporter.py      # Excel 저장 기능
│   │   └── data_processor.py      # 데이터 처리 및 정리
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # 설정 관리
│   │   └── constants.py           # 상수 정의
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # 로깅 시스템
│       └── helpers.py             # 유틸리티 함수
├── resources/
│   ├── icons/                     # 아이콘 파일들
│   ├── images/                    # 이미지 파일들
│   └── styles/                    # QSS 스타일시트
├── data/                          # 저장된 데이터 폴더
│   ├── schedules/                 # 스케줄 데이터
│   └── exports/                   # Excel 내보내기 파일
├── logs/                          # 로그 파일 저장
├── requirements.txt               # Python 의존성
├── config.json                    # 설정 파일
├── .gitignore
├── README.md
└── PROJECT_STRUCTURE.md
```

## 🛠️ 기술 스택

### GUI 프레임워크
- **PyQt6**: 현대적이고 아름다운 GUI 구현
- **QSS (Qt Style Sheets)**: 커스텀 스타일링
- **Qt Designer**: GUI 레이아웃 디자인

### 웹 스크래핑
- **Selenium WebDriver**: 동적 콘텐츠 처리 (하이웍스는 SPA)
- **ChromeDriver**: 브라우저 자동화
- **BeautifulSoup4**: HTML 파싱 (필요시)

### 데이터 처리
- **pandas**: 데이터 조작 및 분석
- **openpyxl**: Excel 파일 생성 및 편집
- **xlsxwriter**: 고급 Excel 기능

### 기타 라이브러리
- **requests**: HTTP 요청
- **lxml**: XML/HTML 파싱
- **python-dotenv**: 환경변수 관리
- **schedule**: 작업 스케줄링 (필요시)

## 📦 주요 기능 모듈

### 1. GUI 모듈 (`src/gui/`)
- **main_window.py**: 메인 애플리케이션 창
  - 현대적인 다크/라이트 테마 지원
  - 반응형 레이아웃
  - 메뉴바 및 툴바
  
- **login_dialog.py**: 로그인 인터페이스
  - 하이웍스 로그인 폼
  - 자동 로그인 옵션
  - 보안 토큰 저장

- **data_viewer.py**: 데이터 조회 창
  - 테이블 형태로 스케줄 표시
  - 필터링 및 정렬 기능
  - 실시간 데이터 새로고침

### 2. 스크래핑 모듈 (`src/scraper/`)
- **hiworks_scraper.py**: 하이웍스 전용 스크래퍼
  - 로그인 세션 관리
  - 페이지 네비게이션
  - 데이터 추출 로직

- **login_handler.py**: 인증 처리
  - 로그인 상태 확인
  - 세션 유지
  - 에러 처리

- **schedule_extractor.py**: 스케줄 데이터 추출
  - 특정 위치 데이터 파싱
  - 데이터 정규화
  - 중복 제거

### 3. 데이터 모듈 (`src/data/`)
- **excel_exporter.py**: Excel 내보내기
  - 다양한 Excel 형식 지원
  - 자동 포맷팅
  - 차트 생성 (필요시)

- **data_processor.py**: 데이터 처리
  - 데이터 정리 및 변환
  - 통계 계산
  - 데이터 검증

## 🎨 UI/UX 설계

### 디자인 원칙
- **Material Design** 또는 **Fluent Design** 스타일
- **다크/라이트 테마** 자동 전환
- **반응형 레이아웃** 지원
- **직관적인 네비게이션**

### 주요 화면
1. **로그인 화면**: 깔끔한 로그인 폼
2. **메인 대시보드**: 스케줄 개요 및 통계
3. **데이터 조회 화면**: 상세 스케줄 테이블
4. **설정 화면**: 프로그램 설정 관리

## 🔧 설정 관리

### config.json 구조
```json
{
  "hiworks": {
    "login_url": "https://login.office.hiworks.com/",
    "timeout": 30,
    "retry_count": 3
  },
  "gui": {
    "theme": "dark",
    "window_size": [1200, 800],
    "auto_login": false
  },
  "data": {
    "export_path": "./data/exports/",
    "auto_save": true,
    "excel_format": "xlsx"
  },
  "logging": {
    "level": "INFO",
    "file_path": "./logs/"
  }
}
```

## 🚀 실행 방법

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **ChromeDriver 설치**
   - Chrome 브라우저 버전에 맞는 ChromeDriver 다운로드
   - PATH에 추가 또는 프로젝트 폴더에 배치

3. **프로그램 실행**
   ```bash
   python src/main.py
   ```

## 📝 개발 단계

### Phase 1: 기본 구조
- [ ] 프로젝트 구조 생성
- [ ] 기본 GUI 프레임워크 설정
- [ ] 설정 파일 구조 정의

### Phase 2: 로그인 기능
- [ ] 하이웍스 로그인 구현
- [ ] 세션 관리 로직
- [ ] 로그인 GUI 구현

### Phase 3: 데이터 스크래핑
- [ ] 스케줄 페이지 접근
- [ ] 데이터 추출 로직
- [ ] 데이터 정리 및 변환

### Phase 4: GUI 완성
- [ ] 메인 창 구현
- [ ] 데이터 조회 화면
- [ ] Excel 내보내기 기능

### Phase 5: 최적화
- [ ] 성능 최적화
- [ ] 에러 처리 강화
- [ ] 사용자 경험 개선

## 🔒 보안 고려사항

- **자격 증명 암호화** 저장
- **HTTPS 통신** 보장
- **세션 토큰** 안전한 관리
- **로컬 데이터** 암호화 (필요시)

## 📊 데이터 구조

### 스케줄 데이터 예시
```python
{
    "date": "2024-01-15",
    "time": "09:00-18:00",
    "title": "회의",
    "description": "팀 미팅",
    "location": "회의실 A",
    "attendees": ["김철수", "이영희"],
    "status": "confirmed"
}
```

이 구조로 개발을 시작하시겠습니까? 특정 부분에 대해 더 자세한 설명이 필요하시면 말씀해 주세요! 