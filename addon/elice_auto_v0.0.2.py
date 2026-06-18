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
    
    # 1. 설치가 안 된 패키지만 골라내기
    for pip_name, module_name in packages.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(pip_name)
            
    if not missing_packages:
        return # 다 있으면 바로 통과
        
    print(f"⚙️ 부족한 패키지를 설치합니다: {', '.join(missing_packages)}")
    
    # 2. 설치 도구(pip) 자체를 최신으로 업데이트 (구버전 에러 방지)
    try:
        print("   - pip 설치 도구 최신화 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    except Exception:
        pass # 실패해도 메인 설치로 넘어감

    # 3. 누락된 패키지들을 한 번에 묶어서 일괄 설치 (의존성 충돌 해결)
    try:
        print("   - 패키지 일괄 설치 진행 중... (시간이 조금 걸릴 수 있습니다)")
        # 설치 명령어 조합
        install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        
        # subprocess.run을 사용하여 결과와 에러 메시지를 가로채기
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 모든 패키지 일괄 설치 완료!")
        else:
            print("\n⚠️ 기본 설치에 실패했습니다. (권한 문제일 수 있어 사용자 모드로 재시도합니다)")
            
            # 4. 실패 시 사용자 권한(--user)으로 재시도
            user_install_cmd = [sys.executable, "-m", "pip", "install", "--user"] + missing_packages
            result_user = subprocess.run(user_install_cmd, capture_output=True, text=True)
            
            if result_user.returncode == 0:
                print("✅ 사용자 권한(--user) 일괄 설치 완료!")
            else:
                # 5. 그래도 실패하면 진짜 이유(에러 로그)를 화면에 뱉어내기
                print("\n❌ 최종 설치 실패! 아래의 진짜 에러 원인을 확인해주세요:")
                print("="*50)
                print(result_user.stderr) # 시스템이 뱉어낸 실제 빨간 에러 글씨들
                print("="*50)
                print("💡 힌트: C++ 빌드 도구가 없거나, 인터넷 방화벽 문제일 수 있습니다.")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ 설치 프로세스 작동 중 치명적 에러 발생: {e}")
        sys.exit(1)

def setup_mac_env():
    """맥(Mac) 환경 감지 시 zbar 엔진 자동 설치 시도"""
    if platform.system() == "Darwin":
        print("🍎 Mac 환경 감지됨: QR 해독용 zbar 엔진 자동 설치를 점검합니다...")
        try:
            subprocess.run(["brew", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["brew", "install", "zbar"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ [Mac] zbar 엔진 설치/확인 완료!")
        except FileNotFoundError:
            print("⚠️ [경고] Homebrew가 설치되어 있지 않아 zbar를 자동 설치할 수 없습니다.")
            print("   터미널을 열고 Homebrew 설치 후, 'brew install zbar'를 직접 입력해주세요.")
        except Exception as e:
            print(f"⚠️ [Mac] zbar 자동 설치 중 무시 가능한 문제 발생: {e}")

# --- 1. 봇 실행 전 환경 점검 및 셋업 ---
check_and_install_packages()
setup_mac_env() 
print("✅ 모든 환경 준비 완료!\n")

# --- 자동 설치 완료 후 라이브러리 불러오기 (끊겼던 부분 복구) ---
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
from pyzbar.pyzbar import decode
from PIL import Image

current_folder = os.getcwd()
driver = None

def get_browser_driver():
    """크롬을 우선 시도하고, 실패 시 엣지로 자동 전환하는 듀얼 엔진 함수"""
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