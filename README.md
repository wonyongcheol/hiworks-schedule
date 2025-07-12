# 하이웍스 스케줄 관리자

하이웍스(Hiworks) 웹사이트에서 스케줄 데이터를 자동으로 수집하고 관리하는 윈도우 프로그램입니다.

## 🚀 주요 기능

- **자동 로그인**: 아이디/비밀번호 저장 및 자동 로그인
- **스케줄 수집**: Selenium을 통한 하이웍스 스케줄 자동 수집
- **카테고리별 분류**: schedule, spacial, lunar, birthday 등 카테고리별 정리
- **데이터 내보내기**: 엑셀(xlsx) 형식으로 스케줄 데이터 저장
- **현대적 GUI**: PyQt6 기반의 직관적인 사용자 인터페이스

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 프로그램 실행
```bash
python src/main.py
```

### 3. 실행파일 생성
```bash
pyinstaller --onefile --windowed --collect-all PyQt6 --paths=src --name hiworks-schedule src/main.py
```

## 🎯 사용법

1. **로그인**: 하이웍스 아이디/비밀번호 입력
2. **날짜 선택**: 조회할 기간 설정
3. **데이터 수집**: 스케줄 데이터 자동 수집
4. **카테고리 확인**: 탭으로 구분된 카테고리별 스케줄 확인
5. **엑셀 저장**: 원하는 카테고리의 데이터를 엑셀로 저장

## 🛠️ 기술 스택

- **GUI**: PyQt6
- **웹 자동화**: Selenium WebDriver
- **데이터 처리**: pandas
- **파일 저장**: openpyxl, xlsxwriter
- **보안**: cryptography (자격 증명 암호화)

## 📁 프로젝트 구조

```
hiworks-schedule/
├── src/
│   ├── main.py              # 메인 실행 파일
│   ├── gui/                 # GUI 관련 모듈
│   ├── scraper/             # 웹 스크래핑 모듈
│   ├── utils/               # 유틸리티 모듈
│   └── config/              # 설정 관리
├── resources/               # 리소스 파일
├── data/                    # 데이터 저장소
├── logs/                    # 로그 파일
├── dist/                    # 배포 파일
├── requirements.txt         # 의존성 목록
└── config.json             # 설정 파일
```

## 📝 주의사항

- 하이웍스 계정 정보가 필요합니다
- Chrome 브라우저가 설치되어 있어야 합니다
- 인터넷 연결이 필요합니다
- 실행파일 배포 시 `config.json`, `resources/` 폴더도 함께 복사해야 합니다