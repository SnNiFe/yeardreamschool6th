import os
import sys
import subprocess
import importlib
import datetime
import time 
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import platform 
import logging
import warnings
import threading 
import webbrowser # C++ 다운로드 링크 연결용
import json # 👈 [추가됨] 세이브 파일을 읽고 쓰기 위한 부품

# =====================================================================
# [1] 시스템 기본 설정 및 전역 변수
# =====================================================================
# 터미널 창의 불필요한 경고 메시지 숨김 처리
logging.getLogger().setLevel(logging.ERROR) 
warnings.filterwarnings("ignore") 

# 봇 작동 상태를 제어하는 전역 변수 (True일 때만 루프가 돌아감)
is_running = False 
driver = None


# =====================================================================
# [2] 필수 패키지 자동 설치 및 환경 세팅 함수
# =====================================================================
def check_and_install_packages():
    """실행에 필요한 파이썬 라이브러리가 있는지 검사하고 없으면 설치합니다."""
    print("🔍 필수 라이브러리를 점검합니다...")
    packages = {
        "selenium": "selenium",
        "webdriver-manager": "webdriver_manager",
        "schedule": "schedule",
        "pyautogui": "pyautogui",
        "pyzbar": "pyzbar",
        "Pillow": "PIL"
    }
    
    missing_packages = []
    for pip_name, module_name in packages.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(pip_name)
            
    if not missing_packages:
        return 
        
    print(f"⚙️ 부족한 패키지를 설치합니다: {', '.join(missing_packages)}")
    try:
        # pip 도구 자체를 최신 버전으로 업데이트
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    except Exception:
        pass 

    try:
        # 누락된 패키지 일괄 설치 시도
        install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # 권한 에러 방지를 위해 사용자(--user) 모드 및 보호 환경 강제 돌파 옵션 적용
            print("⚠️ 기본 설치 실패. 사용자 권한으로 강제 설치를 재시도합니다...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "--user"] + missing_packages)
    except Exception as e:
        print(f"❌ 설치 중 에러 발생: {e}")

def setup_mac_env():
    """Mac 환경일 경우 QR 스캔 엔진인 zbar를 Homebrew로 자동 설치합니다."""
    if platform.system() == "Darwin":
        try:
            subprocess.run(["brew", "install", "zbar"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            pass

# 프로그램 시작 시 환경 세팅 즉시 실행
check_and_install_packages()
setup_mac_env() 

# ---------------------------------------------------------------------
# 패키지 설치 완료 후 본격적으로 라이브러리 불러오기
# ---------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import schedule
import pyautogui
from PIL import Image

# --- [핵심 수정: QR 엔진 로드 및 에러 복구 팝업 복원] ---
QR_AVAILABLE = True
try:
    from pyzbar.pyzbar import decode
except Exception as e:
    QR_AVAILABLE = False
    print(f"\n⚠️ [경고] QR 스캐너 모듈 고장! (에러 원인: {e})")
    
    # 윈도우 환경에서 구형 C++(2013)이 없어서 터진 경우 자동 다운로드 안내
    if platform.system() == "Windows":
        def ask_cpp_install():
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            result = messagebox.askyesno(
                "QR 스캐너 복구 (Visual C++ 2013 필요)",
                "새 컴퓨터이신가요? QR 모듈이 작동하지 않습니다.\n\n"
                "해당 모듈(pyzbar)을 구동하려면 마이크로소프트의 구형 뼈대인\n"
                "'Visual C++ 2013 재배포 가능 패키지(x64)'가 반드시 필요합니다.\n\n"
                "공식 설치 파일을 다운로드하시겠습니까?"
            )
            root.destroy()
            return result
            
        if ask_cpp_install():
            print("🌐 브라우저를 열어 C++ 2013 설치 파일을 다운로드합니다...")
            webbrowser.open("https://aka.ms/highdpimfc2013x64enu")
            print("💡 안내: 다운로드된 파일을 설치하신 후, PC를 반드시 '재부팅'하고 봇을 켜주세요!")
            time.sleep(3)
            sys.exit(0) 

current_folder = os.getcwd()


# =====================================================================
# [3] 웹 브라우저 및 봇 유틸리티 함수
# =====================================================================
def get_browser_driver():
    """크롬 브라우저를 봇 프로필로 연결합니다. 실패 시 엣지(Edge)로 우회합니다."""
    # 카메라, 마이크 권한 요청을 자동으로 차단하여 팝업 방해 금지
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,    
        "profile.default_content_setting_values.media_stream_camera": 2, 
        "profile.default_content_setting_values.geolocation": 2          
    }
    try:
        print("🌐 크롬(Chrome) 브라우저 연결 시도 중...")
        c_options = ChromeOptions()
        c_options.add_experimental_option("detach", True) # 봇 종료 시 브라우저 유지
        c_options.add_argument("--disable-blink-features=AutomationControlled") # 봇 탐지 방지
        c_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        c_options.add_experimental_option("useAutomationExtension", False)
        c_options.add_argument("--remote-allow-origins=*")
        c_options.add_argument("--no-sandbox")
        c_options.add_argument("--disable-dev-shm-usage")
        c_options.add_experimental_option("prefs", prefs)
        
        # 현재 폴더에 봇 전용 쿠키(로그인 정보) 보관 폴더 생성
        chrome_profile = os.path.join(current_folder, "bot_profile_chrome")
        c_options.add_argument(f"user-data-dir={chrome_profile}")
        
        d = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=c_options)
        print("✅ 크롬 연결 성공!")
        return d
    except Exception as e:
        print(f"⚠️ 크롬 연결 실패 (원인: {e}). 엣지(Edge)로 전환합니다...")

    try:
        print("🌐 엣지(Edge) 브라우저 연결 시도 중...")
        e_options = EdgeOptions()
        e_options.add_experimental_option("detach", True)
        e_options.add_argument("--disable-blink-features=AutomationControlled")
        e_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        e_options.add_experimental_option("useAutomationExtension", False)
        e_options.add_experimental_option("prefs", prefs)
        edge_profile = os.path.join(current_folder, "bot_profile_edge")
        e_options.add_argument(f"user-data-dir={edge_profile}")
        
        d = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=e_options)
        print("✅ 엣지 연결 성공!")
        return d
    except Exception as e:
        print(f"❌ 크롬과 엣지 모두 연결할 수 없습니다. 에러: {e}")
        return None

