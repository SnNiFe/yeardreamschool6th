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
import webbrowser 
import json 
import ctypes      
import traceback   
import calendar    # 👈 [추가됨] 미니 달력을 만들기 위한 내장 모듈


# =====================================================================
# [1] 시스템 기본 설정 및 전역 변수
# =====================================================================
logging.getLogger().setLevel(logging.ERROR) 
warnings.filterwarnings("ignore") 

is_running = False 
driver = None

# 👇 [수정됨] 단일 변수 대신 딕셔너리 형태로 출석 로그를 통째로 메모리에 들고 있습니다.
attendance_log = {}
# 👇 [여기서부터 3줄 추가] 오전/오후 출석 완료 여부를 기억하는 변수
morning_done = False
afternoon_done = False
last_attendance_date = ""

# =====================================================================
# [2] 필수 패키지 자동 설치 및 환경 세팅 함수
# =====================================================================
def check_and_install_packages():
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
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    except Exception:
        pass 

    try:
        install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ 기본 설치 실패. 사용자 권한으로 강제 설치를 재시도합니다...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "--user"] + missing_packages)
    except Exception as e:
        print(f"❌ 설치 중 에러 발생: {e}")

def setup_mac_env():
    if platform.system() == "Darwin":
        try:
            subprocess.run(["brew", "install", "zbar"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            pass

check_and_install_packages()
setup_mac_env() 

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

QR_AVAILABLE = True
try:
    from pyzbar.pyzbar import decode
except Exception as e:
    QR_AVAILABLE = False
    print(f"\n⚠️ [경고] QR 스캐너 모듈 고장! (에러 원인: {e})")
    if platform.system() == "Windows":
        def ask_cpp_install():
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            result = messagebox.askyesno(
                "QR 스캐너 복구 (Visual C++ 2013 필요)",
                "해당 모듈(pyzbar)을 구동하려면 마이크로소프트의 구형 뼈대인\n"
                "'Visual C++ 2013 재배포 가능 패키지(x64)'가 반드시 필요합니다.\n\n"
                "공식 설치 파일을 다운로드하시겠습니까?"
            )
            root.destroy()
            return result
        if ask_cpp_install():
            print("🌐 브라우저를 열어 C++ 2013 설치 파일을 다운로드합니다...")
            webbrowser.open("https://aka.ms/highdpimfc2013x64enu")
            time.sleep(3)
            sys.exit(0) 

current_folder = os.getcwd()


# =====================================================================
# [3] 웹 브라우저 및 유틸리티 함수
# =====================================================================
def get_browser_driver():
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,    
        "profile.default_content_setting_values.media_stream_camera": 2, 
        "profile.default_content_setting_values.geolocation": 2          
    }
    try:
        c_options = ChromeOptions()
        c_options.add_experimental_option("detach", True) 
        c_options.add_argument("--disable-blink-features=AutomationControlled")
        c_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        c_options.add_experimental_option("useAutomationExtension", False)
        c_options.add_argument("--remote-allow-origins=*")
        c_options.add_argument("--no-sandbox")
        c_options.add_argument("--disable-dev-shm-usage")
        c_options.add_experimental_option("prefs", prefs)
        
        chrome_profile = os.path.join(current_folder, "bot_profile_chrome")
        c_options.add_argument(f"user-data-dir={chrome_profile}")
        
        d = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=c_options)
        return d
    except Exception as e:
        print(f"⚠️ 크롬 연결 실패. 엣지(Edge)로 전환합니다... ({e})")

    try:
        e_options = EdgeOptions()
        e_options.add_experimental_option("detach", True)
        e_options.add_argument("--disable-blink-features=AutomationControlled")
        e_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        e_options.add_experimental_option("useAutomationExtension", False)
        e_options.add_experimental_option("prefs", prefs)
        edge_profile = os.path.join(current_folder, "bot_profile_edge")
        e_options.add_argument(f"user-data-dir={edge_profile}")
        
        d = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=e_options)
        return d
    except Exception as e:
        print(f"❌ 크롬과 엣지 모두 연결할 수 없습니다. 에러: {e}")
        return None

