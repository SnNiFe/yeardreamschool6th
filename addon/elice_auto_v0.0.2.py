import os
import sys
import subprocess
import importlib
import datetime
import time 
import tkinter as tk
from tkinter import messagebox
import platform 

def check_and_install_packages():
    """파이썬 외부 라이브러리 스마트 자동 설치 (일괄 설치 및 에러 추적)"""
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
        print("   - 패키지 일괄 설치 진행 중... (시간이 조금 걸릴 수 있습니다)")
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

# --- [핵심 수정] QR 엔진(pyzbar) 로드 실패 시 무시하고 넘어가도록 예외 처리 ---
QR_AVAILABLE = True
try:
    from pyzbar.pyzbar import decode
except Exception as e:
    # dll 로드 실패 시 뻗지 않고 변수만 False로 변경
    QR_AVAILABLE = False
    print(f"\n⚠️ [경고] 컴퓨터에 C++ 기본 라이브러리가 부족하여 QR 스캐너 모듈이 고장났습니다.")
    print(f"   강의실 자동 입장은 정상적으로 진행되지만, QR 자동 출석은 작동하지 않습니다.")
# -------------------------------------------------------------------------

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
        c_options.add_experimental_option("prefs", prefs)
        chrome_profile = os.path.join(current_folder, "bot_profile_chrome")
        c_options.add_argument(f"user-data-dir={chrome_profile}")
        
        d = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=c_options)
        print("✅ 크롬 연결 성공!")
        return d
    except Exception:
        print("⚠️ 크롬 연결 실패. 엣지(Edge)로 전환합니다...")

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

def scan_screen_for_qr():
    # --- [수정] QR 엔진이 고장난 상태면 튕기지 않고 바로 함수 종료 ---
    if not QR_AVAILABLE:
        print("\n❌ QR 감시 모듈이 비활성화 되어있습니다.")
        print("💡 팁: 나중에 이 컴퓨터에서 QR 기능을 살리려면 인터넷에서 'Visual C++ 재배포 가능 패키지(x64)'를 다운받아 설치하세요.")
        return None
    # -------------------------------------------------------------

    print("👀 [QR 감시 모드] 화면에서 QR 코드를 찾는 중... (종료하려면 터미널에서 Ctrl+C)")
    while True:
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

def run_bot():
    global driver
    print(f"\n🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] 예약된 자동 입장을 시작합니다!")
    
    if driver is None:
        driver = get_browser_driver()
        if driver is None:
            return 
    
    url = "https://yeardream2026.elice.io/my/lecturerooms?page=1"
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
        time.sleep(5) 
        
    except Exception:
        print("로그인 화면이 감지되지 않았습니다. (진행)")

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
            print("오늘 날짜의 강의실을 찾지 못했습니다.")
            return

        print("오버랩 팝업 및 입장 버튼 대기 중...")
        time.sleep(5) 
        
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
            print("🎉 강의실 입장 완료!")
            found_url = scan_screen_for_qr()
            if found_url:
                print("🌐 출석 링크를 새 탭으로 엽니다!")
                driver.execute_script(f"window.open('{found_url}', '_blank');")
        else:
            print("입장 버튼 클릭 실패.")

    except Exception as e:
        print(f"작동 중 에러 발생: {e}")

if __name__ == "__main__":
    print("=====================================")
    print("1: 지금 바로 매크로 실행하기 (테스트용)")
    print("2: 내장 타이머(스케줄러) 켜두기")
    print("=====================================")
    choice = input("원하는 모드의 번호를 입력하세요: ")
    
    if choice == '1':
        run_bot()
    elif choice == '2':
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
        
        print("\n창을 닫지 말고 백그라운드에 최소화하여 켜두세요. (종료: 터미널에서 Ctrl+C)")
        
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")