def play_beep():
    """QR 코드를 발견했을 때 OS별로 경고음을 재생합니다."""
    try:
        current_os = platform.system()
        if current_os == "Windows":
            import winsound
            winsound.Beep(1000, 500)
        elif current_os == "Darwin": 
            os.system("afplay /System/Library/Sounds/Ping.aiff") 
        else:
            print('\a') 
    except Exception:
        pass

def show_login_warning():
    """최초 실행이거나 로그인 쿠키가 풀렸을 때 뜨는 경고창입니다."""
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 
    messagebox.showwarning(
        "수동 로그인 필요", 
        "자동 로그인이 실패했거나 봇 프로필이 초기화되었습니다.\n\n"
        "열려있는 브라우저 창에서 '수동으로 로그인'을 완료한 후, 매크로를 다시 실행해 주세요!"
    )
    root.destroy()

def get_today_date_str():
    """오늘 날짜를 추출합니다. (예: 6/25)"""
    now = datetime.datetime.now()
    return f"{now.month}/{now.day}"

def close_annoying_popups(driver):
    """화면을 가리는 각종 공지사항 팝업이나 iframe(액자) 오버레이를 박살냅니다."""
    try:
        popup_texts = ["오늘 그만 보기", "오늘 하루 보지 않기", "다시 보지 않기", "닫기", "오늘 하루 열지 않음"]
        closed = False
        
        # 1단계: 기본 창에서 버튼 글씨 찾기
        for text in popup_texts:
            btns = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            for btn in btns:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"🛡️ 방해 팝업 치움: '{text}' 버튼 클릭")
                    time.sleep(0.5)
                    closed = True
                    break
            if closed: break

        # 2단계: 못 찾았다면 iframe 내부로 침투하여 찾기
        if not closed:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    for text in popup_texts:
                        btns = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                        for btn in btns:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                                print(f"🛡️ 방해 팝업(iframe 내부) 치움: '{text}' 버튼 클릭")
                                time.sleep(0.5)
                                closed = True
                                break
                        if closed: break
                except Exception:
                    pass
                finally:
                    driver.switch_to.default_content() # 원래 화면 복귀
                if closed: break

        # 3단계: 그래도 못 닫았으면 최후의 수단으로 화면 빈 공간(회색 여백) 타격 및 ESC 연타
        if not closed:
            driver.execute_script("var el = document.elementFromPoint(10, 10); if(el) el.click();")
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            
    except Exception:
        pass # 에러가 나도 메인 작업(출석)이 멈추지 않도록 무시함

