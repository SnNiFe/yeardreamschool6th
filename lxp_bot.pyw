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

# --- 터미널을 깨끗하게 유지하기 위한 설정 ---
logging.getLogger().setLevel(logging.ERROR) 
warnings.filterwarnings("ignore") 

# --- 봇 제어용 전역 변수 (신호등 역할) ---
is_running = False 
driver = None

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
import webbrowser

QR_AVAILABLE = True
try:
    from pyzbar.pyzbar import decode
except Exception:
    QR_AVAILABLE = False

current_folder = os.getcwd()

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
            print('') 
    except Exception:
        pass

def show_login_warning():
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 
    messagebox.showwarning(
        "수동 로그인 필요", 
        "자동 로그인이 실패했거나 봇 프로필이 초기화되었습니다.\n\n"
        "열려있는 브라우저 창에서 '수동으로 로그인'을 완료한 후, 매크로를 다시 실행해 주세요!"
    )
    root.destroy()

# --- [유연한 날짜 매칭 지원] 월/일 문자열만 추출 ---
def get_today_date_str():
    now = datetime.datetime.now()
    return f"{now.month}/{now.day}"

def close_annoying_popups(driver):
    try:
        popup_texts = ["오늘 그만 보기", "오늘 하루 보지 않기", "다시 보지 않기", "닫기", "오늘 하루 열지 않음"]
        for text in popup_texts:
            btns = driver.find_elements(By.開PATH, f"//*[contains(text(), '{text}')]")
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

def run_bot():
    global driver, is_running
    if not is_running: 
        return
        
    print(f"\n🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] 자동 입장을 시작/확인 합니다!")
    
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
    
    # GUI 상에서 설정한 URL 읽어오기
    url = url_entry.get().strip()
    if not url:
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
        list_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '강의실')]")))
        print("✅ 강의실 목록 로딩 완벽 확인!")
        
        close_annoying_popups(driver)
    except Exception:
        if is_running:
            print("로그인 화면이 감지되지 않았습니다. (세션 유지 상태로 진행)")

    if not is_running: return 

    remaining_login_buttons = driver.find_elements(By.XPATH, "//button[contains(., '로그인')]")
    if remaining_login_buttons and remaining_login_buttons[0].is_displayed():
        print("❌ 로그인이 완료되지 않았습니다. 팝업을 띄웁니다.")
        show_login_warning()
        return 
    
    print("✅ 로그인 확인됨. 강의실 탐색 시작.")
    today_date = get_today_date_str()
    print(f"오늘 날짜 타겟 접두사: {today_date}")

    try:
        wait = WebDriverWait(driver, 20)
        # --- [핵심 수정] 날짜 텍스트가 포함된 모든 요소를 수집 ---
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{today_date}')]")))

        target_found = False
        for elem in elements:
            try:
                text = elem.text
                # --- [핵심 수정] 텍스트 안에 오늘 날짜와 '강의실' 키워드가 둘 다 존재하면 매칭 (사이에 공백, 요일, 라이브 등 무엇이 오든 호환) ---
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
                time.sleep(2) 
                
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                        
                print("👀 출석 화면을 덮는 iframe 오버레이 대기 중...")
                time.sleep(4) 
                
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
        else:
            print("입장 버튼 클릭 실패.")
    except Exception as e:
        if is_running:
            print(f"작동 중 에러 발생: {e}")

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
    
    # --- [핵심 수정] GUI에서 체크박스로 활성화된 시간대만 수집하여 스케줄러 등록 ---
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
        run_bot()
    
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
    
    close_browser_var = tk.BooleanVar(value=True) 
    
    title_lbl = tk.Label(root, text="🚀 엘리스 LXP 통합 출석 자동화 시스템", font=("Helvetica", 14, "bold"), bg="#f4f4f4")
    title_lbl.pack(pady=10)
    
    # --- [신규 UI] 입장 주소(URL) 커스텀 입력 칸 배치 ---
    url_frame = tk.LabelFrame(root, text="🌐 엘리스 강의실 대시보드 URL 주소 설정", font=("Helvetica", 9, "bold"), bg="#f4f4f4", padx=10, pady=5)
    url_frame.pack(padx=20, pady=5, fill=tk.X)
    
    url_entry = tk.Entry(url_frame, font=("Consolas", 10))
    url_entry.insert(0, "https://yeardream2026.elice.io/my/lecturerooms?page=1")
    url_entry.pack(fill=tk.X, expand=True, pady=2)
    
    # --- [신규 UI] 오전/오후 5분 간격 타이머 선택 매트릭스 ---
    time_frame = tk.LabelFrame(root, text="⏰ 타이머 실행 시간 선택 (5분 간격)", font=("Helvetica", 9, "bold"), bg="#f4f4f4", padx=10, pady=5)
    time_frame.pack(padx=20, pady=5, fill=tk.X)
    
    # 오전 시간대 레이아웃 (09:00 ~ 09:30)
    m_lbl = tk.Label(time_frame, text="오전 타겟 (09:00 ~ 09:30):", font=("Helvetica", 9, "bold"), bg="#f4f4f4")
    m_lbl.pack(anchor=tk.W, pady=2)
    
    m_chk_frame = tk.Frame(time_frame, bg="#f4f4f4")
    m_chk_frame.pack(fill=tk.X, anchor=tk.W)
    
    morning_slots = ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30"]
    morning_vars = {}
    default_active = ["09:05", "09:10", "16:25", "16:30"]
    
    for slot in morning_slots:
        is_chk = slot in default_active
        morning_vars[slot] = tk.BooleanVar(value=is_chk)
        cb = tk.Checkbutton(m_chk_frame, text=slot.split(":")[1]+"분", variable=morning_vars[slot], bg="#f4f4f4", font=("Helvetica", 9))
        cb.pack(side=tk.LEFT, padx=4)
        
    # 오후 시간대 레이아웃 (16:20 ~ 17:00)
    a_lbl = tk.Label(time_frame, text="오후 타겟 (16:20 ~ 17:00):", font=("Helvetica", 9, "bold"), bg="#f4f4f4")
    a_lbl.pack(anchor=tk.W, pady=2)
    
    a_chk_frame1 = tk.Frame(time_frame, bg="#f4f4f4")
    a_chk_frame1.pack(fill=tk.X, anchor=tk.W)
    
    afternoon_slots = ["16:20", "16:25", "16:30", "16:35", "16:40", "16:45", "16:50", "16:55", "17:00"]
    afternoon_vars = {}
    
    for idx, slot in enumerate(afternoon_slots):
        is_chk = slot in default_active
        afternoon_vars[slot] = tk.BooleanVar(value=is_chk)
        # 가독성을 위해 줄나눔 처리 가능하게 배치
        target_parent = a_chk_frame1
        cb = tk.Checkbutton(target_parent, text=slot.split(":")[1]+"분" if "16" in slot else "17:00", variable=afternoon_vars[slot], bg="#f4f4f4", font=("Helvetica", 9))
        cb.pack(side=tk.LEFT, padx=3)

    def start_integrated_mode():
        global is_running
        is_running = True
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

    print("환영합니다! 시스템 핵심 환경 구성이 모두 완벽히 정렬되었습니다.")
    print("주소와 타이머 시간(5분 간격 체크박스)을 조율하신 후 상단 가동 버튼을 눌러주세요.")

    def on_closing():
        global is_running, driver
        is_running = False
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