def play_beep():
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
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 
    messagebox.showwarning("수동 로그인 필요", "자동 로그인이 실패했습니다. 브라우저 창에서 수동으로 로그인 후 다시 실행해 주세요!")
    root.destroy()

def get_today_date_str():
    now = datetime.datetime.now()
    return f"{now.month}/{now.day}"

def close_annoying_popups(driver):
    try:
        popup_texts = ["오늘 그만 보기", "오늘 하루 보지 않기", "다시 보지 않기", "닫기", "오늘 하루 열지 않음"]
        closed = False
        
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
                except: pass
                finally: driver.switch_to.default_content() 
                if closed: break

        if not closed:
            driver.execute_script("var el = document.elementFromPoint(10, 10); if(el) el.click();")
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            
    except: pass 

def scan_screen_for_qr(timeout_minutes=5):
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
        except: pass 
        time.sleep(2) 
    return None


# =====================================================================
# [4] 엘리스 로그인 및 강의실 자동 입장 메인 로직 (🛡️ 무적 루프 적용)
# =====================================================================

# 👇 [새로 추가] UI와 상관없이 출석 기록만 안전하게 DB에 저장하는 함수
def save_attendance_to_file():
    global attendance_log
    config_file = os.path.join(os.getcwd(), "bot_config.json")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
        
    data["attendance_log"] = attendance_log # 출석 기록 업데이트
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass


def run_bot():
    global driver, is_running, attendance_log
    
    if not is_running: 
        return
        
    # [새로운 날짜 확인 및 DB 초기화]
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if today_str not in attendance_log:
        attendance_log[today_str] = {"morning": False, "afternoon": False}
        print(f"📅 새로운 날짜({today_str})가 되어 출석 기록을 준비합니다.")

    # 👇 [수정된 구역] 무작정 스킵하지 않고 상황을 판단합니다!
    current_hour = datetime.datetime.now().hour  
    is_already_done = False
    
    if current_hour < 12 and attendance_log[today_str].get("morning") == True:
        is_already_done = True
    elif current_hour >= 12 and attendance_log[today_str].get("afternoon") == True:
        is_already_done = True

    if is_already_done:
        # 출석은 했지만, 현재 브라우저가 살아있는지 슬쩍 찔러봄
        is_browser_alive = False
        if driver is not None:
            try:
                driver.current_url 
                is_browser_alive = True
            except: pass
            
        if is_browser_alive:
            print("✅ [스킵] 이미 출석이 완료되었고, 현재 강의 시청 중이시므로 방해하지 않습니다.")
            return # 창이 켜져 있으니 진짜 스킵
        else:
            print("💡 출석은 이미 기록되어 있지만, 강의 시청을 위해 강의실로 자동 입장을 시작합니다.")
            # return 하지 않고 아래로 내려가서 브라우저를 켭니다!

    # (이 아래부터 기존의 try: max_retry_val = int(retry_var.get()) ... 코드가 이어집니다)
        
    # 기존 진입 횟수 체크 시작
    try:
        max_retry_val = int(retry_var.get())
        wait_time_val = int(wait_var.get())
    except:
        max_retry_val = 3
        wait_time_val = 1
        
    retry_count = 0

    try:
        max_retry_val = int(retry_var.get())
        wait_time_val = int(wait_var.get())
    except:
        max_retry_val = 3
        wait_time_val = 1
        
    retry_count = 0
    
    while retry_count < max_retry_val and is_running:
        try:
            print(f"\n🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] 시도 {retry_count + 1}/{max_retry_val}: 자동 입장을 시작합니다!")
            
            if driver is not None:
                try: driver.quit()
                except: pass
                driver = None

            driver = get_browser_driver()
            if driver is None: raise Exception("브라우저 연결 실패")
            
            driver.maximize_window()
            time.sleep(1)
            if platform.system() == "Windows":
                try:
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3) 
                    print("✅ 창을 최상단으로 고정했습니다.")
                except: pass
            
            url = url_entry.get().strip()
            if not url: url = "https://yeardream2026.elice.io/my/lecturerooms?page=1"
            
            driver.get(url)
            
            try:
                login_wait = WebDriverWait(driver, 5) 
                login_button = login_wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., '로그인')]")))
                print("로그인 화면 감지됨! 자동완성 적용 대기 중...")
                time.sleep(3) 
                
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
            except:
                print("💡 로그인 버튼이 없습니다. 이미 로그인된 상태로 간주하고 진입합니다.")

            print("강의실 목록 로딩 대기 중...")
            list_wait = WebDriverWait(driver, 30)
            list_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '강의실')]")))
            close_annoying_popups(driver) 

            remaining_login_buttons = driver.find_elements(By.XPATH, "//button[contains(., '로그인')]")
            if remaining_login_buttons and remaining_login_buttons[0].is_displayed():
                print("❌ 로그인이 완료되지 않았습니다. 팝업을 띄웁니다.")
                show_login_warning()
                return 
            
            print("🛡️ 방해 팝업(나중에 하기) 탐색 중...")
            time.sleep(3) 
            try:
                bypass_btn = driver.find_element(By.XPATH, "//*[contains(text(), '나중에 하기')]")
                driver.execute_script("arguments[0].click();", bypass_btn)
                print("✅ '나중에 하기' 팝업을 치웠습니다!")
            except: pass

            # ====================================================================
            # 🔍 강의실 탐색 로직 (플랜 A -> 플랜 B)
            # ====================================================================
            print("✅ 강의실 탐색 시작 (플랜 A: 날짜 기반 검색).")
            today_date = get_today_date_str()
            wait = WebDriverWait(driver, 20)
            target_found = False
            
            try:
                elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{today_date}')]")))
                for elem in elements:
                    text = elem.text
                    if len(text) > 0 and len(text) < 100 and "강의실" in text:
                        print(f"🎯 [플랜 A 성공] 날짜 매칭 강의실 발견: {text}")
                        driver.execute_script("arguments[0].click();", elem)
                        target_found = True
                        break
            except: pass

            # 💡 [플랜 B 가동] 날짜로 못 찾았다면, 특강이라고 간주하고 인원수로 탐색!
            if not target_found:
                print("⚠️ 오늘 날짜 강의실이 없습니다. [플랜 B: 10명 이상 참여 방 탐색]을 시작합니다.")
                import re 
                try:
                    # 1. '명'이라는 글자가 들어간 <b> 태그를 찾고, 그 부모 요소(/..)를 통째로 낚아챔
                    participant_elements = driver.find_elements(By.XPATH, "//b[contains(text(), '명')]/..")
                    
                    for elem in participant_elements:
                        # 2. 껍데기 안에 있는 모든 글자를 하나로 합쳐서 가져옴 (예: "55명 참여")
                        text = elem.text.replace("\n", " ").strip() 
                        
                        if "참여" in text:
                            # 3. 정규식으로 숫자만 깔끔하게 발라냄
                            match = re.search(r'(\d+)\s*명\s*참여', text)
                            if match:
                                count = int(match.group(1))
                                if count >= 10: 
                                    print(f"🎯 [플랜 B 성공] 특강/활성화된 방 발견! (현재 인원: {count}명)")
                                    driver.execute_script("arguments[0].click();", elem)
                                    target_found = True
                                    break
                except Exception as e:
                    print(f"⚠️ 플랜 B 탐색 중 오류 발생: {e}")

            # 플랜 A와 플랜 B가 모두 실패했을 때만 진짜 에러를 내고 재시작 루프로 던짐
            if not target_found:
                raise Exception(f"⚠️ 정규 강의({today_date}) 및 활성화된 특강(10명 이상) 방을 모두 찾지 못했습니다.")
            # ====================================================================

            print("입장 버튼 클릭 대기 중...")
            time.sleep(2) 
            if not is_running: return 
            
            click_success = False
            try:
                elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{today_date}')]")))
                for elem in elements:
                    text = elem.text
                    if len(text) > 0 and len(text) < 100 and "강의실" in text:
                        print(f"🎯 [플랜 A 성공] 날짜 매칭 강의실 발견: {text}")
                        driver.execute_script("arguments[0].click();", elem)
                        target_found = True
                        break
            except: pass

            time.sleep(2) 

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
                                break 
                    except: pass
                    finally: driver.switch_to.default_content() 
                    if click_success: break 
                        
            if not click_success:
                 raise Exception("⚠️ 강의실 입장 버튼을 클릭하지 못했습니다.")

            # ====================================================================
            # 🎉 [안전 구역] 이후 발생하는 부가 기능(채팅창/출석) 에러는 무시합니다.
            # ====================================================================
            print("🎉 강의실 최종 입장 완료!")
            time.sleep(5) 
            close_annoying_popups(driver)

            # (이 아래부터 기존의 try: 채팅창 열기 및 QR 스캔 로직 이어짐...)

            try:
                print("💬 채팅창 열기 시도 중...")
                chat_clicked = False
                MY_XPATH = "//span[@aria-label='라이브 강의실 채팅']//button"
                
                try:
                    btn = driver.find_element(By.XPATH, MY_XPATH)
                    driver.execute_script("arguments[0].click();", btn)
                    chat_clicked = True
                    print("✅ 기본 화면에서 채팅창을 열었습니다.")
                except:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        try:
                            driver.switch_to.frame(iframe)
                            btn = driver.find_element(By.XPATH, MY_XPATH)
                            driver.execute_script("arguments[0].click();", btn)
                            chat_clicked = True
                            print("✅ iframe 내부에서 채팅창을 열었습니다.")
                        except: pass
                        finally: driver.switch_to.default_content() 
                        if chat_clicked: break
            except: print("⚠️ 채팅창을 열지 못했습니다. (무시하고 계속 진행)")

            # (위쪽 채팅창 열기 등 기존 코드...)

            
            # 👇 [새로 추가된 구역] 이미 출석이 되어있다면 여기서 멈추고 시청 모드로 전환!
            if is_already_done:
                print("🎉 이미 출석이 완료된 상태입니다. QR 스캔을 생략하고 편안한 시청을 위해 고정을 해제합니다!")
                if platform.system() == "Windows":
                    try:
                        hwnd = ctypes.windll.user32.GetForegroundWindow()
                        ctypes.windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 3)
                    except: pass
                break # 아래쪽 QR 로직을 무시하고 바로 대기 상태로 빠져나감
            
            
            original_window = driver.current_window_handle 
            expected_url = driver.current_url 
            
            try:
                found_url = scan_screen_for_qr(timeout_minutes=wait_time_val) 
                if found_url and is_running:
                    print("🌐 출석 링크를 새 탭으로 엽니다!")
                    driver.execute_script(f"window.open('{found_url}', '_blank');")
                    time.sleep(2) 
                    
                    for window_handle in driver.window_handles:
                        if window_handle != original_window:
                            driver.switch_to.window(window_handle)
                            break
                            
                    time.sleep(4) 
                    print("👀 출석 화면 오버레이(팝업) 1차 제거 시도 중...")
                    close_annoying_popups(driver) 
                    
                    try:
                        close_btns = driver.find_elements(By.XPATH, "//*[contains(text(), '닫기')]")
                        for btn in close_btns:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                                print("✅ 팝업 '닫기' 버튼 강제 타격 완료!")
                    except: pass

                    # =========================================================
                    # 🔍 [구형 로직 완벽 삭제 및 마이페이지 교차 검증 시작]
                    # =========================================================
                    time.sleep(3) # QR 인식이 서버에 반영될 여유 시간
                    
                    print("🔍 [마이페이지 교차 검증] 출석 도장이 시스템에 찍혔는지 확인합니다...")
                    driver.get("https://yeardream2026.elice.io/my")
                    time.sleep(4) 
                    
                    import re
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    
                    # 👇 [새로 추가된 핵심 구역] 봇을 속이는 가짜 안내 문구를 텍스트에서 강제로 날려버립니다.
                    page_text = re.sub(r'09:00\s*[Aa][Mm]\s*~\s*17:00\s*[Pp][Mm]', '', page_text, flags=re.IGNORECASE)
                    page_text = re.sub(r'09:00\s*~\s*17:00', '', page_text) # (AM/PM 글씨가 생략된 변형 대비)

                    check_hour = datetime.datetime.now().hour
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    # 오전 출석(09:xx AM) 확인
                    if check_hour < 12: 
                        if re.search(r'0?9:\d{2}', page_text): 
                            attendance_log[today_str]["morning"] = True
                            print("🎉 [오전 출석 최종 확인] 오전 출석 도장이 확인되었습니다!")
                            save_attendance_to_file()  # 🟢 [수정완료] 전용 저장 함수 호출
                            try: refresh_calendar_ui() 
                            except: pass
                        else:
                            print("⚠️ 마이페이지에 오전 출석 시간(09:xx)이 발견되지 않았습니다.")
                    
                    # 오후 퇴실(04:xx PM 또는 16:xx) 확인
                    else: 
                        if re.search(r'(16:\d{2}|0?4:\d{2}\s*[Pp][Mm]?)', page_text):
                            attendance_log[today_str]["afternoon"] = True
                            print("🎉 [오후 퇴실 최종 확인] 오후 퇴실 도장이 확인되었습니다!")
                            
                            # 👇 [새로 추가된 구역] 오전 기록이 DB에 비어있는데 화면엔 있다면 보정!
                            if not attendance_log[today_str].get("morning"):
                                if re.search(r'0?9:\d{2}', page_text):
                                    attendance_log[today_str]["morning"] = True
                                    print("💡 [자동 보정] 마이페이지에서 오전 출석 기록도 발견되어 달력에 함께 보정(체크)했습니다!")
                            # 👆 [추가 끝]

                            save_attendance_to_file() 
                            try: refresh_calendar_ui() 
                            except: pass
                        else:
                            print("⚠️ 마이페이지에 오후 퇴실 시간(16:xx 또는 4:xx PM)이 발견되지 않았습니다.")
                    print("✅ 교차 검증 완료. 이제 이 확인용 탭을 닫습니다.")
                    driver.close() # 새 탭 미련 없이 닫기
                    # =========================================================

            except Exception as e:
                print(f"⚠️ QR 출석 진행 중 오류 발생 (무시하고 화면 유지): {e}")
            
            finally:
                # [안전 구역] 찌꺼기 탭 정리 및 원래 강의실로 시점 복귀
                try:
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                    except: pass

                    for handle in driver.window_handles:
                        if handle != original_window:
                            driver.switch_to.window(handle)
                            driver.close() 
                    
                    driver.switch_to.window(original_window)
                    current_url = driver.current_url
                    base_expected = expected_url.split("?")[0]
                    base_current = current_url.split("?")[0]
                    
                    if base_expected in base_current or "elice.io" in base_current:
                        print("✅ 기존 강의실 화면 복귀 완료.")
                        if platform.system() == "Windows":
                            try:
                                hwnd = ctypes.windll.user32.GetForegroundWindow()
                                ctypes.windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 3)
                                print("🔓 창 최상단 고정을 해제합니다.")
                            except: pass
                    else:
                        print(f"⚠️ 강의실 이탈 감지됨 (현재 주소: {current_url}) - 화면 유지함")

                except Exception as e:
                    print(f"⚠️ 탭 복귀 중 에러 발생: {e} - 화면 유지함")

            # 스케줄러 장기 대기 방지 및 루프 종료
            print("🎉 출석/대기 사이클 완료! 봇 엔진은 다음 스케줄을 감시하기 위해 돌아갑니다.")
            time.sleep(10)
            break

        except Exception as e:
            retry_count += 1
            print(f"\n🚨 [오류 발생] 강의실 진입 실패! (실패 횟수: {retry_count}/{max_retry_val})")
            print(f"상세 원인: {e}")
            
            # 👇 [여기서부터 덮어쓰기] 블랙박스 안전 저장 코드로 교체
            try:
                if driver:
                    # 파일명에 콜론(:)만 안 들어가게 처리
                    safe_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 폴더가 없으면 에러가 나니 만들어주는 딱 두 줄만 유지
                    if not os.path.exists("errorLogs"):
                        os.makedirs("errorLogs")
                        
                    # 맨 앞에 / 없이 깔끔하게 상대 경로로 저장!
                    driver.save_screenshot(f"errorLogs/error_blackbox_{safe_now}.png")
                    print(f"📸 블랙박스 저장 완료: errorLogs/error_blackbox_{safe_now}.png")
            except Exception as pic_error: 
                print(f"⚠️ 블랙박스 캡처 중 오류 발생: {pic_error}")

            try:
                if driver: driver.quit()
                time.sleep(1)
                if platform.system() == "Windows":
                    os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
                    os.system("taskkill /f /im msedgedriver.exe /t >nul 2>&1")
                print("🧹 백그라운드 프로세스 청소 완료.")
            except: pass
            
            if retry_count < max_retry_val and is_running:
                print("🔄 5초 뒤 새 창을 열어 처음부터 다시 시도합니다...\n")
                time.sleep(5)
            else:
                print("💀 최대 재시도 횟수 초과 혹은 중지 요청으로 인해 봇을 대기 상태로 전환합니다.")
                break 