def scan_screen_for_qr(timeout_minutes=5):
    """지정된 시간 동안 화면 전체를 스크린샷 찍어 QR 코드가 있는지 감시합니다."""
    global is_running 
    if not QR_AVAILABLE:
        print("\n❌ QR 감시 모듈이 비활성화 되어있습니다.")
        return None

    print(f"👀 [QR 감시 모드] 화면에서 QR 코드를 찾는 중... (최대 {timeout_minutes}분 동안만 감시)")
    start_time = datetime.datetime.now()

    while is_running:
        current_time = datetime.datetime.now()
        elapsed_minutes = (current_time - start_time).total_seconds() / 60.0
        if elapsed_minutes > timeout_minutes:
            print(f"⏰ {timeout_minutes}분이 경과하여 QR 감시를 자동으로 종료합니다.")
            return None
            
        try:
            screenshot = pyautogui.screenshot()
            decoded_objects = decode(screenshot)
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                if qr_data.startswith("http"):
                    print(f"🎉 QR 코드 발견! 추출된 링크: {qr_data}")
                    play_beep() 
                    return qr_data 
        except Exception:
            pass 
        time.sleep(2) 
    return None


# =====================================================================
# [4] 엘리스 로그인 및 강의실 자동 입장 메인 로직
# =====================================================================
def run_bot():
    """봇의 핵심 행동(로그인 -> 강의실 탐색 -> 입장 -> 스캔)을 수행합니다."""
    global driver, is_running
    if not is_running: 
        return
        
    print(f"\n🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] 자동 입장을 시작/확인 합니다!")
    
    # 크롬 프로필이 꼬이지 않도록 이전에 켜둔 창은 깔끔하게 닫고 새로 출발
    if driver is not None:
        print("🧹 크롬 프로필 충돌 방지를 위해 기존 창을 완전히 닫고 새 창을 준비합니다.")
        try:
            driver.quit()
        except Exception:
            pass
        driver = None

    driver = get_browser_driver()
    if driver is None:
        return 
    
    # GUI 상단에 적힌 URL 가져오기
    url = url_entry.get().strip()
    if not url:
        url = "https://yeardream2026.elice.io/my/lecturerooms?page=1"
    
    try:
        driver.get(url)
        login_wait = WebDriverWait(driver, 5) 
        login_button = login_wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., '로그인')]")))
        
        print("로그인 화면 감지됨! 자동완성 적용 대기 중...")
        time.sleep(3) 
        
        # 비밀번호 칸을 건드려서 브라우저 자동완성 강제 활성화 유도
        pw_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if pw_inputs:
            pw_input = pw_inputs[0]
            pw_input.click() 
            time.sleep(1.5) 
            pw_input.send_keys(Keys.SPACE)
            pw_input.send_keys(Keys.BACKSPACE)
            time.sleep(1) 
            pw_input.send_keys(Keys.TAB) 
            time.sleep(1.5) 
        
        login_button = login_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '로그인')]")))
        driver.execute_script("arguments[0].click();", login_button)
        
        print("로그인 처리 중! '라이브 강의실' 목록이 로딩될 때까지 스마트하게 기다립니다...")
        list_wait = WebDriverWait(driver, 30)
        list_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '강의실')]")))
        print("✅ 강의실 목록 로딩 완벽 확인!")
        
        close_annoying_popups(driver) # 방해 팝업 치우기
    except Exception:
        if is_running:
            print("로그인 화면이 감지되지 않았습니다. (세션 유지 상태로 진행)")

    if not is_running: return 

    # 로그인 실패 여부 재확인
    remaining_login_buttons = driver.find_elements(By.XPATH, "//button[contains(., '로그인')]")
    if remaining_login_buttons and remaining_login_buttons[0].is_displayed():
        print("❌ 로그인이 완료되지 않았습니다. 팝업을 띄웁니다.")
        show_login_warning()
        return 
    
    print("✅ 로그인 확인됨. 강의실 탐색 시작.")
    today_date = get_today_date_str()
    print(f"오늘 날짜 타겟 접두사: {today_date}")

    try:
        # 1. 화면에 있는 글자 중 오늘 날짜(예: 6/25)가 포함된 요소를 모두 수집
        wait = WebDriverWait(driver, 20)
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{today_date}')]")))

        target_found = False
        for elem in elements:
            try:
                text = elem.text
                # 2. 텍스트 안에 '오늘 날짜'와 '강의실'이라는 두 키워드가 동시에 있으면 무조건 정답으로 간주
                if len(text) > 0 and len(text) < 100 and "강의실" in text:
                    print(f"🎯 매칭되는 강의실 발견: {text}")
                    driver.execute_script("arguments[0].click();", elem)
                    target_found = True
                    break
            except Exception:
                continue
        
        if not target_found:
            print("⚠️ 현재 열려있는 오늘 날짜 기반의 강의실을 찾지 못했습니다. (대기 모드 유지)")
            return 

        print("오버랩 팝업 및 입장 버튼 대기 중...")
        time.sleep(5) 
        if not is_running: return 
        
        # 입장 버튼 클릭 시도
        click_success = False
        try:
            enter_buttons = driver.find_elements(By.XPATH, "//*[normalize-space()='입장하기']")
            for btn in enter_buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1.5) 
                    click_success = True
                    print("기본 화면에서 입장 클릭 성공!")
        except Exception:
            pass

        # 기본 화면에 없으면 iframe 안쪽으로 침투해서 입장 버튼 탐색
        if not click_success:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe) 
                    enter_buttons = driver.find_elements(By.XPATH, "//*[normalize-space()='입장하기']")
                    for btn in enter_buttons:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1.5) 
                            click_success = True
                            print("iframe 내부에서 입장 클릭 성공!")
                            break 
                except Exception:
                    pass
                finally:
                    driver.switch_to.default_content() 
                if click_success:
                    break 
                    
        # 입장에 성공했다면 새 창에서 QR 감시 시작
        if click_success:
            print("🎉 강의실 입장 버튼 클릭 완료! 페이지 로딩을 기다립니다...")
            time.sleep(5) 
            close_annoying_popups(driver)

            # === 💬 라이브 강의실 채팅창 열기 로직 ===
            print("💬 '채팅' 아이콘 버튼을 속성까지 샅샅이 탐색합니다...")
            chat_clicked = False
            try:
                # 텍스트뿐만 아니라 툴팁(title, alt) 및 접근성(aria-label) 속성까지 뒤지는 강력한 XPATH
                xpath_query = "//*[contains(@title, '채팅') or contains(@aria-label, '채팅') or contains(@alt, '채팅') or contains(text(), '채팅')]"
                
                # 1단계: 기본 화면에서 버튼 검색 및 클릭
                chat_btns = driver.find_elements(By.XPATH, xpath_query)
                for btn in chat_btns:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        print("✅ 기본 화면에서 아이콘 버튼을 찾아 채팅창 열기 성공!")
                        chat_clicked = True
                        break
                
                # 2단계: 기본 화면에 없으면 iframe 내부로 진입해서 탐색
                if not chat_clicked:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        try:
                            driver.switch_to.frame(iframe)
                            chat_btns = driver.find_elements(By.XPATH, xpath_query)
                            for btn in chat_btns:
                                if btn.is_displayed():
                                    driver.execute_script("arguments[0].click();", btn)
                                    print("✅ iframe 내부에서 아이콘 버튼을 찾아 채팅창 열기 성공!")
                                    chat_clicked = True
                                    break
                        except Exception:
                            pass
                        finally:
                            driver.switch_to.default_content() # 원래 화면으로 복귀
                        if chat_clicked: break
                        
                if not chat_clicked:
                    print("⚠️ '채팅' 아이콘/버튼을 속성까지 뒤졌으나 찾지 못했습니다.")
                else:
                    time.sleep(2) # 채팅창이 완전히 열릴 때까지 잠시 대기
            except Exception as ce:
                print(f"⚠️ 채팅창을 여는 중 오류 발생: {ce}")
            # =============================================

            found_url = scan_screen_for_qr()
            if found_url and is_running:
                print("🌐 출석 링크를 새 탭으로 엽니다!")
                original_window = driver.current_window_handle 
                driver.execute_script(f"window.open('{found_url}', '_blank');")
                time.sleep(2) 
                
                # 포커스를 출석용 새 탭으로 전환
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                        
                print("👀 출석 화면을 덮는 오버레이(팝업) 대기 중...")
                time.sleep(4) 
                
                # 출석 탭을 가리는 '닫기' 팝업 제거
                closed_overlay = False
                try:
                    close_buttons = driver.find_elements(By.XPATH, "//*[normalize-space()='닫기']")
                    for btn in close_buttons:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            print("✅ 출석 화면 기본 창에서 '닫기' 버튼을 치웠습니다!")
                            closed_overlay = True
                            break
                except Exception:
                    pass
                
                if not closed_overlay:
                    try:
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        for iframe in iframes:
                            try:
                                driver.switch_to.frame(iframe)
                                close_buttons = driver.find_elements(By.XPATH, "//*[normalize-space()='닫기']")
                                for btn in close_buttons:
                                    if btn.is_displayed():
                                        driver.execute_script("arguments[0].click();", btn)
                                        print("✅ 출석 화면 iframe 안에서 '닫기' 버튼을 찾아 치웠습니다!")
                                        closed_overlay = True
                                        break
                            except Exception:
                                pass
                            finally:
                                driver.switch_to.default_content()
                            if closed_overlay:
                                break
                    except Exception:
                        driver.switch_to.default_content()

                # --- [출석 성공 시 탭 자동 닫기 로직] ---
                print("👀 출석 완료 텍스트 대기 중...")
                try:
                    # 화면에 '출석' 글씨가 뜰 때까지 최대 10초 대기
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '출석')]")))
                    print("✅ 출석 완료 글씨 확인! 탭을 닫고 원래 강의실로 복귀합니다.")
                    driver.close() # 새 탭(현재 탭)만 살짝 닫기
                    driver.switch_to.window(original_window) # 원래 강의실 창으로 시선 복귀
                except Exception:
                    print("⚠️ '출석' 글씨를 찾지 못했습니다. 혹시 모르니 탭을 그대로 둡니다.")
                # ----------------------------------------
        else:
            print("입장 버튼 클릭 실패.")
    except Exception as e:
        if is_running:
            print(f"작동 중 에러 발생: {e}")


