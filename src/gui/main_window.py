import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox,
    QStatusBar, QMenuBar, QMenu, QSplitter, QCheckBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction
from typing import Optional
from config.settings import settings
from config.constants import WINDOW_TITLE, DARK_COLORS, LIGHT_COLORS
from utils.logger import logger
from utils.credential_manager import CredentialManager
from scraper.hiworks_scraper import HiworksScraper


class NavigationThread(QThread):
    """네비게이션을 위한 별도 스레드"""
    navigation_completed = pyqtSignal(dict)
    navigation_error = pyqtSignal(str)

    def __init__(self, scraper, direction, parent=None):
        super().__init__(parent)
        self.scraper = scraper
        self.direction = direction  # "prev" 또는 "next"

    def run(self):
        try:
            if self.direction == "prev":
                success = self.scraper.navigate_to_previous_month()
            else:
                success = self.scraper.navigate_to_next_month()
            if success:
                table_data = self.scraper.extract_schedule_table_data()
                self.navigation_completed.emit(table_data)
            else:
                self.navigation_error.emit(f"{self.direction} 이동 실패")
        except Exception as e:
            self.navigation_error.emit(f"네비게이션 중 오류: {str(e)}")


class WebAccessThread(QThread):
    """웹 접속을 위한 별도 스레드"""
    status_updated = pyqtSignal(str)
    table_data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, user_id, user_pw, headless=True, view_mode="목록", parent=None):
        super().__init__(parent)
        self.scraper: Optional[HiworksScraper] = None
        self.headless = headless
        self.user_id = user_id
        self.user_pw = user_pw
        self.view_mode = view_mode

    def run(self):
        try:
            self.status_updated.emit("WebDriver 설정 중...")
            self.scraper = HiworksScraper(headless=self.headless)
            self.status_updated.emit("하이웍스 로그인 페이지로 이동 중...")
            if self.scraper.login(self.user_id, self.user_pw):
                self.status_updated.emit("로그인 성공!")
                self.status_updated.emit("스케줄 페이지로 이동 중...")
                if self.scraper.execute_view_mode_change(self.view_mode):
                    self.status_updated.emit(f"스케줄 페이지 접근 및 {self.view_mode} 보기 모드 변경 완료!")
                    self.status_updated.emit("스케줄 테이블 데이터를 추출하는 중...")
                    table_data = self.scraper.extract_schedule_table_data()
                    self.table_data_updated.emit(table_data)
                else:
                    self.status_updated.emit("스케줄 페이지 접근 실패")
            else:
                self.error_occurred.emit("로그인 실패 또는 로그인 페이지 접속 실패")
        except Exception as e:
            error_msg = f"웹 접속 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_signal.emit()

    def cleanup(self):
        if self.scraper:
            self.scraper.close_driver()


