import os
import sys
import subprocess
import importlib
import datetime
import time 
import tkinter as tk
from tkinter import messagebox
import platform 
import logging
import warnings
import threading 

# --- 터미널을 깨끗하게 유지하기 위한 설정 ---
logging.getLogger().setLevel(logging.ERROR) 
warnings.filterwarnings("ignore") 

# --- 봇 제어용 전역 변수 (신호등 역할) ---
is_running = False 
# ----------------------------------------------------

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
        print("   - pip 설치 도구 최신화 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    except Exception:
        pass 

    try:
        print("   - 패키 일괄 설치 진행 중... (시간이 조금 걸릴 수 있습니다)")
        install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 모든 패키지 일괄 설치 완료!")
        else:
            print("\n⚠️ 기본 설치에 실패했습니다. (권한 문제일 수 있어 사용자 모드로 재시도합니다)")
            user_install_cmd = [sys.executable, "-m", "pip", "install", "--user"] + missing_packages
            result_user = subprocess.run(user_install_cmd, capture_output=True, text=True)
            
            if result_user.returncode == 0:
                print("✅ 사용자 권한(--user) 일괄 설치 완료!")
            else:
                print("\n⚠️ 시스템 보호 정책(uv/PEP 668) 차단 감지. 'uv' 전용 우회를 시도합니다...")
                uv_success = False
                try:
                    result_uv = subprocess.run(["uv", "pip", "install", "--system"] + missing_packages, capture_output=True, text=True)
                    if result_uv.returncode == 0:
                        print("✅ uv 환경 전용 명령어(--system)로 강제 설치 완료!")
                        uv_success = True
                except Exception:
                    pass 
                
                if not uv_success:
                    print("\n⚠️ 최후의 수단(break-system-packages)으로 우회를 시도합니다...")
                    force_install_cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", "--user"] + missing_packages
                    result_force = subprocess.run(force_install_cmd, capture_output=True, text=True)
                    
                    if result_force.returncode == 0:
                        print("✅ 보호 정책 우회 및 강제 일괄 설치 완료!")
                    else:
                        print("\n❌ 최종 설치 실패! 아래의 진짜 에러 원인을 확인해주세요:")
                        print("="*50)
                        print(result_force.stderr) 
                        print("="*50)
                        print("💡 힌트: C++ 빌드 도구가 없거나, 파이썬 가상환경(venv)을 직접 만들어야 할 수 있습니다.")
                        sys.exit(1)
                
    except Exception as e:
        print(f"❌ 설치 프로세스 작동 중 치명적 에러 발생: {e}")
        sys.exit(1)

def setup_mac_env():
    if platform.system() == "Darwin":
        print("🍎 Mac 환경 감지됨: QR 해독용 zbar 엔진 자동 설치를 점검합니다...")
        try:
            subprocess.run(["brew", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["brew", "install", "zbar"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ [Mac] zbar 엔진 설치/확인 완료!")
        except Exception:
            pass

check_and_install_packages()
setup_mac_env() 
print("✅ 모든 환경 준비 완료!\n")

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
import webbrowser

QR_AVAILABLE = True
try:
    from pyzbar.pyzbar import decode
except Exception as e:
    QR_AVAILABLE = False
    print(f"\n⚠️ [경고] QR 스캐너 모듈 고장! (실제 에러 원인: {e})")
    
    if platform.system() == "Windows":
        def ask_cpp_install():
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            result = messagebox.askyesno(
                "QR 스캐너 복구 (2013년도 구형 C++ 필요)",
                f"QR 엔진이 작동을 멈췄습니다.\n[실제 에러 내용: {e}]\n\n"
                "최신 C++을 깔아도 이 창이 뜬다면, pyzbar 모듈의 고질적인 문제인\n"
                "'2013년도 구형 C++ 뼈대(vcredist 2013)'가 없기 때문입니다.\n\n"
                "마이크로소프트 2013년도 공식 설치 파일을 다운로드하시겠습니까?"
            )
            root.destroy()
            return result
            
        if ask_cpp_install():
            print("🌐 브라우저를 열어 2013년도 버전 공식 C++ 설치 파일을 다운로드합니다...")
            webbrowser.open("https://aka.ms/highdpimfc2013x64enu")
            print("💡 안내: 다운로드된 파일을 설치하신 후, PC를 한 번만 더 재부팅해주세요!")
            time.sleep(3)
            sys.exit(0) 
        else:
            print("❌ 다운로드를 건너뛰셨습니다. QR 기능을 끈 채로 강의실 자동 입장만 진행합니다.")
    else:
        print(f"   강의실 자동 입장은 정상적으로 진행되지만, QR 자동 출석은 작동하지 않습니다.")

current_folder = os.getcwd()
driver = None

def get_browser_driver():
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,    
        "profile.default_content_setting_values.media_stream_camera": 2, 
        "profile.default_content_setting_values.geolocation": 2          
    }

    try:
        print("🌐 크롬(Chrome) 브라우저 연결 시도 중...")
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
    messagebox.showwarning(
        "수동 로그인 필요", 
        "자동 로그인이 실패했거나 봇 프로필이 초기화되었습니다.\n\n"
        "열려있는 브라우저 창에서 '수동으로 로그인'을 완료(비밀번호 저장 필수)한 후, 매크로를 다시 실행해 주세요!"
    )
    root.destroy()

def get_today_str():
    now = datetime.datetime.now()
    weekdays = ["(월)", "(화)", "(수)", "(목)", "(금)", "(토)", "(일)"]
    return f"{now.month}/{now.day}{weekdays[now.weekday()]}"

def close_annoying_popups(driver):
    try:
        popup_texts = ["오늘 그만 보기", "오늘 하루 보지 않기", "다시 보지 않기", "닫기", "오늘 하루 열지 않음"]
        for text in popup_texts:
            btns = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            for btn in btns:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"🛡️ 방해 팝업 치움: '{text}' 버튼 클릭")
                    time.sleep(0.5)
    except Exception:
        pass

def scan_screen_for_qr(timeout_minutes=30):
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
            print(f"⏰ {timeout_minutes}분이 경과하여 QR 감시를 자동으로 종료합니다. (수업에 집중하세요!)")
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
        
    print("🛑 QR 감시가 강제로 중지되었습니다.")
    return None

def run_bot():
    global driver, is_running
    
    if not is_running: 
        return
        
    print(f"\n🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] 자동 입장을 시작/확인 합니다!")
    
    if driver is not None:
        print("🧹 크롬 프로필 충돌(빈 화면 현상) 방지를 위해 기존 창을 완전히 닫고 새 창을 준비합니다.")
        try:
            driver.quit()
        except Exception:
            pass
        driver = None

    driver = get_browser_driver()
    if driver is None:
        return 
    
    url = "https://yeardream2026.elice.io/my/lecturerooms?page=1"
    
    try:
        driver.get(url)
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
        
        print("로그인 처리 중! '라이브 강의실' 목록이 로딩될 때까지 스마트하게 기다립니다...")
        list_wait = WebDriverWait(driver, 30)
        list_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '라이브 강의실')]")))
        print("✅ 강의실 목록 로딩 완벽 확인!")
        
        close_annoying_popups(driver)
        
    except Exception:
        if is_running:
            print("로그인 화면이 감지되지 않았습니다. (진행)")

    if not is_running: return 

    remaining_login_buttons = driver.find_elements(By.XPATH, "//button[contains(., '로그인')]")
    if remaining_login_buttons and remaining_login_buttons[0].is_displayed():
        print("❌ 로그인이 완료되지 않았습니다. 팝업을 띄웁니다.")
        show_login_warning()
        return 
    
    print("✅ 로그인 확인됨. 강의실 탐색 시작.")
    today_text = get_today_str()
    print(f"오늘 날짜 타겟: {today_text}")

    try:
        wait = WebDriverWait(driver, 20)
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{today_text}')]")))

        target_found = False
        for elem in elements:
            try:
                text = elem.text
                if len(text) > 0 and len(text) < 50 and "강의실" in text:
                    print(f"강의실 발견: {text}")
                    driver.execute_script("arguments[0].click();", elem)
                    target_found = True
                    break
            except Exception:
                continue
        
        if not target_found:
            print("⚠️ 현재 열려있는 '오늘 날짜의 강의실'을 찾지 못했습니다.")
            print("👉 (아직 수업 전이거나 수업이 끝났습니다. 창을 유지하며 타이머 모드로 진입합니다.)")
            return 

        print("오버랩 팝업 및 입장 버튼 대기 중...")
        time.sleep(5) 
        
        if not is_running: return 
        
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
                    
        if click_success:
            print("🎉 강의실 입장 버튼 클릭 완료! 페이지 로딩을 기다립니다...")
            time.sleep(5) 

            close_annoying_popups(driver)

            found_url = scan_screen_for_qr()
            if found_url and is_running:
                print("🌐 출석 링크를 새 탭으로 엽니다!")
                
                original_window = driver.current_window_handle 
                driver.execute_script(f"window.open('{found_url}', '_blank');")
                
                time.sleep(2) # 새 탭이 열릴 시간을 조금 더 넉넉히 줍니다.
                
                # 시선을 새로 열린 출석 탭으로 이동
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                        
                print("👀 출석 화면을 덮는 iframe 오버레이 대기 중...")
                time.sleep(4) 
                
                # --- [핵심 수정] 새 탭(출석)에서 '입장하기'가 아닌 '닫기'를 누르도록 변경 및 iframe 탐색 추가 ---
                closed_overlay = False
                
                # 1. 기본 화면에서 '닫기' 버튼 탐색
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
                
                # 2. 기본 화면에 없다면 iframe(액자) 내부로 침투하여 '닫기' 탐색
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
                                driver.switch_to.default_content() # 원래 화면으로 복귀
                            
                            if closed_overlay:
                                break
                    except Exception:
                        driver.switch_to.default_content()

                if not closed_overlay:
                    print("⚠️ '닫기' 버튼을 찾지 못했습니다. (팝업이 없거나 이미 치워짐)")
                # ------------------------------------------------------------------------------------------
                
        else:
            print("입장 버튼 클릭 실패.")

    except Exception as e:
        if is_running:
            print(f"작동 중 에러 발생: {e}")