# =====================================================================
# [5] GUI 및 스케줄러 루프 제어
# =====================================================================
class PrintLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, message):
        self.text_widget.after(0, self._append, message)
    def _append(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END) 
    def flush(self): pass

def run_scheduler_loop():
    global is_running
    target_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    target_times = []
    for t_str, var in morning_vars.items():
        if var.get(): target_times.append(t_str)
    for t_str, var in afternoon_vars.items():
        if var.get(): target_times.append(t_str)
            
    if not target_times:
        print("\n⚠️ 선택된 예약 시간이 없습니다! 기본 모드로 1회만 진행합니다.")
    else:
        print("\n⏳ 선택된 예약 타이머 설정 중...")
        for day in target_days:
            for t in target_times:
                getattr(schedule.every(), day).at(t).do(run_bot)
                print(f" - [{day.capitalize()}] {t} 실행 예약 등록 완료")
                
    print("\n✅ 예약 시스템 준비 완료! 백그라운드 실시간 감시를 시작합니다.")
    
    if is_running:
        print("💡 [통합 기능] 현재 시점 기준으로 즉시 1회 검사를 진행합니다...")
        run_bot() 
    
    if is_running and target_times:
        print("\n⏳ 1회 즉시 검사가 종료되었습니다. 다음 예약 스케줄에 맞춰 대기합니다...")

    while is_running:
        schedule.run_pending()
        time.sleep(1) 
    print("🛑 스케줄러 대기 상태가 종료되었습니다.")