class MainWindow(QMainWindow):
    """메인 애플리케이션 창"""
    
    def __init__(self):
        super().__init__()
        self.web_thread: Optional[WebAccessThread] = None
        self.nav_thread: Optional[NavigationThread] = None
        self.credential_manager = CredentialManager()
        self.init_ui()
        self.apply_theme()
        self.load_saved_credentials()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 메뉴바 생성
        self.create_menu_bar()
        
        # 상태바 생성
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
        
        # 제목 레이블
        title_label = QLabel("하이웍스 스케줄 관리자")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 설정 영역
        settings_layout = QHBoxLayout()
        
        # 헤드리스 모드 체크박스
        self.headless_checkbox = QCheckBox("백그라운드 모드 (브라우저 창 숨김)")
        self.headless_checkbox.setChecked(settings.get("hiworks.headless_mode", True))
        self.headless_checkbox.setToolTip("체크하면 브라우저 창이 표시되지 않고 백그라운드에서 실행됩니다.")
        settings_layout.addWidget(self.headless_checkbox)
        
        # 보기 모드는 목록으로 고정
        view_mode_label = QLabel("보기 모드: 목록 (고정)")
        view_mode_label.setStyleSheet("color: #666; font-style: italic;")
        settings_layout.addWidget(view_mode_label)
        
        settings_layout.addStretch()  # 오른쪽 여백
        main_layout.addLayout(settings_layout)
        
        # 아이디/비밀번호 입력 영역
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
        
        # 자격 증명 저장 체크박스
        self.save_credentials_checkbox = QCheckBox("자격 증명 저장")
        self.save_credentials_checkbox.setToolTip("아이디와 비밀번호를 안전하게 저장합니다.")
        login_layout.addWidget(self.save_credentials_checkbox)
        
        # 자동 로그인 체크박스
        self.auto_login_checkbox = QCheckBox("자동 로그인")
        self.auto_login_checkbox.setToolTip("프로그램 시작 시 저장된 자격 증명으로 자동 로그인합니다.")
        login_layout.addWidget(self.auto_login_checkbox)
        
        main_layout.addLayout(login_layout)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("시작")
        self.connect_button.clicked.connect(self.connect_to_hiworks)
        self.connect_button.setMinimumHeight(40)
        button_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(button_layout)
        
        # 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 상태 표시 레이블
        self.status_label = QLabel("대기 중...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 스케줄 테이블 영역
        table_layout = QVBoxLayout()
        
        # 년월 정보 및 네비게이션 영역
        nav_layout = QHBoxLayout()
        
        # 이전달 버튼
        self.prev_month_button = QPushButton("◀ 이전달")
        self.prev_month_button.clicked.connect(self.navigate_to_previous_month)
        self.prev_month_button.setEnabled(False)
        nav_layout.addWidget(self.prev_month_button)
        
        # 년월 정보 레이블
        self.month_label = QLabel("날짜 정보 없음")
        self.month_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setStyleSheet("color: #fff; background: #333; padding: 10px; border-radius: 6px;")
        nav_layout.addWidget(self.month_label)
        
        # 다음달 버튼
        self.next_month_button = QPushButton("다음달 ▶")
        self.next_month_button.clicked.connect(self.navigate_to_next_month)
        self.next_month_button.setEnabled(False)
        nav_layout.addWidget(self.next_month_button)
        
        table_layout.addLayout(nav_layout)
        
        # 테이블 제목
        table_label = QLabel("스케줄 테이블 데이터")
        table_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        table_layout.addWidget(table_label)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table_layout.addWidget(self.schedule_table)
        
        table_widget = QWidget()
        table_widget.setLayout(table_layout)
        main_layout.addWidget(table_widget)
        

    
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
        
        # 스타일시트 설정
        style_sheet = f"""
        QMainWindow {{ background-color: {colors['background']}; color: {colors['text']}; }}
        QLabel {{ color: {colors['text']}; }}
        QPushButton {{ background-color: {colors['primary']}; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }}
        QPushButton:hover {{ background-color: {colors['primary']}dd; }}
        QPushButton:disabled {{ background-color: {colors['secondary']}; color: {colors['text_secondary']}; }}
        QCheckBox {{ color: {colors['text']}; spacing: 8px; }}
        QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {colors['border']}; border-radius: 3px; background-color: {colors['surface']}; }}
        QCheckBox::indicator:checked {{ background-color: {colors['primary']}; border-color: {colors['primary']}; }}
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
        """하이웍스에 접속"""
        if self.web_thread and self.web_thread.isRunning():
            QMessageBox.warning(self, "경고", "이미 웹 접속이 진행 중입니다.")
            return
        
        user_id = self.id_input.text().strip()
        user_pw = self.pw_input.text().strip()
        if not user_id or not user_pw:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력하세요.")
            return

        # 자격 증명 저장 체크박스가 체크되어 있으면 저장
        if self.save_credentials_checkbox.isChecked():
            self.save_credentials()

        # 헤드리스 모드 설정 가져오기
        headless_mode = self.headless_checkbox.isChecked()
        
        # 보기 모드는 목록으로 고정
        view_mode = "목록"
        
        # UI 상태 업데이트
        self.connect_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 무한 진행률
        self.status_label.setText("웹 접속 중...")
        
        # 웹 접속 스레드 시작 (헤드리스 모드 및 보기 모드 설정 전달)
        self.web_thread = WebAccessThread(user_id=user_id, user_pw=user_pw, headless=headless_mode, view_mode=view_mode, parent=self)
        self.web_thread.status_updated.connect(self.update_status)
        self.web_thread.table_data_updated.connect(self.update_table_data)
        self.web_thread.error_occurred.connect(self.handle_error)
        self.web_thread.finished_signal.connect(self.on_web_access_finished)
        self.web_thread.start()
    
    def update_status(self, status: str):
        """상태 업데이트"""
        self.status_label.setText(status)
        self.status_bar.showMessage(status)
        logger.info(status)
    

    
    def update_table_data(self, table_data: dict):
        """테이블 데이터 업데이트 (tr/td 테이블 구조 기반)"""
        try:
            if "error" in table_data:
                logger.error(f"테이블 데이터 오류: {table_data['error']}")
                return
            data = table_data.get("data", [])
            if not data:
                logger.warning("테이블 데이터가 비어있습니다.")
                return
            # 헤더와 데이터 분리
            headers = []
            rows = []
            for item in data:
                if item.get("type") == "header":
                    headers = item.get("data", [])
                elif item.get("type") == "data":
                    row = item.get("data", [])
                    if row:
                        rows.append(row)
            if not headers:
                # 헤더가 없으면 기본값
                max_cols = max((len(row) for row in rows), default=1)
                headers = [f"열{i+1}" for i in range(max_cols)]
            # 테이블 설정
            self.schedule_table.clear()
            self.schedule_table.setColumnCount(len(headers))
            self.schedule_table.setHorizontalHeaderLabels(headers)
            self.schedule_table.setRowCount(len(rows))
            # 데이터 채우기
            for row_idx, row_data in enumerate(rows):
                for col_idx, cell in enumerate(row_data):
                    self.schedule_table.setItem(row_idx, col_idx, QTableWidgetItem(cell))
            logger.info(f"테이블 데이터 업데이트 완료: {len(rows)}개 행, {len(headers)}개 열")
            # 년월 정보 업데이트
            current_month = table_data.get("current_month", "날짜 정보 없음")
            self.month_label.setText(current_month)
            # 네비게이션 버튼 활성화
            self.prev_month_button.setEnabled(True)
            self.next_month_button.setEnabled(True)
        except Exception as e:
            logger.error(f"테이블 데이터 업데이트 중 오류: {e}")
    
    def navigate_to_previous_month(self):
        """이전달로 이동합니다."""
        if self.web_thread and self.web_thread.scraper:
            # 이미 네비게이션 중이면 무시
            if self.nav_thread and self.nav_thread.isRunning():
                return
                
            self.status_label.setText("이전달로 이동 중...")
            self.prev_month_button.setEnabled(False)
            self.next_month_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 무한 진행률
            
            # 네비게이션 스레드 시작
            self.nav_thread = NavigationThread(scraper=self.web_thread.scraper, direction="prev", parent=self)
            self.nav_thread.navigation_completed.connect(self.on_navigation_completed)
            self.nav_thread.navigation_error.connect(self.on_navigation_error)
            self.nav_thread.start()
        else:
            QMessageBox.warning(self, "경고", "웹 접속이 필요합니다.")
    
    def navigate_to_next_month(self):
        """다음달로 이동합니다."""
        if self.web_thread and self.web_thread.scraper:
            # 이미 네비게이션 중이면 무시
            if self.nav_thread and self.nav_thread.isRunning():
                return
                
            self.status_label.setText("다음달로 이동 중...")
            self.prev_month_button.setEnabled(False)
            self.next_month_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 무한 진행률
            
            # 네비게이션 스레드 시작
            self.nav_thread = NavigationThread(scraper=self.web_thread.scraper, direction="next", parent=self)
            self.nav_thread.navigation_completed.connect(self.on_navigation_completed)
            self.nav_thread.navigation_error.connect(self.on_navigation_error)
            self.nav_thread.start()
        else:
            QMessageBox.warning(self, "경고", "웹 접속이 필요합니다.")
    
    def on_navigation_completed(self, table_data: dict):
        """네비게이션 완료 처리"""
        self.update_table_data(table_data)
        self.status_label.setText("데이터 로드 완료")
        self.progress_bar.setVisible(False)
        self.prev_month_button.setEnabled(True)
        self.next_month_button.setEnabled(True)
        
        # 스레드 정리
        if self.nav_thread:
            self.nav_thread.deleteLater()
            self.nav_thread = None
    
    def on_navigation_error(self, error_msg: str):
        """네비게이션 오류 처리"""
        self.status_label.setText(error_msg)
        self.progress_bar.setVisible(False)
        self.prev_month_button.setEnabled(True)
        self.next_month_button.setEnabled(True)
        QMessageBox.warning(self, "네비게이션 오류", error_msg)
        
        # 스레드 정리
        if self.nav_thread:
            self.nav_thread.deleteLater()
            self.nav_thread = None
    
    def handle_error(self, error_msg: str):
        """오류 처리"""
        QMessageBox.critical(self, "오류", error_msg)
        logger.error(error_msg)
    
    def on_web_access_finished(self):
        """웹 접속 완료 처리"""
        # UI 상태 복원
        self.connect_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 스레드는 유지 (네비게이션을 위해)
        # 실제 정리는 closeEvent에서 수행
    

    
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
                self.auto_login_checkbox.setChecked(credentials.get('auto_login', False))
                
                # 자동 로그인이 활성화되어 있으면 자동으로 로그인 시도
                if credentials.get('auto_login', False):
                    QTimer.singleShot(1000, self.auto_login)
                    
        except Exception as e:
            logger.error(f"저장된 자격 증명 로드 실패: {e}")
    
    def save_credentials(self):
        """현재 입력된 자격 증명을 저장합니다."""
        try:
            username = self.id_input.text().strip()
            password = self.pw_input.text().strip()
            
            if not username or not password:
                return False
            
            auto_login = self.auto_login_checkbox.isChecked()
            
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
        # 네비게이션 스레드가 실행 중인지 확인
        if self.nav_thread and self.nav_thread.isRunning():
            reply = QMessageBox.question(self, "확인", 
                                       "네비게이션이 진행 중입니다. 정말 종료하시겠습니까?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.nav_thread.terminate()
                self.nav_thread.wait()
            else:
                event.ignore()
                return
        
        if self.web_thread and self.web_thread.isRunning():
            reply = QMessageBox.question(self, "확인", 
                                       "웹 접속이 진행 중입니다. 정말 종료하시겠습니까?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # 웹 브라우저 종료
                if self.web_thread.scraper:
                    self.web_thread.scraper.close_driver()
                
                self.web_thread.terminate()
                self.web_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            # 웹 브라우저가 열려있으면 종료
            if self.web_thread and self.web_thread.scraper:
                self.web_thread.scraper.close_driver()
            event.accept()


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