# ==============================================================================
# --- 터미널 글씨를 GUI 창으로 가로채는 클래스 ---
class PrintLogger:
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
    global is_running
    target_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    target_times = ["09:05", "09:10", "16:25", "16:30"]
    
    print("\n⏳ 내장 타이머 설정 중...")
    
    if "everyday" in target_days:
        for t in target_times:
            schedule.every().day.at(t).do(run_bot)
            print(f" - [매일] {t}에 실행 예약 완료")
    else:
        for day in target_days:
            for t in target_times:
                getattr(schedule.every(), day).at(t).do(run_bot)
                print(f" - [{day.capitalize()}] {t}에 실행 예약 완료")
                
    print("\n✅ 예약 타이머 설정 완료! 백그라운드 감시를 시작합니다.")
    print("💡 [통합 기능] 현재 시점으로 접속 가능한 강의가 있는지 즉시 1회 검사를 진행합니다...")
    
    if is_running:
        run_bot()
    
    if is_running:
        print("\n⏳ 1회 검사가 종료되었습니다. 예약된 다음 강의 시간을 기다리는 중입니다... (창을 최소화해 두세요)")

    while is_running:
        schedule.run_pending()
        time.sleep(1) 
    print("🛑 스케줄러 대기 상태가 종료되었습니다.")

