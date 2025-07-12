import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox,
    QStatusBar, QMenuBar, QMenu, QSplitter, QCheckBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate, QObject
from PyQt6.QtGui import QFont, QIcon, QAction
from typing import Optional
from config.settings import settings
from config.constants import WINDOW_TITLE, DARK_COLORS, LIGHT_COLORS
from utils.logger import logger
from utils.credential_manager import CredentialManager
from scraper.hiworks_scraper import HiworksScraper
import datetime
import json
from collections import defaultdict
import pandas as pd
from PyQt6.QtWidgets import QFileDialog
import re


class LoginWorker(QObject):
    finished = pyqtSignal(bool)
    def __init__(self, user_id, user_pw, headless=True):
        super().__init__()
        from scraper.hiworks_scraper import HiworksScraper
        self.user_id = user_id
        self.user_pw = user_pw
        self.headless = headless
        self.scraper = HiworksScraper(headless=self.headless)
    def run(self):
        result = self.scraper.login(self.user_id, self.user_pw)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """메인 애플리케이션 창"""
    
    def __init__(self):
        super().__init__()
        self.credential_manager = CredentialManager()
        self.worker = None  # 로그인 성공 시 할당되는 scraper
        self.category_tabs = {}  # 지연 초기화를 위해 미리 선언
        
        # 기본 UI만 먼저 초기화
        self.init_basic_ui()
        self.apply_theme()
        self.load_saved_credentials()
        
        # 나머지 UI는 필요할 때 초기화
        self._advanced_ui_initialized = False
    
    def init_basic_ui(self):
        """기본 UI만 초기화 (빠른 시작을 위해)"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, 800, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 메뉴바 생성
        self.create_menu_bar()
        
        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
        
        # 제목
        title_label = QLabel("하이웍스 스케줄 관리자")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 설정 레이아웃
        settings_layout = QHBoxLayout()
        self.headless_checkbox = QCheckBox("백그라운드 모드 (브라우저 창 숨김)")
        self.headless_checkbox.setChecked(settings.get("hiworks.headless_mode", True))
        self.headless_checkbox.setToolTip("체크하면 브라우저 창이 표시되지 않고 백그라운드에서 실행됩니다.")
        self.headless_checkbox.stateChanged.connect(self.save_headless_setting)
        settings_layout.addWidget(self.headless_checkbox)
        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)
        
        # 로그인 레이아웃
        login_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디")
        self.id_input.setFixedWidth(200)
        login_layout.addWidget(self.id_input)
        
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setFixedWidth(200)
        login_layout.addWidget(self.pw_input)
        
        self.save_credentials_checkbox = QCheckBox("자격 증명 저장")
        self.save_credentials_checkbox.setToolTip("아이디와 비밀번호를 안전하게 저장합니다.")
        login_layout.addWidget(self.save_credentials_checkbox)
        
        self.auto_login_checkbox = QCheckBox("자동 로그인")
        self.auto_login_checkbox.setToolTip("프로그램 시작 시 저장된 자격 증명으로 자동 로그인합니다.")
        self.auto_login_checkbox.stateChanged.connect(self.save_auto_login_setting)
        login_layout.addWidget(self.auto_login_checkbox)
        main_layout.addLayout(login_layout)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("로그인")
        self.connect_button.clicked.connect(self.connect_to_hiworks)
        self.connect_button.setMinimumHeight(40)
        button_layout.addWidget(self.connect_button)
        main_layout.addLayout(button_layout)
        
        # 진행바
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 상태 라벨
        self.status_label = QLabel("대기 중...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 날짜 레이아웃 (기본값만 설정)
        self.setup_date_inputs(main_layout)
        
        # 요청 버튼 (비활성화 상태로 생성)
        self.request_button = QPushButton("요청")
        self.request_button.clicked.connect(self.request_schedule_data)
        self.request_button.setEnabled(False)
        self.request_button.setMinimumHeight(40)
        main_layout.addWidget(self.request_button)
        
        # 나머지 UI는 필요할 때 초기화
        self._setup_placeholder_for_advanced_ui(main_layout)
    
    def _setup_placeholder_for_advanced_ui(self, main_layout):
        """고급 UI를 위한 플레이스홀더 설정"""
        self.advanced_ui_placeholder = QWidget()
        main_layout.addWidget(self.advanced_ui_placeholder)
    
    def _init_advanced_ui(self):
        """고급 UI 지연 초기화"""
        if self._advanced_ui_initialized:
            return
            
        logger.info("고급 UI 초기화 시작")
        
        # 기존 플레이스홀더 제거
        if hasattr(self, 'advanced_ui_placeholder'):
            self.advanced_ui_placeholder.setParent(None)
        
        # 메인 레이아웃 가져오기
        main_layout = self.centralWidget().layout()
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 테이블 탭을 먼저 생성 (제일 왼쪽에 위치)
        self.category_tab_widget = QTabWidget()
        self.tab_widget.addTab(self.category_tab_widget, "테이블")
        
        # JSON 뷰 탭을 나중에 추가 (오른쪽에 위치)
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.json_view, "JSON 결과")
        
        # 카테고리별 탭은 데이터가 있을 때 생성
        self._advanced_ui_initialized = True
        logger.info("고급 UI 초기화 완료")
    
    def setup_date_inputs(self, main_layout):
        """날짜 입력 위젯 설정"""
        date_layout = QHBoxLayout()
        
        # QDateEdit으로 교체
        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setFixedWidth(120)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setFixedWidth(120)
        
        # 기본값: 이번달 1일~말일
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        last_day = QDate(today.year(), today.month(), today.daysInMonth())
        
        self.start_date_input.setDate(first_day)
        self.end_date_input.setDate(last_day)
        
        date_layout.addWidget(QLabel("시작일:"))
        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(QLabel("종료일:"))
        date_layout.addWidget(self.end_date_input)
        date_layout.addStretch()
        
        main_layout.addLayout(date_layout)
        
        # 날짜 입력 위젯 비활성화 (로그인 후 활성화)
        self.start_date_input.setEnabled(False)
        self.end_date_input.setEnabled(False)

    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 도구 메뉴
        tools_menu = menubar.addMenu("도구")
        
        settings_action = QAction("설정", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # 자격 증명 관리 메뉴
        credentials_menu = tools_menu.addMenu("자격 증명 관리")
        
        clear_credentials_action = QAction("저장된 자격 증명 삭제", self)
        clear_credentials_action.triggered.connect(self.clear_saved_credentials)
        credentials_menu.addAction(clear_credentials_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말")
        
        about_action = QAction("정보", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_theme(self):
        """테마 적용"""
        theme = settings.get("gui.theme", "dark")
        colors = DARK_COLORS if theme == "dark" else LIGHT_COLORS
        def adjust_color(hex_color, factor=0.8):
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = min(255, max(0, int(r * factor)))
            g = min(255, max(0, int(g * factor)))
            b = min(255, max(0, int(b * factor)))
            return f'#{r:02x}{g:02x}{b:02x}'
        primary = colors['primary']
        hover = adjust_color(primary, 1.2 if theme=="dark" else 0.8)
        # 탭 배경/글자색
        tab_bg = adjust_color(colors['background'], 0.92 if theme=="dark" else 1.08)
        tab_fg = colors['text']
        # 스타일시트 설정
        style_sheet = f"""
        QMainWindow {{ background-color: {colors['background']}; color: {colors['text']}; }}
        QLabel {{ color: {colors['text']}; }}
        QPushButton {{ background-color: {colors['primary']}; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }}
        QPushButton:hover {{ background-color: {hover}; color: white; }}
        QPushButton:disabled {{ background-color: {colors['secondary']}; color: {colors['text_secondary']}; }}
        QTabWidget::pane {{ background: {tab_bg}; border-radius: 6px; }}
        QTabBar::tab {{ background: {tab_bg}; color: {tab_fg}; padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }}
        QTabBar::tab:selected {{ background: {colors['surface']}; color: {primary}; font-weight: bold; }}
        QTabBar::tab:!selected {{ background: {tab_bg}; color: {tab_fg}; }}
        QTabBar::tab:hover {{ background: {hover}; color: white; }}
        QCheckBox {{ color: {colors['text']}; spacing: 8px; }}
        QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {colors['border']}; border-radius: 3px; background-color: {colors['surface']}; }}
        QCheckBox::indicator:checked {{ background-color: {colors['primary']}; border-color: {primary}; }}
        QCheckBox::indicator:unchecked {{ background-color: {colors['surface']}; border-color: {colors['border']}; }}
        QLineEdit {{ background-color: {colors['surface']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 4px; padding: 4px; }}
        QTextEdit {{ background-color: {colors['surface']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 4px; }}
        QProgressBar {{ border: 1px solid {colors['border']}; border-radius: 4px; text-align: center; }}
        QProgressBar::chunk {{ background-color: {colors['primary']}; border-radius: 3px; }}
        QStatusBar {{ background-color: {colors['surface']}; color: {colors['text']}; }}
        /* 경고창 스타일 */
        QMessageBox {{
            background-color: white;
            color: black;
        }}
        QMessageBox QLabel {{
            color: black;
            font-size: 12px;
        }}
        QMessageBox QPushButton {{
            background-color: #007acc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: #005a9e;
        }}
        """
        self.setStyleSheet(style_sheet)
    
    def connect_to_hiworks(self):
        user_id = self.id_input.text().strip()
        user_pw = self.pw_input.text().strip()
        if not user_id or not user_pw:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력하세요.")
            return
        
        logger.info(f"로그인 시도: username={user_id}")
        logger.info(f"자격 증명 저장 체크박스 상태: {self.save_credentials_checkbox.isChecked()}")
        logger.info(f"자동 로그인 체크박스 상태: {self.auto_login_checkbox.isChecked()}")
        
        self.connect_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("로그인 중...")
        self.repaint()
        # QThread + Worker로 로그인 처리
        self.login_thread = QThread()
        headless_mode = self.headless_checkbox.isChecked()
        logger.info(f"백그라운드 모드 설정: {headless_mode}")
        self.login_worker = LoginWorker(user_id, user_pw, headless=headless_mode)
        self.login_worker.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.login_worker.run)
        def on_finished(result):
            if result:
                logger.info("로그인 성공!")
                self.status_label.setText("로그인 성공! 날짜를 선택 후 요청 버튼을 누르세요.")
                self.start_date_input.setEnabled(True)
                self.end_date_input.setEnabled(True)
                self.request_button.setEnabled(True)
                self.worker = self.login_worker.scraper
                
                # 자격 증명 저장 체크박스가 체크되어 있으면 저장
                if self.save_credentials_checkbox.isChecked():
                    logger.info("자격 증명 저장 체크박스가 체크되어 있어 저장을 시도합니다.")
                    self.save_credentials()
                else:
                    logger.info("자격 증명 저장 체크박스가 체크되지 않아 저장하지 않습니다.")
            else:
                logger.error("로그인 실패")
                self.status_label.setText("로그인 실패")
                QMessageBox.critical(self, "오류", "로그인에 실패했습니다.")
            self.progress_bar.setVisible(False)
            self.connect_button.setEnabled(True)
            self.login_thread.quit()
            self.login_thread.wait()
        self.login_worker.finished.connect(on_finished)
        self.login_thread.start()

    def update_status(self, status: str):
        """상태 업데이트"""
        self.status_label.setText(status)
        self.status_bar.showMessage(status)
        logger.info(status)
    

    


    def display_category_tables(self, json_data):
        """카테고리별로 하위 탭에 테이블 표시 (카테고리/상태 컬럼 제외)"""
        def format_datetime(dt_str):
            if not dt_str:
                return ''
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.datetime.strptime(dt_str, fmt)
                    return dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    continue
            return dt_str
        
        def decode_html_entities(text):
            """HTML 엔티티를 실제 문자로 변환합니다."""
            if not text:
                return text
            
            # HTML 엔티티 변환
            html_entities = {
                '&lt;': '<',
                '&gt;': '>',
                '&amp;': '&',
                '&quot;': '"',
                '&#39;': "'",
                '&apos;': "'",
                '&nbsp;': ' ',
                '&copy;': '©',
                '&reg;': '®',
                '&trade;': '™',
                '&hellip;': '…',
                '&mdash;': '—',
                '&ndash;': '–',
                '&lsquo;': ''',
                '&rsquo;': ''',
                '&ldquo;': '"',
                '&rdquo;': '"',
            }
            
            decoded_text = text
            for entity, char in html_entities.items():
                decoded_text = decoded_text.replace(entity, char)
            
            # 숫자 엔티티 변환 (예: &#60; -> <)
            import re
            decoded_text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), decoded_text)
            decoded_text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), decoded_text)
            
            return decoded_text
        
        # 고급 UI 초기화 (필요시)
        self._init_advanced_ui()
        
        # 카테고리 탭 위젯이 이미 생성되어 있으므로 기존 것 사용
        # 기존 카테고리 탭 제거
        while self.category_tab_widget.count() > 0:
            self.category_tab_widget.removeTab(0)
        self.category_tabs.clear()
        
        # 데이터 분류
        schedules = []
        if isinstance(json_data, list):
            schedules = json_data
        elif isinstance(json_data, dict):
            possible_keys = ['schedules', 'data', 'events', 'items', 'list']
            for key in possible_keys:
                if key in json_data and isinstance(json_data[key], list):
                    schedules = json_data[key]
                    break
            if not schedules:
                schedules = [json_data]
        
        # 카테고리별 분류
        cat_dict = defaultdict(list)
        for sch in schedules:
            if isinstance(sch, dict):
                cat = sch.get('category', '기타')
                cat_dict[cat].append(sch)
        
        # 각 카테고리별로 탭 생성
        for cat, sch_list in cat_dict.items():
            if not sch_list:
                continue
                
            # 탭 위젯 생성
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # 테이블 라벨
            table_label = QLabel(f"{cat} 일정 ({len(sch_list)}개)")
            table_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(table_label)
            
            # 테이블 생성
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["시작일시", "종료일시", "제목", "프로젝트", "내용"])
            table.setRowCount(len(sch_list))
            
            # 테이블 데이터 채우기
            for row, schedule in enumerate(sch_list):
                start_date = format_datetime(schedule.get('start_date', schedule.get('start', '')))
                end_date = format_datetime(schedule.get('end_date', schedule.get('end', '')))
                subject = decode_html_entities(schedule.get('subject', schedule.get('title', schedule.get('name', ''))))
                project = decode_html_entities(schedule.get('project_name', schedule.get('project', '')))
                content = decode_html_entities(schedule.get('content', schedule.get('description', schedule.get('desc', ''))))
                
                table.setItem(row, 0, QTableWidgetItem(str(start_date)))
                table.setItem(row, 1, QTableWidgetItem(str(end_date)))
                table.setItem(row, 2, QTableWidgetItem(str(subject)))
                table.setItem(row, 3, QTableWidgetItem(str(project)))
                table.setItem(row, 4, QTableWidgetItem(str(content)))
            
            # 테이블 크기 조정
            table.horizontalHeader().setStretchLastSection(True)
            table.resizeColumnsToContents()
            layout.addWidget(table, 1)  # stretch=1로 추가
            
            # 엑셀 저장 버튼을 테이블 아래로 이동
            excel_btn = QPushButton("엑셀로 저장")
            excel_btn.setFixedWidth(120)
            excel_btn.clicked.connect(lambda _, c=cat: self.save_table_to_excel(c))
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(excel_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            self.category_tab_widget.addTab(tab, cat)
            self.category_tabs[cat] = (tab, table_label, table)
        
        logger.info(f"카테고리별 테이블 생성 완료: {len(self.category_tabs)}개 카테고리")

    def save_table_to_excel(self, cat):
        tab, table_label, table = self.category_tabs[cat]
        headers = []
        for i in range(table.columnCount()):
            h = table.horizontalHeaderItem(i)
            val = h.text() if h and h.text() else f"컬럼{i+1}"
            headers.append(str(val))
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        # 모든 header가 str임을 보장
        headers = [str(h) for h in headers]
        df = pd.DataFrame(data, columns=headers)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{cat}_일정_{now}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(self, "엑셀로 저장", default_name, "Excel Files (*.xlsx)")
        if file_path:
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "저장 완료", f"엑셀 파일로 저장되었습니다:\n{file_path}")


    def show_settings(self):
        """설정 창 표시"""
        QMessageBox.information(self, "설정", "설정 기능은 추후 구현 예정입니다.")
    
    def show_about(self):
        """정보 창 표시"""
        QMessageBox.about(self, "정보", 
                         f"{WINDOW_TITLE}\n\n"
                         "하이웍스 스케줄 데이터를 수집하는 프로그램입니다.\n"
                         "현재 버전: 1.0.0")
    
    def load_saved_credentials(self):
        """저장된 자격 증명을 로드합니다."""
        try:
            credentials = self.credential_manager.load_credentials()
            if credentials:
                self.id_input.setText(credentials.get('username', ''))
                self.pw_input.setText(credentials.get('password', ''))
                self.save_credentials_checkbox.setChecked(True)
                
                # 자동 로그인 설정: 설정 파일 우선, 자격증명 파일 백업
                auto_login_from_settings = settings.get("hiworks.auto_login", False)
                auto_login_from_credentials = credentials.get('auto_login', False)
                auto_login = auto_login_from_settings or auto_login_from_credentials
                
                self.auto_login_checkbox.setChecked(auto_login)
                logger.info(f"자동 로그인 설정 로드: 설정파일={auto_login_from_settings}, 자격증명파일={auto_login_from_credentials}, 최종={auto_login}")
                
                # 자동 로그인이 활성화되어 있으면 자동으로 로그인 시도
                if auto_login:
                    QTimer.singleShot(1000, self.auto_login)
                    
        except Exception as e:
            logger.error(f"저장된 자격 증명 로드 실패: {e}")
    
    def save_credentials(self):
        """현재 입력된 자격 증명을 저장합니다."""
        try:
            logger.info("save_credentials 함수 호출됨")
            username = self.id_input.text().strip()
            password = self.pw_input.text().strip()
            
            logger.info(f"입력된 username 길이: {len(username)}")
            logger.info(f"입력된 password 길이: {len(password)}")
            
            if not username or not password:
                logger.warning("username 또는 password가 비어있어 저장하지 않습니다.")
                return False
            
            auto_login = self.auto_login_checkbox.isChecked()
            logger.info(f"auto_login 설정: {auto_login}")
            
            success = self.credential_manager.save_credentials(
                username, password, auto_login
            )
            
            if success:
                logger.info("자격 증명이 저장되었습니다.")
                return True
            else:
                logger.error("자격 증명 저장에 실패했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"자격 증명 저장 중 오류: {e}")
            import traceback
            logger.error(f"상세 스택 트레이스: {traceback.format_exc()}")
            return False
    
    def auto_login(self):
        """저장된 자격 증명으로 자동 로그인을 시도합니다."""
        if self.auto_login_checkbox.isChecked():
            self.connect_to_hiworks()
    
    def clear_saved_credentials(self):
        """저장된 자격 증명을 삭제합니다."""
        try:
            if self.credential_manager.delete_credentials():
                self.id_input.clear()
                self.pw_input.clear()
                self.save_credentials_checkbox.setChecked(False)
                self.auto_login_checkbox.setChecked(False)
                QMessageBox.information(self, "완료", "저장된 자격 증명이 삭제되었습니다.")
            else:
                QMessageBox.warning(self, "오류", "자격 증명 삭제에 실패했습니다.")
        except Exception as e:
            logger.error(f"자격 증명 삭제 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"자격 증명 삭제 중 오류가 발생했습니다: {e}")
    
    def closeEvent(self, event):
        """창 종료 이벤트"""
        # 웹 브라우저가 열려있으면 종료
        if hasattr(self, 'worker') and self.worker:
            self.worker.close_driver()
        event.accept()



    def request_schedule_data(self):
        """일정 데이터 요청 (요청 버튼 클릭 시 호출)"""
        # 고급 UI 초기화 (필요시)
        self._init_advanced_ui()
        
        start = self.start_date_input.date().toString("yyyy-MM-dd")
        end = self.end_date_input.date().toString("yyyy-MM-dd")
        
        if not start or not end:
            QMessageBox.warning(self, "입력 오류", "시작일과 종료일을 모두 입력하세요.")
            return
            
        if self.worker is None:
            QMessageBox.warning(self, "오류", "로그인 후에만 요청할 수 있습니다.")
            return
            
        self.status_label.setText("일정 JSON 요청 중...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.repaint()
        
        try:
            import json
            result = self.worker.fetch_schedule_json(start, end)
            
            # 세션 만료 체크 및 재로그인 시도
            if isinstance(result, dict) and result.get("need_relogin"):
                logger.info("세션이 만료되었습니다. 사용자에게 재로그인을 요청합니다.")
                self.status_label.setText("세션 만료")
                
                QMessageBox.information(
                    self, 
                    "세션 만료", 
                    "로그인 세션이 만료되었습니다.\n\n"
                    "아이디와 비밀번호를 다시 입력하고 로그인 버튼을 클릭해주세요."
                )
                
                # 로그인 관련 UI를 다시 활성화
                self.connect_button.setEnabled(True)
                self.start_date_input.setEnabled(False)
                self.end_date_input.setEnabled(False)
                self.request_button.setEnabled(False)
                self.worker = None
                
                return
            
            # 오류 응답 체크
            if isinstance(result, dict) and "error" in result:
                error_msg = result.get("error", "알 수 없는 오류")
                logger.error(f"일정 요청 실패: {error_msg}")
                QMessageBox.critical(self, "오류", f"일정 데이터 요청 실패:\n{error_msg}")
                self.status_label.setText("일정 요청 실패")
                return
            
            # JSON 데이터 표시
            pretty = json.dumps(result, ensure_ascii=False, indent=2)
            
            # JSON 뷰에 표시할 때도 HTML 엔티티 변환
            def decode_json_html_entities(obj):
                """JSON 객체 내의 모든 문자열에서 HTML 엔티티를 변환합니다."""
                if isinstance(obj, dict):
                    return {k: decode_json_html_entities(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decode_json_html_entities(item) for item in obj]
                elif isinstance(obj, str):
                    # HTML 엔티티 변환
                    html_entities = {
                        '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"',
                        '&#39;': "'", '&apos;': "'", '&nbsp;': ' ',
                        '&copy;': '©', '&reg;': '®', '&trade;': '™',
                        '&hellip;': '…', '&mdash;': '—', '&ndash;': '–',
                        '&lsquo;': ''', '&rsquo;': ''', '&ldquo;': '"', '&rdquo;': '"',
                    }
                    decoded_text = obj
                    for entity, char in html_entities.items():
                        decoded_text = decoded_text.replace(entity, char)
                    
                    # 숫자 엔티티 변환
                    decoded_text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), decoded_text)
                    decoded_text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), decoded_text)
                    
                    return decoded_text
                else:
                    return obj
            
            # JSON 데이터의 HTML 엔티티 변환
            decoded_result = decode_json_html_entities(result)
            pretty = json.dumps(decoded_result, ensure_ascii=False, indent=2)
            
            self.json_view.setPlainText(pretty)
            
            # JSON 데이터를 카테고리별로 분리하여 테이블로 표시
            self.display_category_tables(result)
            
            # 요청 후 테이블 탭을 기본으로 활성화
            if hasattr(self, 'category_tab_widget'):
                # 테이블 탭이 있으면 해당 탭으로 이동
                table_tab_index = self.tab_widget.indexOf(self.category_tab_widget)
                if table_tab_index != -1:
                    self.tab_widget.setCurrentIndex(table_tab_index)
                    
                    # 카테고리 탭이 있다면 schedule 탭으로 이동
                    if self.category_tabs.get('schedule'):
                        idx = self.category_tab_widget.indexOf(self.category_tabs.get('schedule')[0])
                        if idx != -1:
                            self.category_tab_widget.setCurrentIndex(idx)
                else:
                    # 테이블 탭이 없으면 JSON 탭으로 이동
                    self.tab_widget.setCurrentIndex(0)
            else:
                # 카테고리 탭 위젯이 없으면 JSON 탭으로 이동
                self.tab_widget.setCurrentIndex(0)
            
            self.status_label.setText("일정 JSON 응답 표시 완료")
            
        except Exception as e:
            logger.error(f"일정 데이터 요청 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"일정 데이터 요청 중 오류가 발생했습니다: {e}")
            self.status_label.setText("일정 요청 실패")
        finally:
            self.progress_bar.setVisible(False)

    def save_headless_setting(self):
        """백그라운드 모드 체크박스 상태가 변경될 때 설정을 저장합니다."""
        settings.set("hiworks.headless_mode", self.headless_checkbox.isChecked())
        logger.info(f"백그라운드 모드 설정 변경: {self.headless_checkbox.isChecked()}")

    def save_auto_login_setting(self):
        """자동 로그인 체크박스 상태가 변경될 때 설정을 저장합니다."""
        settings.set("hiworks.auto_login", self.auto_login_checkbox.isChecked())
        logger.info(f"자동 로그인 설정 변경: {self.auto_login_checkbox.isChecked()}")


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 애플리케이션 정보 설정
    app.setApplicationName("하이웍스 스케줄 관리자")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hiworks Schedule Manager")
    
    # 메인 창 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 이벤트 루프 시작
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 