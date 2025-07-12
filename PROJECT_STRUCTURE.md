# 하이웍스 스케줄 프로그램 - 프로젝트 구조 (최신)

## 📋 프로젝트 개요
- **목적**: 하이웍스(https://login.office.hiworks.com/) 로그인 후 스케줄 데이터 수집/분류/엑셀 저장
- **GUI**: PyQt6 기반, 현대적 디자인, datepicker, 카테고리별 탭, 엑셀 저장
- **실행파일 빌드**: PyInstaller로 단일 exe 생성 지원

## 🏗️ 프로젝트 구조 (예시)
```
hiworks-schedule/
├── src/
│   ├── main.py                # 메인 실행 파일
│   ├── gui/
│   │   └── main_window.py     # 메인 GUI 창
│   ├── scraper/
│   │   └── hiworks_scraper.py # 하이웍스 자동화/데이터 추출
│   ├── config/
│   │   ├── settings.py        # 설정 관리
│   │   └── constants.py       # 상수 정의
│   └── ...
├── resources/                # 아이콘/이미지 등 리소스
├── data/                     # 저장된 데이터/엑셀
├── dist/                     # 빌드된 실행파일(main.exe) 및 배포 리소스
├── requirements.txt          # Python 의존성
├── config.json               # 설정 파일
├── README.md
└── ...
```

## 🛠️ 주요 기능 흐름
- **로그인/자동 로그인** → **날짜 선택(datepicker)** → **요청** → **카테고리별 탭에 일정 표시** → **엑셀로 저장**
- **테이블/JSON 탭 전환** 지원
- **엑셀 저장**: 각 카테고리별 표 아래 버튼으로 xlsx 저장

## ⚠️ 배포/실행파일 주의사항
- **chromedriver.exe**: dist/main.exe와 같은 폴더에 복사 필요
- **config.json, resources/**: dist 폴더에 함께 복사
- **PyQt6 DLL/리소스**: --collect-all PyQt6 옵션으로 빌드 권장
- **공식 Python 사용 권장**: Microsoft Store Python은 빌드/실행에 문제 많음

## 📝 최신화 내역
- datepicker, 카테고리별 탭, 엑셀 저장, 실행파일 빌드/배포 주의 등 반영

---

자세한 사용법/배포법은 README.md 참고, 추가 문의는 언제든 환영! 