def create_gui():
    root = tk.Tk()
    root.title("엘리스 자동 출석 비서")
    root.geometry("600x500") 
    root.configure(bg="#f4f4f4")
    
    title_lbl = tk.Label(root, text="🚀 엘리스 LXP 출석 자동화 봇", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
    title_lbl.pack(pady=15)
    
    def start_integrated_mode():
        global is_running
        is_running = True
        btn_start.config(state=tk.DISABLED, text="감시 및 타이머 작동 중...")
        btn_stop.config(state=tk.NORMAL) 
        threading.Thread(target=run_scheduler_loop, daemon=True).start()

    def stop_bot():
        global is_running, driver
        print("\n🛑 강제 중지 명령을 실행합니다... 잠시만 대기해주세요.")
        
        is_running = False
        schedule.clear()
        
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
            driver = None

        btn_start.config(state=tk.NORMAL, text="▶️ 통합 자동 시작 (즉시 1회 실행 + 예약 타이머)")
        btn_stop.config(state=tk.DISABLED)
        print("✅ 봇이 완전히 중지되고 초기화되었습니다. 상단 버튼을 눌러 다시 시작할 수 정 있습니다.\n")

    frame = tk.Frame(root, bg="#f4f4f4")
    frame.pack(pady=5)

    btn_start = tk.Button(frame, text="▶️ 통합 자동 시작 (즉시 1회 실행 + 예약 타이머)", font=("Helvetica", 11, "bold"), 
                     width=40, height=2, command=start_integrated_mode, bg="#4CAF50", fg="black")
    btn_start.pack(pady=5)
    tk.Label(frame, text="클릭 시 현재 강의실을 찾아 즉시 입장하며, 이후 정해진 시간에 알아서 작동합니다.", 
             bg="#f4f4f4", fg="#666666", font=("Helvetica", 9)).pack()
    
    btn_stop = tk.Button(frame, text="⏹️ 작동 중지 및 초기화", font=("Helvetica", 11, "bold"), 
                         width=40, height=2, command=stop_bot, fg="red", state=tk.DISABLED)
    btn_stop.pack(pady=15)

    log_frame = tk.Frame(root)
    log_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, bg="black", fg="#00ff00", font=("Consolas", 9), 
                       yscrollcommand=scrollbar.set, state=tk.NORMAL)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=log_text.yview)

    sys.stdout = PrintLogger(log_text)
    sys.stderr = PrintLogger(log_text)

    print("환영합니다! 필수 환경 로딩이 끝났습니다.")
    print("원하시는 모드의 버튼을 클릭해주세요.")

    root.mainloop()

if __name__ == "__main__":
    create_gui()