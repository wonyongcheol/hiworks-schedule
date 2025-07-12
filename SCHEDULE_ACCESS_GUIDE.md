# 스케줄 페이지 접근 및 보기 모드 변경 가이드

## 개요

하이웍스 스케줄 관리자는 로그인 후 자동으로 스케줄 페이지에 접근하여 원하는 보기 모드로 변경하는 기능을 제공합니다.

## 주요 기능

### 1. 자동 스케줄 페이지 접근
- 로그인 성공 후 자동으로 스케줄 페이지로 이동
- URL: `https://calendar.office.hiworks.com/kevinlab.com/schedule/schedulemain`
- 페이지 로딩 완료까지 자동 대기

### 2. 보기 모드 자동 변경
- **월간 보기**: 전체 월의 스케줄을 한 번에 확인
- **주간 보기**: 한 주의 스케줄을 상세히 확인
- **일간 보기**: 하루의 스케줄을 시간별로 확인
- **목록 보기**: 스케줄을 목록 형태로 확인

### 3. UI에서 보기 모드 선택
- 드롭다운 메뉴에서 원하는 보기 모드 선택
- 프로그램 시작 시 기본값: "월간"

## 사용 방법

### 1. 보기 모드 선택
1. 프로그램 실행
2. 상단 설정 영역에서 "보기 모드:" 드롭다운 선택
3. 원하는 보기 모드 선택 (월간/주간/일간/목록)

### 2. 자동 실행
1. 아이디/비밀번호 입력
2. "시작" 버튼 클릭
3. 자동으로 다음 순서로 진행:
   - 로그인
   - 스케줄 페이지 접근
   - 선택한 보기 모드로 변경

## 기술적 구현

### 스케줄 페이지 접근 (`navigate_to_schedule_page`)
```python
def navigate_to_schedule_page(self) -> bool:
    # 1. 로그인 상태 확인
    # 2. 스케줄 URL로 이동
    # 3. 페이지 로딩 대기
    # 4. 접근 성공 여부 확인
```

### 보기 모드 변경 (`change_view_mode`)
```python
def change_view_mode(self, view_mode: str = "월간") -> bool:
    # 1. JavaScript 함수 매개변수 매핑
    # 2. HiworksEvent.calendar_change_view() 함수 직접 실행
    # 3. 실패 시 기존 클릭 방식으로 대체
    # 4. 변경 적용 확인
```

### 전체 프로세스 (`execute_view_mode_change`)
```python
def execute_view_mode_change(self, view_mode: str = "월간") -> bool:
    # 1. 스케줄 페이지로 이동
    # 2. 보기 모드 변경
    # 3. 성공 여부 반환
```

## 보기 모드 변경 과정

### 1단계: JavaScript 함수 매개변수 매핑
보기 모드에 따라 적절한 JavaScript 매개변수를 선택합니다:
- **월간**: `listMonth`
- **주간**: `listWeek`
- **일간**: `listDay`
- **목록**: `listMonth`

### 2단계: JavaScript 함수 직접 실행
`HiworksEvent.calendar_change_view()` 함수를 직접 실행합니다:
```javascript
HiworksEvent.calendar_change_view('listMonth');
```

### 3단계: 대체 방법 (JavaScript 실패 시)
JavaScript 실행이 실패하면 기존의 클릭 방식을 사용합니다:
- 보기 드롭다운 찾기 및 클릭
- 원하는 보기 모드 선택
- 변경 적용 확인

### 4단계: 변경 확인
`view_mode` ID를 가진 요소의 텍스트를 확인하여 변경이 제대로 적용되었는지 검증합니다.

## 로그 메시지

프로그램은 각 단계에서 상세한 로그를 출력합니다:

```
2025-07-12 13:35:08 - hiworks_schedule - INFO - 스케줄 페이지 접근 및 보기 모드 변경을 시작합니다.
2025-07-12 13:35:08 - hiworks_schedule - INFO - 스케줄 페이지로 이동합니다: https://calendar.office.hiworks.com/kevinlab.com/schedule/schedulemain
2025-07-12 13:35:11 - hiworks_schedule - INFO - 스케줄 페이지 URL: https://calendar.office.hiworks.com/kevinlab.com/schedule/schedulemain
2025-07-12 13:35:11 - hiworks_schedule - INFO - 스케줄 페이지에 성공적으로 도달했습니다.
2025-07-12 13:35:11 - hiworks_schedule - INFO - 보기 모드를 '월간'으로 변경합니다.
2025-07-12 13:35:11 - hiworks_schedule - INFO - JavaScript 매개변수: listMonth
2025-07-12 13:35:11 - hiworks_schedule - INFO - JavaScript 실행: HiworksEvent.calendar_change_view('listMonth');
2025-07-12 13:35:11 - hiworks_schedule - INFO - JavaScript 함수 실행 완료
2025-07-12 13:35:13 - hiworks_schedule - INFO - 현재 보기 모드: 월간
2025-07-12 13:35:13 - hiworks_schedule - INFO - 보기 모드가 '월간'으로 성공적으로 변경되었습니다.
2025-07-12 13:35:13 - hiworks_schedule - INFO - 스케줄 페이지 접근 및 보기 모드 변경이 완료되었습니다.
```

## 오류 처리

### 스케줄 페이지 접근 실패
- **원인**: 로그인이 되지 않았거나 네트워크 문제
- **해결**: 로그인 상태 확인 후 재시도

### JavaScript 실행 실패
- **원인**: JavaScript 함수가 정의되지 않았거나 실행 오류
- **해결**: 기존 클릭 방식으로 자동 대체

### 보기 모드 변경 실패
- **원인**: 드롭다운 메뉴가 나타나지 않거나 선택할 수 없는 경우
- **해결**: 대기 시간 조정 후 재시도

## 성능 최적화

### 대기 시간 설정
- **페이지 로딩**: 3초
- **JavaScript 실행**: 즉시
- **변경 적용**: 2초

### 선택자 우선순위
가장 정확한 선택자부터 순차적으로 시도하여 성능을 최적화합니다.

## 문제 해결

### 스케줄 페이지에 접근할 수 없는 경우
1. **로그인 상태 확인**: 먼저 로그인이 성공했는지 확인
2. **네트워크 연결 확인**: 인터넷 연결 상태 확인
3. **URL 확인**: 스케줄 페이지 URL이 올바른지 확인

### 보기 모드가 변경되지 않는 경우
1. **페이지 로딩 확인**: 스케줄 페이지가 완전히 로딩되었는지 확인
2. **JavaScript 확인**: 페이지의 JavaScript가 활성화되어 있는지 확인
3. **선택자 업데이트**: 페이지 구조가 변경되었을 수 있으므로 선택자 확인

### 특정 보기 모드가 작동하지 않는 경우
1. **보기 모드 이름 확인**: 정확한 보기 모드 이름 사용
2. **권한 확인**: 해당 보기 모드에 접근할 권한이 있는지 확인
3. **대체 방법**: 다른 보기 모드로 시도

## 향후 개선 사항

### 예정된 기능
- [ ] 보기 모드 변경 실패 시 자동 재시도
- [ ] 사용자 정의 보기 모드 지원
- [ ] 보기 모드 변경 히스토리 저장
- [ ] 키보드 단축키 지원

### 기술적 개선
- [ ] 더 정확한 요소 찾기 알고리즘
- [ ] 동적 대기 시간 조정
- [ ] 오류 복구 메커니즘 강화 