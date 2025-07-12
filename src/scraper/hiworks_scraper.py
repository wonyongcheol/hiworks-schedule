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
        self.company_domain = None  # 회사 도메인 (예: kevinlab.com, bontemuseum.com)
        
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
        """비밀번호를 입력하고 로그인합니다."""
        try:
            logger.info("비밀번호 입력 페이지에서 회사 도메인을 추출합니다.")
            
            # 현재 URL에서 회사 도메인 추출
            current_url = self.driver.current_url
            logger.info(f"현재 URL: {current_url}")
            
            # URL 패턴: https://login.office.hiworks.com/company.com/
            if "login.office.hiworks.com" in current_url:
                # URL에서 회사 도메인 부분 추출
                url_parts = current_url.split("login.office.hiworks.com/")
                if len(url_parts) > 1:
                    company_part = url_parts[1].split("/")[0]  # 첫 번째 슬래시까지
                    if company_part and "." in company_part:  # 유효한 도메인인지 확인
                        self.company_domain = company_part
                        logger.info(f"회사 도메인 추출 완료: {self.company_domain}")
                    else:
                        logger.warning(f"유효하지 않은 회사 도메인: {company_part}")
                else:
                    logger.warning("URL에서 회사 도메인을 추출할 수 없습니다.")
            else:
                logger.warning("예상한 로그인 URL 패턴이 아닙니다.")
            
            # 기존 비밀번호 입력 로직
            logger.info("비밀번호 입력을 시작합니다.")
            
            # 비밀번호 입력 필드 찾기
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, ".password-input"),
                (By.CSS_SELECTOR, "#userPw"),
                (By.NAME, "userPw"),
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"비밀번호 필드를 찾았습니다: {selector_type, selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if not password_field:
                logger.error("비밀번호 입력 필드를 찾을 수 없습니다.")
                return False
            
            # 기존 내용 지우기
            password_field.clear()
            
            # 비밀번호 입력
            password_field.send_keys(user_pw)
            logger.info("비밀번호를 입력했습니다.")
            
            # 로그인 버튼 찾기 및 클릭
            login_button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), '로그인')]"),
                (By.XPATH, "//input[@value='로그인']"),
                (By.CSS_SELECTOR, ".login-btn"),
                (By.CSS_SELECTOR, "#loginBtn"),
                (By.CSS_SELECTOR, ".btn-login"),
            ]
            
            login_button = None
            for selector_type, selector_value in login_button_selectors:
                try:
                    login_button = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.info(f"로그인 버튼을 찾았습니다: {selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if not login_button:
                logger.error("로그인 버튼을 찾을 수 없습니다.")
                return False
            
            # 로그인 버튼 클릭
            login_button.click()
            logger.info("로그인 버튼을 클릭했습니다.")
            
            # 로그인 성공 확인
            time.sleep(3)  # 페이지 로딩 대기
            
            # 로그인 성공 여부 확인
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            logger.info(f"로그인 후 URL: {current_url}")
            logger.info(f"로그인 후 페이지 제목: {page_title}")
            
            # 로그인 성공 판단 조건
            success_indicators = [
                "login" not in current_url.lower(),
                "error" not in page_title.lower(),
                "fail" not in page_title.lower(),
                "invalid" not in page_title.lower(),
            ]
            
            if all(success_indicators):
                self.is_logged_in = True
                logger.info("로그인이 성공했습니다!")
                return True
            else:
                logger.error("로그인에 실패했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"비밀번호 입력 및 로그인 중 오류: {e}")
            return False
    

    
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
    
    
    def fetch_schedule_json(self, start_date: str, end_date: str) -> dict:
        """Selenium 세션 쿠키로 하이웍스 일정 JSON을 직접 받아온다."""
        # 회사 도메인 확인 및 설정
        if not self.company_domain:
            logger.warning("회사 도메인이 설정되지 않았습니다. 기본값 'kevinlab.com'을 사용합니다.")
            self.company_domain = "kevinlab.com"
        
        url = f"https://calendar.office.hiworks.com/{self.company_domain}/schedule/json/get_schedule_new"
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
            "Referer": f"https://calendar.office.hiworks.com/{self.company_domain}/schedule/schedulemain"
        }
        
        try:
            session = requests.Session()
            # Selenium 쿠키를 requests로 복사
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
            
            logger.info(f"일정 JSON 요청: {url}")
            logger.info(f"회사 도메인: {self.company_domain}")
            logger.info(f"요청 데이터: {payload}")
            
            resp = session.post(url, data=payload, headers=headers)
            resp.raise_for_status()
            
            # 응답 내용 확인
            response_text = resp.text.strip()
            logger.info(f"응답 상태 코드: {resp.status_code}")
            logger.info(f"응답 내용 길이: {len(response_text)}")
            logger.info(f"응답 내용 (처음 200자): {response_text[:200]}")
            
            # 빈 응답 체크
            if not response_text:
                logger.warning("빈 응답을 받았습니다.")
                return {"error": "빈 응답", "data": []}
            
            # 세션 만료 체크 (HTML 응답인지 확인)
            if response_text.startswith('<!DOCTYPE html') or '다시 로그인' in response_text:
                logger.warning("세션이 만료되었습니다. 다시 로그인을 시도합니다.")
                return {"error": "세션 만료", "need_relogin": True}
            
            # JSON 파싱 시도
            try:
                json_data = resp.json()
                logger.info(f"JSON 파싱 성공: {type(json_data)}")
                return json_data
            except ValueError as json_error:
                logger.error(f"JSON 파싱 실패: {json_error}")
                logger.error(f"응답 내용: {response_text}")
                return {"error": f"JSON 파싱 실패: {json_error}", "raw_response": response_text}
                
        except requests.exceptions.RequestException as req_error:
            logger.error(f"HTTP 요청 오류: {req_error}")
            return {"error": f"HTTP 요청 오류: {req_error}"}
        except Exception as e:
            logger.error(f"일정 JSON 요청 중 예상치 못한 오류: {e}")
            return {"error": f"예상치 못한 오류: {e}"}
    
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