# =====================================================================
# [5] GUI 및 스케줄러 루프 제어
# =====================================================================
class PrintLogger:
    """print() 함수의 출력을 터미널이 아닌 GUI의 검은 텍스트 창으로 가로채서 띄워주는 도구입니다."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, message):
        self.text_widget.after(0, self._append, message)
    def _append(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END) 
    def flush(self):
        pass

def run_scheduler_loop():
    """GUI에서 체크한 시간들을 취합해 백그라운드 타이머에 등록하고 무한 대기합니다."""
    global is_running
    target_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    # 사용자가 GUI에서 체크한 5분 간격 시간들만 골라냅니다.
    target_times = []
    for t_str, var in morning_vars.items():
        if var.get():
            target_times.append(t_str)
    for t_str, var in afternoon_vars.items():
        if var.get():
            target_times.append(t_str)
            
    if not target_times:
        print("\n⚠️ 선택된 타이머 시간이 없습니다! 기본 모드로 실행만 1회 진행합니다.")
    else:
        print("\n⏳ 선택된 예약 타이머 설정 중...")
        for day in target_days:
            for t in target_times:
                getattr(schedule.every(), day).at(t).do(run_bot)
                print(f" - [{day.capitalize()}] {t} 실행 예약 등록 완료")
                
    print("\n✅ 예약 시스템 준비 완료! 백그라운드 실시간 감시를 시작합니다.")
    print("💡 [통합 기능] 현재 시점 기준으로 접속 가능한 강의가 있는지 즉시 1회 검사를 진행합니다...")
    
    if is_running:
        run_bot() # 시작하자마자 1회 즉시 실행
    
    if is_running and target_times:
        print("\n⏳ 1회 즉시 검사가 종료되었습니다. 다음 예약 스케줄에 맞춰 대기합니다... (창을 최소화해 두세요)")

    while is_running:
        schedule.run_pending()
        time.sleep(1) 
    print("🛑 스케줄러 대기 상태가 종료되었습니다.")

def create_gui():
    global url_entry, morning_vars, afternoon_vars
    
    root = tk.Tk()
    root.title("엘리스 통합 자동 출석 매니저")
    root.geometry("640x700") 
    root.configure(bg="#f4f4f4")
    
    # --- [신규 추가] 세이브 파일(Config) 불러오기 로직 ---
    config_file = os.path.join(current_folder, "bot_config.json")
    def load_config():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # 세이브 파일이 없거나 에러가 나면 기본값 반환
            return {
                "url": "https://yeardream2026.elice.io/my/lecturerooms?page=1",
                "morning": ["09:05", "09:10"],
                "afternoon": ["16:25", "16:30"],
                "close_browser": True
            }
            
    def save_config():
        saved_data = {
            "url": url_entry.get().strip(),
            "morning": [t for t, var in morning_vars.items() if var.get()],
            "afternoon": [t for t, var in afternoon_vars.items() if var.get()],
            "close_browser": close_browser_var.get()
        }
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(saved_data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    # 프로그램 켜지자마자 세이브 데이터 장착
    saved_config = load_config()
    # --------------------------------------------------
    
    # 세이브된 값으로 브라우저 닫기 옵션 설정
    close_browser_var = tk.BooleanVar(value=saved_config.get("close_browser", True)) 
    
    title_lbl = tk.Label(root, text="🚀 엘리스 LXP 통합 출석 자동화 시스템", font=("Helvetica", 14, "bold"), bg="#f4f4f4")
    title_lbl.pack(pady=10)
    
    url_frame = tk.LabelFrame(root, text="🌐 엘리스 강의실 대시보드 URL 주소 설정", font=("Helvetica", 9, "bold"), bg="#f4f4f4", padx=10, pady=5)
    url_frame.pack(padx=20, pady=5, fill=tk.X)
    
    url_entry = tk.Entry(url_frame, font=("Consolas", 10))
    # 세이브된 주소 넣기
    url_entry.insert(0, saved_config.get("url", "https://yeardream2026.elice.io/my/lecturerooms?page=1"))
    url_entry.pack(fill=tk.X, expand=True, pady=2)
    
    time_frame = tk.LabelFrame(root, text="⏰ 타이머 실행 시간 선택 (5분 간격)", font=("Helvetica", 9, "bold"), bg="#f4f4f4", padx=10, pady=5)
    time_frame.pack(padx=20, pady=5, fill=tk.X)
    
    m_lbl = tk.Label(time_frame, text="오전 타겟 (09:00 ~ 09:30):", font=("Helvetica", 9, "bold"), bg="#f4f4f4")
    m_lbl.pack(anchor=tk.W, pady=2)
    
    m_chk_frame = tk.Frame(time_frame, bg="#f4f4f4")
    m_chk_frame.pack(fill=tk.X, anchor=tk.W)
    
    morning_slots = ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30"]
    morning_vars = {}
    # 세이브된 오전 체크박스 설정 가져오기
    active_morning = saved_config.get("morning", ["09:05", "09:10"])
    
    for slot in morning_slots:
        is_chk = slot in active_morning
        morning_vars[slot] = tk.BooleanVar(value=is_chk)
        cb = tk.Checkbutton(m_chk_frame, text=slot.split(":")[1]+"분", variable=morning_vars[slot], bg="#f4f4f4", font=("Helvetica", 9))
        cb.pack(side=tk.LEFT, padx=4)
        
    a_lbl = tk.Label(time_frame, text="오후 타겟 (16:20 ~ 17:00):", font=("Helvetica", 9, "bold"), bg="#f4f4f4")
    a_lbl.pack(anchor=tk.W, pady=2)
    
    a_chk_frame1 = tk.Frame(time_frame, bg="#f4f4f4")
    a_chk_frame1.pack(fill=tk.X, anchor=tk.W)
    
    afternoon_slots = ["16:20", "16:25", "16:30", "16:35", "16:40", "16:45", "16:50", "16:55", "17:00"]
    afternoon_vars = {}
    # 세이브된 오후 체크박스 설정 가져오기
    active_afternoon = saved_config.get("afternoon", ["16:25", "16:30"])
    
    for idx, slot in enumerate(afternoon_slots):
        is_chk = slot in active_afternoon
        afternoon_vars[slot] = tk.BooleanVar(value=is_chk)
        cb = tk.Checkbutton(a_chk_frame1, text=slot.split(":")[1]+"분" if "16" in slot else "17:00", variable=afternoon_vars[slot], bg="#f4f4f4", font=("Helvetica", 9))
        cb.pack(side=tk.LEFT, padx=3)

    def start_integrated_mode():
        global is_running
        is_running = True
        save_config() # [추가됨] 가동 시작 버튼을 누를 때 현재 상태 저장!
        btn_start.config(state=tk.DISABLED, text="시스템 실시간 가동 중...")
        btn_stop.config(state=tk.NORMAL) 
        url_entry.config(state=tk.DISABLED)
        threading.Thread(target=run_scheduler_loop, daemon=True).start()

    def stop_bot():
        global is_running, driver
        print("\n🛑 시스템 중지 요청 수신. 안전하게 프로세스를 정지합니다...")
        is_running = False
        schedule.clear()
        
        if close_browser_var.get() and driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
            driver = None
            print("✅ 봇 중지 및 열려있던 크롬 브라우저를 종료했습니다.")
        else:
            print("✅ 봇 엔진만 정지되었습니다. (강의 연속 시청을 위해 화면 브라우저는 유지)")

        btn_start.config(state=tk.NORMAL, text="▶️ 통합 자동 출석 가동 시작")
        btn_stop.config(state=tk.DISABLED)
        url_entry.config(state=tk.NORMAL)
        print("💡 설정을 변경한 후 다시 가동할 수 있습니다.\n")

    ctrl_frame = tk.Frame(root, bg="#f4f4f4")
    ctrl_frame.pack(pady=5)

    btn_start = tk.Button(ctrl_frame, text="▶️ 통합 자동 출석 가동 시작", font=("Helvetica", 11, "bold"), 
                     width=42, height=2, command=start_integrated_mode, bg="#4CAF50", fg="black")
    btn_start.pack(pady=3)
    
    btn_stop = tk.Button(ctrl_frame, text="⏹️ 작동 중지 및 초기화", font=("Helvetica", 11, "bold"), 
                         width=42, height=2, command=stop_bot, fg="red", state=tk.DISABLED)
    btn_stop.pack(pady=3)

    chk_close = tk.Checkbutton(root, text="프로그램 중지/종료 시 브라우저 같이 닫기", 
                               variable=close_browser_var, bg="#f4f4f4", font=("Helvetica", 9))
    chk_close.pack(pady=2)
    
    tip_lbl = tk.Label(root, text="💡 주의: 창을 남겨두더라도, 나중에 봇을 [다시 시작]하면 충돌 방지를 위해 기존 창을 자동 종료하고 시작합니다.", 
                       font=("Helvetica", 8), bg="#f4f4f4", fg="#777777")
    tip_lbl.pack()

    log_frame = tk.Frame(root)
    log_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, bg="black", fg="#00ff00", font=("Consolas", 9), 
                       yscrollcommand=scrollbar.set, state=tk.NORMAL)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=log_text.yview)

    sys.stdout = PrintLogger(log_text)
    sys.stderr = PrintLogger(log_text)

    print("환영합니다! 세이브 데이터(체크박스, 주소)를 성공적으로 불러왔습니다.")
    print("가동 버튼을 누르거나 프로그램을 끄면 현재 설정이 자동으로 영구 저장됩니다.")

    def on_closing():
        global is_running, driver
        is_running = False
        save_config() # [추가됨] X 버튼으로 프로그램을 끌 때 최종 상태를 한 번 더 저장!
        if close_browser_var.get() and driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
if __name__ == "__main__":
    create_gui()