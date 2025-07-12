from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from typing import Optional, Dict, Any
from config.settings import settings
from utils.logger import logger
import requests


class HiworksScraper:
    """하이웍스 웹사이트 스크래핑을 위한 클래스"""
    
    def __init__(self, headless: bool = True):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.is_logged_in = False
        self.headless = headless
        self.login_url = settings.get("hiworks.login_url", "https://login.office.hiworks.com/")
        self.timeout = settings.get("hiworks.timeout", 30)
        
    def setup_driver(self) -> bool:
        """Chrome WebDriver를 설정합니다."""
        try:
            logger.info("Chrome WebDriver 설정을 시작합니다.")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # 헤드리스 모드 설정
            if self.headless:
                chrome_options.add_argument("--headless=new")  # 새로운 헤드리스 모드 사용
                logger.info("헤드리스 모드로 실행됩니다.")
            else:
                logger.info("브라우저 창이 표시됩니다.")
            
            # 추가 성능 최적화 옵션
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
            # chrome_options.add_argument("--disable-javascript")  # JavaScript 비활성화 (필요시 주석 해제)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 연결 안정성을 위한 추가 옵션
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # ChromeDriver 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            
            # WebDriver 생성
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # WebDriverWait 설정
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            logger.info("Chrome WebDriver 설정이 완료되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"Chrome WebDriver 설정 중 오류 발생: {e}")
            return False
    
    def navigate_to_login_page(self) -> bool:
        """하이웍스 로그인 페이지로 이동합니다."""
        try:
            logger.info(f"하이웍스 로그인 페이지로 이동합니다: {self.login_url}")
            
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            # 로그인 페이지로 이동
            self.driver.get(self.login_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            logger.info(f"현재 페이지 URL: {current_url}")
            
            # 페이지 제목 확인
            page_title = self.driver.title
            logger.info(f"페이지 제목: {page_title}")
            
            # 로그인 폼이 있는지 확인
            try:
                # 로그인 폼 요소 확인 (실제 하이웍스 페이지 구조에 맞게 수정 필요)
                login_form = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                logger.info("로그인 폼을 찾았습니다.")
                return True
                
            except TimeoutException:
                logger.warning("로그인 폼을 찾을 수 없습니다. 페이지 구조를 확인해주세요.")
                return False
                
        except Exception as e:
            logger.error(f"로그인 페이지 이동 중 오류 발생: {e}")
            return False
    
    def login(self, user_id: str, user_pw: str) -> bool:
        """
        하이웍스 2단계 로그인: 아이디 입력 후 제출, 그 다음 비밀번호 입력
        """
        try:
            logger.info("2단계 로그인 프로세스를 시작합니다.")
            
            if not self.navigate_to_login_page():
                logger.error("로그인 페이지 접속 실패")
                return False
            
            # 1단계: 아이디 입력 및 제출
            logger.info("1단계: 아이디 입력 및 제출")
            if not self._input_username_and_submit(user_id):
                logger.error("아이디 입력 및 제출 실패")
                return False
            
            # 2단계: 비밀번호 입력 및 최종 로그인
            logger.info("2단계: 비밀번호 입력 및 최종 로그인")
            if not self._input_password_and_login(user_pw):
                logger.error("비밀번호 입력 및 로그인 실패")
                return False
            
            # 로그인 성공 여부 확인
            logger.info("로그인 성공 여부를 확인하는 중...")
            time.sleep(3)  # 페이지 로딩 대기
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"로그인 후 URL: {current_url}")
            logger.info(f"로그인 후 페이지 제목: {page_title}")
            
            # URL이 변경되었는지 확인 (로그인 성공 시 일반적으로 URL이 변경됨)
            if "login" not in current_url.lower():
                self.is_logged_in = True
                logger.info("로그인 성공으로 판단됩니다.")
                return True
            else:
                logger.warning("로그인 실패로 판단됩니다. (URL에 'login'이 포함됨)")
                return False
                
        except Exception as e:
            logger.error(f"로그인 자동화 중 오류: {e}")
            return False
    
    def _input_username_and_submit(self, user_id: str) -> bool:
        """아이디 입력 및 제출 (1단계)"""
        try:
            logger.info("아이디 입력란을 찾는 중...")
            id_input = None
            
            # 여러 방법으로 아이디 입력란 찾기
            selectors = [
                (By.CSS_SELECTOR, "[id^='mantine-']"),  # mantine- 패턴
                (By.CSS_SELECTOR, "input[type='text'], input[type='email']"),  # type
                (By.XPATH, "//input[@placeholder and (contains(@placeholder, '아이디') or contains(@placeholder, 'ID') or contains(@placeholder, '이메일') or contains(@placeholder, 'email'))]"),  # placeholder
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    id_input = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"아이디 입력란을 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not id_input:
                logger.error("모든 방법으로 아이디 입력란을 찾을 수 없습니다.")
                return False
            
            # 아이디 입력
            id_input.clear()
            id_input.send_keys(user_id)
            logger.info("아이디 입력 완료")
            
            # 제출 버튼 찾기 및 클릭
            logger.info("아이디 제출 버튼을 찾는 중...")
            submit_btn = None
            
            # 여러 방법으로 제출 버튼 찾기
            submit_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '다음')]"),
                (By.XPATH, "//button[contains(text(), '계속')]"),
                (By.XPATH, "//button[contains(text(), '확인')]"),
                (By.XPATH, "//button[contains(text(), '진행')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ]
            
            for selector_type, selector_value in submit_selectors:
                try:
                    submit_btn = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.info(f"제출 버튼을 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not submit_btn:
                # 폼 submit 시도
                try:
                    logger.info("폼 submit을 시도합니다.")
                    id_input.submit()
                    logger.info("폼 submit 완료")
                except Exception as e:
                    logger.error(f"제출 버튼을 찾을 수 없고 폼 submit도 실패: {e}")
                    return False
            else:
                submit_btn.click()
                logger.info("제출 버튼 클릭 완료")
            
            # 페이지 전환 대기
            logger.info("페이지 전환을 기다리는 중...")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"아이디 입력 및 제출 중 오류: {e}")
            return False
    
    def _input_password_and_login(self, user_pw: str) -> bool:
        """비밀번호 입력 및 최종 로그인 (2단계)"""
        try:
            logger.info("비밀번호 입력란을 찾는 중...")
            pw_input = None
            
            # 여러 방법으로 비밀번호 입력란 찾기
            pw_selectors = [
                (By.NAME, "password"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@placeholder and contains(@placeholder, '비밀번호')]"),
            ]
            
            for selector_type, selector_value in pw_selectors:
                try:
                    pw_input = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"비밀번호 입력란을 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not pw_input:
                logger.error("비밀번호 입력란을 찾을 수 없습니다.")
                return False
            
            # 비밀번호 입력
            pw_input.clear()
            pw_input.send_keys(user_pw)
            logger.info("비밀번호 입력 완료")
            
            # 최종 로그인 버튼 찾기 및 클릭
            logger.info("최종 로그인 버튼을 찾는 중...")
            login_btn = None
            
            # 여러 방법으로 로그인 버튼 찾기
            login_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '로그인')]"),
                (By.XPATH, "//button[contains(text(), '확인')]"),
                (By.XPATH, "//button[contains(text(), '완료')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ]
            
            for selector_type, selector_value in login_selectors:
                try:
                    login_btn = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.info(f"로그인 버튼을 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not login_btn:
                # 폼 submit 시도
                try:
                    logger.info("폼 submit을 시도합니다.")
                    pw_input.submit()
                    logger.info("폼 submit 완료")
                except Exception as e:
                    logger.error(f"로그인 버튼을 찾을 수 없고 폼 submit도 실패: {e}")
                    return False
            else:
                login_btn.click()
                logger.info("로그인 버튼 클릭 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"비밀번호 입력 및 로그인 중 오류: {e}")
            return False
    
    def get_page_info(self) -> Dict[str, Any]:
        """현재 페이지 정보를 가져옵니다."""
        if not self.driver:
            return {"error": "WebDriver가 초기화되지 않았습니다."}
        
        try:
            info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "is_logged_in": self.is_logged_in,
                "headless_mode": self.headless
            }
            
            # 페이지 소스 일부 가져오기 (디버깅용)
            page_source = self.driver.page_source
            info["source_length"] = len(page_source)
            info["source_preview"] = page_source[:500] + "..." if len(page_source) > 500 else page_source
            
            return info
            
        except Exception as e:
            logger.error(f"페이지 정보 가져오기 중 오류: {e}")
            return {"error": str(e)}
    
    def close_driver(self):
        """WebDriver를 종료합니다."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver가 종료되었습니다.")
            except Exception as e:
                logger.error(f"WebDriver 종료 중 오류: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate_to_schedule_page(self) -> bool:
        """스케줄 페이지로 이동합니다."""
        try:
            if not self.is_logged_in:
                logger.error("로그인이 필요합니다.")
                return False
            
            schedule_url = "https://calendar.office.hiworks.com/kevinlab.com/schedule/schedulemain"
            logger.info(f"스케줄 페이지로 이동합니다: {schedule_url}")
            
            self.driver.get(schedule_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"스케줄 페이지 URL: {current_url}")
            logger.info(f"스케줄 페이지 제목: {page_title}")
            
            # 스케줄 페이지에 도달했는지 확인
            if "schedule" in current_url.lower():
                logger.info("스케줄 페이지에 성공적으로 도달했습니다.")
                return True
            else:
                logger.warning("스케줄 페이지에 도달하지 못했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"스케줄 페이지 이동 중 오류: {e}")
            return False
    
    def change_view_mode(self, view_mode: str = "월간") -> bool:
        """보기 모드를 변경합니다."""
        try:
            logger.info(f"보기 모드를 '{view_mode}'로 변경합니다.")
            
            # 보기 모드에 따른 JavaScript 함수 매개변수 매핑
            view_mode_mapping = {
                "월간": "listMonth",
                "주간": "listWeek", 
                "일간": "listDay",
                "목록": "listMonth"
            }
            
            # 매핑된 보기 모드 확인
            if view_mode not in view_mode_mapping:
                logger.error(f"지원하지 않는 보기 모드입니다: {view_mode}")
                return False
            
            js_param = view_mode_mapping[view_mode]
            logger.info(f"JavaScript 매개변수: {js_param}")
            
            # JavaScript 함수 직접 실행
            try:
                js_code = f"HiworksEvent.calendar_change_view('{js_param}');"
                logger.info(f"JavaScript 실행: {js_code}")
                
                self.driver.execute_script(js_code)
                logger.info("JavaScript 함수 실행 완료")
                
                # 변경 적용 대기
                time.sleep(2)
                
                # 변경 확인 (선택사항)
                try:
                    current_view = self.driver.find_element(By.ID, "view_mode")
                    current_view_text = current_view.text
                    logger.info(f"현재 보기 모드: {current_view_text}")
                except Exception:
                    logger.info("보기 모드 확인 요소를 찾을 수 없지만 JavaScript 실행은 완료되었습니다.")
                
                logger.info(f"보기 모드가 '{view_mode}'로 성공적으로 변경되었습니다.")
                return True
                
            except Exception as js_error:
                logger.error(f"JavaScript 실행 중 오류: {js_error}")
                
                # JavaScript 실행 실패 시 기존 방법으로 대체
                logger.info("JavaScript 실행 실패, 기존 방법으로 시도합니다.")
                return self._change_view_mode_fallback(view_mode)
                
        except Exception as e:
            logger.error(f"보기 모드 변경 중 오류: {e}")
            return False
    
    def _change_view_mode_fallback(self, view_mode: str) -> bool:
        """보기 모드 변경의 대체 방법 (기존 클릭 방식)"""
        try:
            logger.info(f"대체 방법으로 보기 모드 '{view_mode}' 변경을 시도합니다.")
            
            # 보기 드롭다운 버튼 찾기
            view_dropdown = None
            view_selectors = [
                (By.XPATH, "//a[contains(@href, 'HiworksEvent.drop_view')]"),
                (By.XPATH, "//a[contains(text(), '보기')]"),
                (By.XPATH, "//a[contains(text(), '월간')]"),
                (By.XPATH, "//a[contains(text(), '주간')]"),
                (By.XPATH, "//a[contains(text(), '일간')]"),
            ]
            
            for selector_type, selector_value in view_selectors:
                try:
                    view_dropdown = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.info(f"보기 드롭다운을 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not view_dropdown:
                logger.error("보기 드롭다운을 찾을 수 없습니다.")
                return False
            
            # 드롭다운 클릭
            view_dropdown.click()
            logger.info("보기 드롭다운 클릭 완료")
            
            # 드롭다운 메뉴가 나타날 때까지 대기
            time.sleep(1)
            
            # 원하는 보기 모드 선택
            view_mode_selectors = [
                (By.XPATH, f"//a[contains(text(), '{view_mode}')]"),
                (By.XPATH, f"//div[contains(text(), '{view_mode}')]"),
                (By.XPATH, f"//span[contains(text(), '{view_mode}')]"),
            ]
            
            view_mode_element = None
            for selector_type, selector_value in view_mode_selectors:
                try:
                    view_mode_element = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.info(f"보기 모드 '{view_mode}'를 {selector_type}: {selector_value}로 찾았습니다.")
                    break
                except Exception:
                    continue
            
            if not view_mode_element:
                logger.error(f"보기 모드 '{view_mode}'를 찾을 수 없습니다.")
                return False
            
            # 보기 모드 클릭
            view_mode_element.click()
            logger.info(f"보기 모드 '{view_mode}' 클릭 완료")
            
            # 변경 적용 대기
            time.sleep(2)
            
            # 변경 확인
            try:
                current_view = self.driver.find_element(By.ID, "view_mode")
                current_view_text = current_view.text
                logger.info(f"현재 보기 모드: {current_view_text}")
                
                if view_mode in current_view_text:
                    logger.info(f"보기 모드가 '{view_mode}'로 성공적으로 변경되었습니다.")
                    return True
                else:
                    logger.warning(f"보기 모드 변경이 제대로 적용되지 않았습니다. 현재: {current_view_text}")
                    return False
                    
            except Exception as e:
                logger.error(f"보기 모드 변경 확인 중 오류: {e}")
                return False
                
        except Exception as e:
            logger.error(f"대체 방법으로 보기 모드 변경 중 오류: {e}")
            return False
    
    def execute_view_mode_change(self, view_mode: str = "월간") -> bool:
        """스케줄 페이지로 이동하고 보기 모드를 변경하는 전체 프로세스"""
        try:
            logger.info("스케줄 페이지 접근 및 보기 모드 변경을 시작합니다.")
            
            # 1단계: 스케줄 페이지로 이동
            if not self.navigate_to_schedule_page():
                logger.error("스케줄 페이지 이동 실패")
                return False
            
            # 2단계: 보기 모드 변경
            if not self.change_view_mode(view_mode):
                logger.error("보기 모드 변경 실패")
                return False
            
            logger.info("스케줄 페이지 접근 및 보기 모드 변경이 완료되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"스케줄 페이지 접근 및 보기 모드 변경 중 오류: {e}")
            return False
    
    def extract_schedule_table_data(self) -> Dict[str, Any]:
        """스케줄 테이블에서 데이터를 추출합니다."""
        try:
            logger.info("스케줄 테이블 데이터를 추출하는 중...")
            current_month = self._extract_current_month()
            
            # 테이블 데이터 추출
            table_data = []
            
            # 헤더 추가
            headers = ["날짜", "시간", "제목", "설명", "위치", "참석자", "상태"]
            table_data.append({"type": "header", "data": headers})
            
            # s_day 클래스를 가진 요소들 찾기
            day_elements = self.driver.find_elements(By.CLASS_NAME, "s_day")
            
            if not day_elements:
                # 다른 가능한 셀렉터들 시도
                alternative_selectors = [
                    (By.CSS_SELECTOR, ".fc-daygrid-day"),
                    (By.CSS_SELECTOR, ".fc-list-day"),
                    (By.CSS_SELECTOR, ".schedule-day"),
                    (By.CSS_SELECTOR, ".day-item"),
                    (By.XPATH, "//div[contains(@class, 'day')]"),
                ]
                
                for selector_type, selector_value in alternative_selectors:
                    try:
                        day_elements = self.driver.find_elements(selector_type, selector_value)
                        if day_elements:
                            logger.info(f"대체 셀렉터로 일정 요소를 찾았습니다: {selector_value}")
                            break
                    except Exception:
                        continue
            
            if not day_elements:
                logger.warning("일정 요소를 찾을 수 없습니다.")
                return {
                    "success": False,
                    "error": "일정 요소를 찾을 수 없습니다.",
                    "data": table_data,
                    "current_month": current_month,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "table_extraction"
                }
            
            logger.info(f"총 {len(day_elements)}개의 일정 요소를 찾았습니다.")
            
            # 각 일정 요소에서 데이터 추출
            for i, day_element in enumerate(day_elements):
                try:
                    logger.info(f"일정 요소 {i+1}/{len(day_elements)} 처리 중...")
                    row_datas = self._extract_row_data(day_element)  # 여러 일정 반환
                    logger.info(f"추출된 데이터: {row_datas}")
                    for row_data in row_datas:
                        if not isinstance(row_data, list) or len(row_data) != 7:
                            logger.warning(f"잘못된 row_data 형식: {row_data}")
                            continue
                        if self._has_schedule_data(row_data):
                            table_data.append({"type": "data", "data": row_data})
                            logger.info(f"일정 데이터 추가됨: {row_data[2]}")  # 제목 출력
                        else:
                            logger.info("일정 데이터가 없어서 건너뜀")
                except Exception as e:
                    logger.warning(f"일정 요소 {i+1} 데이터 추출 중 오류: {e}")
                    continue
            
            result = {
                "success": True,
                "table_count": len(table_data),
                "data": table_data,
                "current_month": current_month,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "table_extraction"
            }
            
            logger.info(f"테이블 데이터 추출 완료: {len(table_data)}개 행")
            return result
            
        except Exception as e:
            logger.error(f"테이블 데이터 추출 중 오류: {e}")
            return {
                "error": f"테이블 데이터 추출 중 오류: {str(e)}",
                "data": [],
                "current_month": "오류",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "table_extraction"
            }
    
    def _convert_json_to_table(self, json_data: dict) -> list:
        """JSON 데이터를 테이블 형식으로 변환합니다."""
        try:
            table_data = []
            
            # 헤더 추가
            headers = ["날짜", "시간", "제목", "설명", "위치", "참석자", "상태"]
            table_data.append({"type": "header", "data": headers})
            
            # JSON 데이터에서 스케줄 정보 추출
            schedules = json_data.get("schedules", [])
            if not schedules:
                schedules = json_data.get("data", [])
            
            if isinstance(schedules, list):
                for schedule in schedules:
                    if isinstance(schedule, dict):
                        row_data = [
                            schedule.get("date", ""),
                            schedule.get("time", ""),
                            schedule.get("title", ""),
                            schedule.get("description", ""),
                            schedule.get("location", ""),
                            schedule.get("attendees", ""),
                            schedule.get("status", "")
                        ]
                        # 빈 행이 아닌 경우만 추가
                        if any(cell.strip() for cell in row_data):
                            table_data.append({"type": "data", "data": row_data})
            
            logger.info(f"JSON 데이터를 테이블로 변환 완료: {len(table_data)}개 행")
            return table_data
            
        except Exception as e:
            logger.error(f"JSON을 테이블로 변환 중 오류: {e}")
            return []

    def _extract_row_data(self, row_element) -> list:
        """일정 요소에서 행 데이터(2차원 리스트)를 추출합니다."""
        try:
            full_text = row_element.text.strip()
            logger.info(f"요소 전체 텍스트: '{full_text}'")
            schedules = self._parse_schedule_text(full_text)
            if schedules:
                return schedules  # 2차원 리스트
            else:
                return []
        except Exception as e:
            logger.warning(f"행 데이터 추출 중 오류: {e}")
            return []
    
    def _parse_schedule_text(self, text: str) -> list:
        """스케줄 텍스트를 파싱해서 일정 목록을 반환합니다."""
        try:
            schedules = []
            lines = text.split('\n')
            current_date = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 날짜 라인인지 확인 (예: "7.1 화", "7.2 수")
                if self._is_date_line(line):
                    current_date = line
                    continue
                
                # 일정 라인인지 확인
                if self._is_schedule_line(line):
                    schedule_data = self._parse_schedule_line(line, current_date)
                    if schedule_data:
                        schedules.append(schedule_data)
            
            logger.info(f"파싱된 일정 수: {len(schedules)}")
            return schedules
            
        except Exception as e:
            logger.error(f"스케줄 텍스트 파싱 중 오류: {e}")
            return []
    
    def _is_date_line(self, line: str) -> bool:
        """날짜 라인인지 확인합니다."""
        # "7.1 화", "7.2 수" 형태의 패턴 확인
        pattern = r'^\d+\.\d+\s+[월화수목금토일]$'
        return bool(re.match(pattern, line))
    
    def _is_schedule_line(self, line: str) -> bool:
        """일정 라인인지 확인합니다."""
        # 빈 줄이나 날짜만 있는 줄이 아닌 경우
        if not line or self._is_date_line(line):
            return False
        
        # 시간 정보나 일정 내용이 포함된 경우
        time_patterns = ['오전', '오후', '시', '분']
        schedule_patterns = ['외근', '출장', '회의', '전시회', '업데이트']
        
        has_time = any(pattern in line for pattern in time_patterns)
        has_schedule = any(pattern in line for pattern in schedule_patterns)
        
        return has_time or has_schedule or '[' in line
    
    def _parse_schedule_line(self, line: str, date: str) -> list:
        """일정 라인을 파싱해서 데이터를 반환합니다."""
        try:
            # 시간 추출
            time_text = ""
            if '오전' in line or '오후' in line:
                time_match = re.search(r'(오전|오후)\s*\d+시', line)
                if time_match:
                    time_text = time_match.group()
            
            # 참석자와 상태 추출 (대괄호 안의 내용)
            attendees_text = ""
            status_text = ""
            bracket_match = re.search(r'\[([^\]]+)\]', line)
            if bracket_match:
                bracket_content = bracket_match.group(1)
                if ',' in bracket_content:
                    parts = bracket_content.split(',')
                    attendees_text = parts[0].strip()
                    status_text = parts[1].strip()
                else:
                    attendees_text = bracket_content.strip()
            
            # 제목 추출 (대괄호 제거 후 남은 내용)
            title_text = re.sub(r'\[[^\]]*\]', '', line).strip()
            title_text = re.sub(r'(오전|오후)\s*\d+시', '', title_text).strip()
            
            # 설명, 위치는 빈 값으로 설정
            description_text = ""
            location_text = ""
            
            schedule_data = [
                date,
                time_text,
                title_text,
                description_text,
                location_text,
                attendees_text,
                status_text
            ]
            
            logger.info(f"파싱된 일정: {schedule_data}")
            return schedule_data
            
        except Exception as e:
            logger.error(f"일정 라인 파싱 중 오류: {e}")
            return []
    
    def _has_schedule_data(self, row_data: list) -> bool:
        """행에 일정 데이터가 있는지 확인합니다."""
        if not row_data:
            return False
        
        # 빈 문자열이나 일정 없음을 나타내는 텍스트들
        empty_patterns = [
            "", "일정 없음", "스케줄 없음", "예약 없음", 
            "No schedule", "No events", "Empty", "없음"
        ]
        
        # 모든 셀이 비어있거나 일정 없음을 나타내는 경우 False 반환
        for cell in row_data:
            cell_text = cell.strip()
            if cell_text and cell_text not in empty_patterns:
                return True
        
        return False
    
    def _extract_current_month(self) -> str:
        """현재 표시된 년월 정보를 추출합니다."""
        try:
            # .fc-toolbar .fc-center h2 요소 찾기
            month_selectors = [
                (By.CSS_SELECTOR, ".fc-toolbar .fc-center h2"),
                (By.CSS_SELECTOR, ".fc-center h2"),
                (By.XPATH, "//div[contains(@class, 'fc-toolbar')]//div[contains(@class, 'fc-center')]//h2"),
                (By.XPATH, "//h2[contains(@class, 'fc-toolbar-chunk')]"),
            ]
            
            for selector_type, selector_value in month_selectors:
                try:
                    month_element = self.driver.find_element(selector_type, selector_value)
                    month_text = month_element.text.strip()
                    if month_text:
                        logger.info(f"현재 년월 정보: {month_text}")
                        return month_text
                except Exception:
                    continue
            
            logger.warning("년월 정보를 찾을 수 없습니다.")
            return "날짜 정보 없음"
            
        except Exception as e:
            logger.error(f"년월 정보 추출 중 오류: {e}")
            return "날짜 정보 오류"
    
    def navigate_to_previous_month(self) -> bool:
        """이전달로 이동합니다."""
        try:
            logger.info("이전달로 이동합니다.")
            js_code = 'HiworksSchedule.prev("calendar");'
            self.driver.execute_script(js_code)
            time.sleep(2)  # 페이지 로딩 대기
            logger.info("이전달 이동 완료")
            return True
        except Exception as e:
            logger.error(f"이전달 이동 중 오류: {e}")
            return False
    
    def navigate_to_next_month(self) -> bool:
        """다음달로 이동합니다."""
        try:
            logger.info("다음달로 이동합니다.")
            js_code = 'HiworksSchedule.next("calendar");'
            self.driver.execute_script(js_code)
            time.sleep(2)  # 페이지 로딩 대기
            logger.info("다음달 이동 완료")
            return True
        except Exception as e:
            logger.error(f"다음달 이동 중 오류: {e}")
            return False
    
    def fetch_schedule_json(self, start_date: str, end_date: str) -> dict:
        """Selenium 세션 쿠키로 하이웍스 일정 JSON을 직접 받아온다."""
        url = "https://calendar.office.hiworks.com/kevinlab.com/schedule/json/get_schedule_new"
        payload = {
            "accesstype": "S",
            "syncflag": "N",
            "hid": "",
            "birthday_show_flag": "N",
            "id": "calendar",
            "start": start_date,
            "end": end_date
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://calendar.office.hiworks.com/kevinlab.com/schedule/schedulemain"
        }
        session = requests.Session()
        # Selenium 쿠키를 requests로 복사
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        resp = session.post(url, data=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def fetch_schedule_after_login(self, user_id: str, user_pw: str, start_date: str, end_date: str) -> dict:
        """로그인 후 곧바로 POST로 일정 JSON만 받아오기 (스케줄 페이지 이동 없이)."""
        if not self.login(user_id, user_pw):
            return {"error": "로그인 실패"}
        try:
            logger.info(f"로그인 후 POST로 일정 JSON 요청: {start_date} ~ {end_date}")
            json_data = self.fetch_schedule_json(start_date, end_date)
            logger.info(f"일정 JSON 응답: {str(json_data)[:200]} ...")
            return json_data
        except Exception as e:
            logger.error(f"일정 JSON 요청 중 오류: {e}")
            return {"error": str(e)}
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close_driver() 