def create_gui():
    global url_entry, morning_vars, afternoon_vars, retry_var, wait_var
    
    root = tk.Tk()
    root.title("엘리스 통합 자동 출석 매니저")
    root.geometry("640x750") 
    root.configure(bg="#f4f4f4")
    
    config_file = os.path.join(current_folder, "bot_config.json")
    
    def load_config():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "url": "https://yeardream2026.elice.io/my/lecturerooms?page=1",
                "morning": ["09:05", "09:10"],
                "afternoon": ["16:25", "16:30"],
                "close_browser": True,
                "retry_count": "3",
                "wait_time": "1",
                "attendance_log": {} # 👈 [핵심] 불러올 때 빈 달력 데이터 기본값 생성
            }
            
    def save_config():
        global attendance_log # 👈 [핵심] 전역 변수 데이터를 확실하게 가져옴
        saved_data = {
            "url": url_entry.get().strip(),
            "morning": [t for t, var in morning_vars.items() if var.get()],
            "afternoon": [t for t, var in afternoon_vars.items() if var.get()],
            "close_browser": close_browser_var.get(),
            "retry_count": retry_var.get(),
            "wait_time": wait_var.get(),
            "attendance_log": attendance_log # 👈 [핵심] 파일에 출석 로그를 영구 저장함
        }
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(saved_data, f, ensure_ascii=False, indent=4)
        except Exception as e: 
            print(f"⚠️ 설정 저장 실패: {e}")

    saved_config = load_config()
    close_browser_var = tk.BooleanVar(value=saved_config.get("close_browser", True)) 
    
    title_lbl = tk.Label(root, text="🚀 엘리스 LXP 통합 출석 자동화 시스템", font=("Helvetica", 14, "bold"), bg="#f4f4f4")
    title_lbl.pack(pady=10)
    
    setting_frame = tk.Frame(root, bg="#f4f4f4")
    setting_frame.pack(padx=20, pady=5, fill=tk.X)
    
    retry_var = tk.StringVar(value=saved_config.get("retry_count", "3"))
    wait_var = tk.StringVar(value=saved_config.get("wait_time", "1"))
    
    tk.Label(setting_frame, text="🔄 에러 시 재시도 횟수:", bg="#f4f4f4", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT)
    tk.Entry(setting_frame, textvariable=retry_var, width=5, justify="center").pack(side=tk.LEFT, padx=5)
    
    tk.Label(setting_frame, text="⏳ 초기 로딩/QR 대기 시간 (분):", bg="#f4f4f4", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(15,0))
    tk.Entry(setting_frame, textvariable=wait_var, width=5, justify="center").pack(side=tk.LEFT, padx=5)

    url_frame = tk.LabelFrame(root, text="🌐 엘리스 강의실 대시보드 URL 주소 설정", font=("Helvetica", 9, "bold"), bg="#f4f4f4", padx=10, pady=5)
    url_frame.pack(padx=20, pady=5, fill=tk.X)
    
    url_entry = tk.Entry(url_frame, font=("Consolas", 10))
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
    active_afternoon = saved_config.get("afternoon", ["16:25", "16:30"])
    for idx, slot in enumerate(afternoon_slots):
        is_chk = slot in active_afternoon
        afternoon_vars[slot] = tk.BooleanVar(value=is_chk)
        cb = tk.Checkbutton(a_chk_frame1, text=slot.split(":")[1]+"분" if "16" in slot else "17:00", variable=afternoon_vars[slot], bg="#f4f4f4", font=("Helvetica", 9))
        cb.pack(side=tk.LEFT, padx=3)

    def start_integrated_mode():
        global is_running
        is_running = True
        save_config() 
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
            try: driver.quit()
            except: pass
            driver = None
            print("✅ 봇 중지 및 브라우저 종료 완료.")
        else:
            print("✅ 봇 엔진만 정지되었습니다. (강의 시청 유지)")

        btn_start.config(state=tk.NORMAL, text="▶️ 통합 자동 출석 가동 시작")
        btn_stop.config(state=tk.DISABLED)
        url_entry.config(state=tk.NORMAL)

    # =====================================================================
    # 🎨 [UI 변경] 하단 조작부 좌/우 분할 및 미니 달력 레이아웃
    # =====================================================================
    ctrl_frame = tk.Frame(root, bg="#f4f4f4")
    ctrl_frame.pack(padx=20, pady=5, fill=tk.X)

    # [좌측] 가동/중지 버튼 및 설정 구역
    left_ctrl = tk.Frame(ctrl_frame, bg="#f4f4f4")
    left_ctrl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    btn_start = tk.Button(left_ctrl, text="▶️ 통합 자동 출석 가동 시작", font=("Helvetica", 11, "bold"), 
                     height=2, command=start_integrated_mode, bg="#4CAF50", fg="black")
    btn_start.pack(fill=tk.X, pady=3)
    
    btn_stop = tk.Button(left_ctrl, text="⏹️ 작동 중지 및 초기화", font=("Helvetica", 11, "bold"), 
                         height=2, command=stop_bot, fg="red", state=tk.DISABLED)
    btn_stop.pack(fill=tk.X, pady=3)

    chk_close = tk.Checkbutton(left_ctrl, text="프로그램 중지/종료 시 브라우저 같이 닫기", 
                               variable=close_browser_var, bg="#f4f4f4", font=("Helvetica", 9))
    chk_close.pack(anchor=tk.W, pady=2)

    # [우측] 이번 달 출석 현황 미니 달력 구역
    right_ctrl = tk.Frame(ctrl_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=5, pady=5)
    right_ctrl.pack(side=tk.RIGHT)

    # 👇 [여기서부터 덮어쓰기 시작] 달력 이동을 위한 현재 뷰(View) 변수
    global view_year, view_month
    view_year = datetime.datetime.now().year
    view_month = datetime.datetime.now().month

    def change_month(delta):
        global view_year, view_month
        view_month += delta
        if view_month > 12:
            view_month = 1
            view_year += 1
        elif view_month < 1:
            view_month = 12
            view_year -= 1
        draw_calendar()

    def draw_calendar():
        global attendance_log, view_year, view_month
        for widget in right_ctrl.winfo_children():
            widget.destroy()

        # 📅 [수정됨] 상단 월 이동 네비게이션 (◀ ▶)
        nav_frame = tk.Frame(right_ctrl, bg="#ffffff")
        nav_frame.pack(pady=(0,3), fill=tk.X)
        tk.Button(nav_frame, text="◀", command=lambda: change_month(-1), bd=0, bg="#ffffff", cursor="hand2").pack(side=tk.LEFT)
        tk.Label(nav_frame, text=f"{view_year}년 {view_month}월", font=("Helvetica", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, expand=True)
        tk.Button(nav_frame, text="▶", command=lambda: change_month(1), bd=0, bg="#ffffff", cursor="hand2").pack(side=tk.RIGHT)

        cal_grid = tk.Frame(right_ctrl, bg="#ffffff")
        cal_grid.pack()

        days_header = ["일", "월", "화", "수", "목", "금", "토"]
        for i, d in enumerate(days_header):
            tk.Label(cal_grid, text=d, font=("Helvetica", 7), bg="#ffffff", fg="#555").grid(row=0, column=i)

        calendar.setfirstweekday(calendar.SUNDAY)
        month_days = calendar.monthcalendar(view_year, view_month)

        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                date_str = f"{view_year}-{view_month:02d}-{day:02d}"
                log = attendance_log.get(date_str, {"morning": False, "afternoon": False})
                
                cell = tk.Frame(cal_grid, bg="#ffffff")
                cell.grid(row=r+1, column=c, padx=1, pady=1)

                fg_color = "red" if c == 0 else "black"
                tk.Label(cell, text=str(day), font=("Helvetica", 7, "bold"), bg="#ffffff", fg=fg_color, width=2).pack(side=tk.LEFT)

                # 🖱️ [수정됨] 마우스 클릭을 쉽게 하기 위해 폭을 8px로 넓힘
                canvas = tk.Canvas(cell, width=8, height=12, bg="#ffffff", highlightthickness=0, cursor="hand2")
                canvas.pack(side=tk.LEFT, padx=(0, 2))

                m_color = "#4CAF50" if log.get("morning") else "#e0e0e0"   
                a_color = "#2196F3" if log.get("afternoon") else "#e0e0e0" 

                canvas.create_rectangle(0, 0, 8, 5, fill=m_color, outline="")   
                canvas.create_rectangle(0, 7, 8, 12, fill=a_color, outline="")  

                # ✍️ [수정됨] 마우스 클릭 시 DB 값을 뒤집고 자동 저장(토글 기능)
                # ✍️ [수정됨] 마우스 클릭 시 확인 팝업을 먼저 띄움
                def toggle_status(event, d_str=date_str):
                    # 클릭한 곳이 위쪽(오전)인지 아래쪽(오후)인지 판별
                    is_morning = event.y < 6
                    part_name = "오전(출석)" if is_morning else "오후(퇴실)"
                    
                    # 🚨 [새로 추가됨] 실수 방지용 예/아니오 팝업창
                    confirm = messagebox.askyesno(
                        "출석 기록 수동 수정", 
                        f"[{d_str}] 날짜의 '{part_name}' 기록 상태를 반대로 변경하시겠습니까?"
                    )
                    
                    if confirm: # '예'를 눌렀을 때만 작동
                        if d_str not in attendance_log:
                            attendance_log[d_str] = {"morning": False, "afternoon": False}
                        
                        if is_morning: 
                            attendance_log[d_str]["morning"] = not attendance_log[d_str]["morning"]
                        else:          
                            attendance_log[d_str]["afternoon"] = not attendance_log[d_str]["afternoon"]
                            
                        save_attendance_to_file() # DB 파일에 즉시 기록
                        draw_calendar()           # 화면 새로고침
                # 좌클릭 이벤트 바인딩
                canvas.bind("<Button-1>", toggle_status)

    # (이 아래쪽 코드는 기존과 동일합니다)
    global attendance_log
    attendance_log = saved_config.get("attendance_log", {})
    draw_calendar()
    
    # 봇이 출석을 성공했을 때 외부(쓰레드)에서 달력을 새로고침 할 수 있도록 함수를 전역으로 빼줍니다.
    global refresh_calendar_ui
    refresh_calendar_ui = lambda: root.after(0, draw_calendar)

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

    def on_closing():
        global is_running, driver
        is_running = False
        save_config() 
        if close_browser_var.get() and driver is not None:
            try: driver.quit()
            except: pass
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    create_gui()