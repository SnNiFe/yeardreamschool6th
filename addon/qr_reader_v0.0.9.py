import sys
import subprocess
import importlib

# ==========================================
# 1. 자동 설치 및 자가 치유 기능 정의
# ==========================================
def ensure_packages(packages):
    try:
        import pip
    except ImportError:
        print("\n[시스템 알림] 현재 환경에 패키지 설치 도구(pip)가 누락되어 있습니다.")
        print(">>> pip 자가 복구를 시작합니다. 잠시만 기다려주세요...\n")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        print("\n[시스템 알림] pip 자동 복구 완료!\n")

    for package_name, import_name in packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"\n[알림] '{package_name}' 패키지가 설치되어 있지 않습니다.")
            print(f">>> '{package_name}' 자동 설치를 진행합니다...\n")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"\n[성공] '{package_name}' 설치가 완료되었습니다!\n")

# ==========================================
# 2. 필요한 패키지 검사 및 자동 설치 실행! 
#    (🚨 중요: exe 파일로 실행될 때는 이 과정을 통째로 건너뜁니다!)
# ==========================================
REQUIRED_PACKAGES = {
    "pyzbar": "pyzbar",
    "Pillow": "PIL",
    "selenium": "selenium" 
}

# 파이썬 내장 센서: getattr(sys, 'frozen', False) 가 True면 exe 상태라는 뜻입니다.
if not getattr(sys, 'frozen', False):
    ensure_packages(REQUIRED_PACKAGES)

# ==========================================
# 3. 설치가 보장된 상태에서 비로소 패키지들을 불러옴
# ==========================================
import tkinter as tk # noqa: E402
from tkinter import filedialog, messagebox, ttk # noqa: E402
from PIL import Image, ImageGrab # type: ignore

try:
    from pyzbar.pyzbar import decode # type: ignore
except OSError as e:
    if sys.platform == 'darwin':
        print("\n[🚨 맥OS 시스템 부품 누락 오류]")
        print("'pyzbar' 파이썬 패키지는 설치되었으나, 맥 환경 구동에 필요한 'zbar' 시스템 라이브러리가 없습니다.")
        print("터미널(Terminal) 창을 열고 아래 명령어를 입력하여 설치한 후 다시 실행해 주세요.")
        print("👉  brew install zbar\n")
        input("엔터(Enter) 키를 누르면 프로그램이 종료됩니다...")
        sys.exit(1)
    raise e

import webbrowser # noqa: E402
import ctypes # noqa: E402
import datetime # noqa: E402
import json # noqa: E402
import os # noqa: E402

# --- 윈도우 화면 배율(DPI) 강제 인식 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- 다중 스캔 및 추적을 위한 설정 ---
auto_scan_enabled = False
scan_schedules = [] 
last_scanned_info = {} 
scan_interval_ms = 5000 
auto_scan_job = None  

DB_FILE = "schedules.json"

# ==================== UI 새로고침 전용 함수 ====================

def update_schedule_listbox():
    schedule_listbox.delete(0, tk.END)
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    today_date = datetime.datetime.now().date()
    
    for start_t, end_t, extra_count, filter_str, repeat_str in scan_schedules:
        display_filter = filter_str if filter_str else "모든 URL 허용"
        base_text = f"{start_t.strftime('%H:%M')} ~ {end_t.strftime('%H:%M')} [{repeat_str}] (추가: {extra_count}회) [필터: {display_filter}]"
        
        slot_name = f"{start_t}-{end_t}"
        info = last_scanned_info.get(slot_name)
        
        status_text = ""
        if info and info["date"] == today_date:
            current_count = info["count"]
            max_count = 1 + extra_count
            dt_date = info["date"]
            weekday_str = weekdays[dt_date.weekday()]
            
            if current_count >= max_count:
                status_text = f" ➔ [✅ {dt_date.month}/{dt_date.day}({weekday_str}) {current_count}/{max_count}회 완료]"
            elif current_count > 0:
                status_text = f" ➔ [▶ {dt_date.month}/{dt_date.day}({weekday_str}) {current_count}/{max_count}회 진행중]"
                
        schedule_listbox.insert(tk.END, base_text + status_text)

# ==================== 데이터 저장/불러오기 함수 ====================

def save_schedules_to_file():
    save_data = []
    for start_t, end_t, extra_count, filter_str, repeat_str in scan_schedules:
        save_data.append({
            "start": start_t.strftime("%H:%M"),
            "end": end_t.strftime("%H:%M"),
            "extra_count": extra_count,
            "filter": filter_str,
            "repeat": repeat_str
        })
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"설정 저장 실패: {e}")

def load_schedules_from_file():
    if not os.path.exists(DB_FILE):
        return
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            load_data = json.load(f)
            for item in load_data:
                sh, sm = map(int, item["start"].split(':'))
                eh, em = map(int, item["end"].split(':'))
                start_t = datetime.time(sh, sm)
                end_t = datetime.time(eh, em)
                extra_count = item["extra_count"]
                filter_str = item["filter"]
                repeat_str = item["repeat"]
                
                scan_schedules.append((start_t, end_t, extra_count, filter_str, repeat_str))
        
        update_schedule_listbox()
        
    except Exception as e:
        messagebox.showwarning("경고", f"기존 설정을 불러오는 중 오류가 발생했습니다.\n{e}")

# ==================== 핵심 기능 함수 ====================

def process_image(img):
    try:
        decoded_objects = decode(img)
        if not decoded_objects:
            result_label.config(text="이미지에서 QR 코드를 찾을 수 없습니다.", fg="red", cursor="")
            result_label.unbind("<Button-1>")
            return

        qr_data = decoded_objects[0].data.decode('utf-8')
        result_label.config(text=f"인식 완료! (클릭하면 열립니다)\n{qr_data}", fg="blue", cursor="hand2")
        result_label.bind("<Button-1>", lambda e: open_link(qr_data))
        
    except Exception as e:
        messagebox.showerror("오류", f"이미지 처리 중 문제가 발생했습니다.\n{e}")

def open_link(url):
    if url.startswith("http://") or url.startswith("https://"):
        webbrowser.open(url)
    else:
        messagebox.showinfo("QR 텍스트 내용", url)

def load_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    if file_path: process_image(Image.open(file_path))

def load_from_clipboard(event=None):
    if event is not None and isinstance(event.widget, tk.Entry):
        return
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image): process_image(img)
        else: messagebox.showwarning("경고", "클립보드에 이미지가 없습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"클립보드 읽기 오류.\n{e}")

def capture_fullscreen():
    root.iconify()
    root.after(300, _do_fullscreen_capture)

def _do_fullscreen_capture():
    try:
        img = ImageGrab.grab()
        root.deiconify()
        process_image(img)
    except Exception as e:
        root.deiconify()
        messagebox.showerror("오류", f"화면 캡처 오류.\n{e}")

def start_area_capture():
    root.iconify()
    root.after(300, _show_transparent_overlay)

def _show_transparent_overlay():
    overlay = tk.Toplevel(root)
    overlay.attributes('-fullscreen', True)
    overlay.attributes('-alpha', 0.3)
    overlay.attributes('-topmost', True)
    overlay.config(bg='black', cursor="cross")

    canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    rect_id = [None]
    start_x, start_y = [0], [0]

    def on_press(event):
        start_x[0], start_y[0] = event.x, event.y
        rect_id[0] = canvas.create_rectangle(start_x[0], start_y[0], start_x[0], start_y[0], outline='red', width=2)

    def on_drag(event):
        canvas.coords(rect_id[0], start_x[0], start_y[0], event.x, event.y)

    def on_release(event):
        end_x, end_y = event.x, event.y
        overlay.destroy()
        
        x1, x2 = sorted([start_x[0], end_x])
        y1, y2 = sorted([start_y[0], end_y])

        if x2 - x1 < 10 or y2 - y1 < 10:
            root.deiconify()
            return
        root.after(300, lambda: _do_area_capture(x1, y1, x2, y2))

    def _do_area_capture(x1, y1, x2, y2):
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        root.deiconify()
        process_image(img)

    canvas.bind('<Button-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)
    overlay.bind('<Escape>', lambda e: (overlay.destroy(), root.deiconify()))

# ==================== GUI 편의성 함수 ====================

def set_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.config(fg='grey')

    def on_focusin(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focusout(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focusin)
    entry.bind("<FocusOut>", on_focusout)

# ==================== 스케줄 관리 GUI 함수 ====================

def add_schedule():
    start_str = start_entry.get().strip()
    end_str = end_entry.get().strip()
    extra_str = extra_count_entry.get().strip()
    filter_str = filter_entry.get().strip()
    repeat_str = repeat_combo.get() 
    
    if start_str == "HH:MM" or end_str == "HH:MM":
        messagebox.showerror("입력 오류", "정확한 시간을 입력해주세요.")
        return

    if filter_str == "예: naver.com (공백 시 모든 URL 허용)" or filter_str == "":
        filter_str = ""

    try:
        sh, sm = map(int, start_str.split(':'))
        eh, em = map(int, end_str.split(':'))
        start_t = datetime.time(sh, sm)
        end_t = datetime.time(eh, em)
        extra_count = int(extra_str)
        
        if start_t >= end_t:
            messagebox.showerror("입력 오류", "종료 시간이 시작 시간보다 빠르거나 같을 수 없습니다.")
            return
        if extra_count < 0:
            messagebox.showerror("입력 오류", "추가 확인 횟수는 0 이상이어야 합니다.")
            return
            
        scan_schedules.append((start_t, end_t, extra_count, filter_str, repeat_str))
        save_schedules_to_file()
        update_schedule_listbox()
        
        start_entry.delete(0, tk.END)
        end_entry.delete(0, tk.END)
        set_placeholder(start_entry, "HH:MM")
        set_placeholder(end_entry, "HH:MM")
        
        extra_count_entry.delete(0, tk.END)
        extra_count_entry.insert(0, "0")
        
        filter_entry.delete(0, tk.END)
        set_placeholder(filter_entry, "예: naver.com (공백 시 모든 URL 허용)")
        
    except ValueError:
        messagebox.showerror("입력 오류", "시간 형식(HH:MM)과 추가 횟수(숫자)를 확인해주세요.")

def delete_schedule():
    selected = schedule_listbox.curselection()
    if not selected:
        messagebox.showwarning("삭제 오류", "삭제할 시간대를 선택해주세요.")
        return
    idx = selected[0]
    scan_schedules.pop(idx)      
    save_schedules_to_file()
    update_schedule_listbox()

# ==================== 자동 스캔 감시 함수 ====================

def check_auto_scan():
    global last_scanned_info, auto_scan_job
    if not auto_scan_enabled: return

    now = datetime.datetime.now()
    current_time = now.time()
    current_date = now.date()
    current_weekday = now.weekday() 

    for start_t, end_t, extra_count, filter_str, repeat_str in scan_schedules:
        is_target_day = False
        if repeat_str == "매일":
            is_target_day = True
        elif repeat_str == "평일 (월~금)" and current_weekday <= 4:
            is_target_day = True
        elif repeat_str == "주말 (토~일)" and current_weekday >= 5:
            is_target_day = True
            
        if not is_target_day:
            continue 

        slot_name = f"{start_t}-{end_t}"
        info = last_scanned_info.get(slot_name, {"date": None, "count": 0})
        
        if info["date"] != current_date:
            info = {"date": current_date, "count": 0}

        total_required_hits = 1 + extra_count

        if start_t <= current_time <= end_t and info["count"] < total_required_hits:
            if _silent_scan(info["count"], extra_count, filter_str):
                info["count"] += 1
                last_scanned_info[slot_name] = info
                update_schedule_listbox()
                break 

    if auto_scan_enabled:
        auto_scan_job = root.after(scan_interval_ms, check_auto_scan) 

def _silent_scan(current_success_count, extra_count, filter_str):
    try:
        img = ImageGrab.grab()
        decoded_objects = decode(img)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            if qr_data.startswith("http://") or qr_data.startswith("https://"):
                if filter_str and (filter_str not in qr_data):
                    return False
                webbrowser.open(qr_data)
                
                if current_success_count == 0:
                    status_text = f"⏰ 자동 스캔 성공! (첫 인식 완료)\n{qr_data}"
                else:
                    status_text = f"⏰ 자동 스캔 성공! (추가 확인 {current_success_count}/{extra_count}회)\n{qr_data}"
                
                result_label.config(text=status_text, fg="green")
                return True
    except Exception:
        pass
    return False

def toggle_auto_scan():
    global auto_scan_enabled, scan_interval_ms, auto_scan_job
    if not scan_schedules:
        messagebox.showwarning("실행 오류", "먼저 감시할 시간을 추가해 주세요.")
        return

    if auto_scan_enabled:
        auto_scan_enabled = False
        if auto_scan_job is not None:
            root.after_cancel(auto_scan_job)
            auto_scan_job = None
            
        btn_auto_cap.config(text="⏰ 자동 감시 켜기", fg="black")
        result_label.config(text="자동 감시가 중지되었습니다.", fg="black")
        add_btn.config(state="normal")
        del_btn.config(state="normal")
        interval_entry.config(state="normal")
        repeat_combo.config(state="readonly")
    else:
        try:
            sec = float(interval_entry.get())
            if sec < 0.5:
                messagebox.showwarning("경고", "최소 0.5초 이상으로 설정해주세요.")
                return
            scan_interval_ms = int(sec * 1000)
        except ValueError:
            messagebox.showerror("입력 오류", "감시 주기는 숫자로 입력해주세요.")
            return

        auto_scan_enabled = True
        btn_auto_cap.config(text=f"⏰ 자동 감시 끄기 ({sec}초 간격 작동중...)", fg="blue")
        result_label.config(text=f"설정된 시간대에 {sec}초 간격으로 화면을 감시합니다.", fg="blue")
        add_btn.config(state="disabled")
        del_btn.config(state="disabled")
        interval_entry.config(state="disabled")
        repeat_combo.config(state="disabled")
        
        update_schedule_listbox()
        check_auto_scan()

# ==================== 메인 화면 (GUI) 배치 ====================
root = tk.Tk()
root.title("최종 완성형 QR 리더기")
root.geometry("640x680")

instruction_label = tk.Label(root, text="원하는 방식을 선택하여 QR 코드를 스캔하세요.", pady=5)
instruction_label.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

btn_file = tk.Button(btn_frame, text="📁 이미지 열기", command=load_from_file, width=24, height=2)
btn_file.grid(row=0, column=0, padx=5, pady=5)

btn_clip = tk.Button(btn_frame, text="📋 클립보드 읽기", command=load_from_clipboard, width=24, height=2)
btn_clip.grid(row=0, column=1, padx=5, pady=5)

btn_full_cap = tk.Button(btn_frame, text="🖥️ 1회 전체 스캔", command=capture_fullscreen, width=24, height=2)
btn_full_cap.grid(row=1, column=0, padx=5, pady=5)

btn_area_cap = tk.Button(btn_frame, text="✂️ 영역 지정 캡처", command=start_area_capture, width=24, height=2)
btn_area_cap.grid(row=1, column=1, padx=5, pady=5)

schedule_frame = tk.LabelFrame(root, text="⏰ 자동 감시 설정", padx=10, pady=10)
schedule_frame.pack(fill="x", padx=15, pady=5)

input_frame = tk.Frame(schedule_frame)
input_frame.pack(pady=5)

tk.Label(input_frame, text="시작").grid(row=0, column=0, padx=2)
start_entry = tk.Entry(input_frame, width=6, justify="center")
start_entry.grid(row=0, column=1, padx=2)

tk.Label(input_frame, text="종료").grid(row=0, column=2, padx=2)
end_entry = tk.Entry(input_frame, width=6, justify="center")
end_entry.grid(row=0, column=3, padx=2)

tk.Label(input_frame, text="추가확인").grid(row=0, column=4, padx=2)
extra_count_entry = tk.Entry(input_frame, width=4, justify="center")
extra_count_entry.insert(0, "0") 
extra_count_entry.grid(row=0, column=5, padx=2)

add_btn = tk.Button(input_frame, text="➕ 추가", command=add_schedule, width=8)
add_btn.grid(row=0, column=6, padx=5)

tk.Label(input_frame, text="반복 요일").grid(row=1, column=0, padx=2, pady=5)
repeat_combo = ttk.Combobox(input_frame, values=["매일", "평일 (월~금)", "주말 (토~일)"], width=10, state="readonly")
repeat_combo.current(0) 
repeat_combo.grid(row=1, column=1, columnspan=2, padx=2, pady=5, sticky="w")

tk.Label(input_frame, text="URL 필터").grid(row=2, column=0, padx=2, pady=5)
filter_entry = tk.Entry(input_frame, width=35)
filter_entry.grid(row=2, column=1, columnspan=5, padx=2, pady=5, sticky="w")

set_placeholder(start_entry, "HH:MM")
set_placeholder(end_entry, "HH:MM")
set_placeholder(filter_entry, "예: naver.com (공백 시 모든 URL 허용)")

schedule_listbox = tk.Listbox(schedule_frame, height=4)
schedule_listbox.pack(fill="x", pady=5)

del_btn = tk.Button(schedule_frame, text="🗑️ 선택된 시간 삭제", command=delete_schedule)
del_btn.pack(fill="x")

control_frame = tk.Frame(root)
control_frame.pack(pady=5)

tk.Label(control_frame, text="감시 주기(초) :").pack(side="left", padx=5)
interval_entry = tk.Entry(control_frame, width=5, justify="center")
interval_entry.insert(0, "5") 
interval_entry.pack(side="left")

btn_auto_cap = tk.Button(root, text="⏰ 자동 감시 시작", command=toggle_auto_scan, width=50, height=2, font=("Malgun Gothic", 9, "bold"))
btn_auto_cap.pack(pady=5)

result_label = tk.Label(root, text="여기에 링크가 표시됩니다.", font=("Malgun Gothic", 10, "bold"), pady=5)
result_label.pack()

version_label = tk.Label(root, text="v0.0.9", font=("Malgun Gothic", 8), fg="gray")
version_label.pack(side="bottom", anchor="e", padx=10, pady=5)

root.bind('<Control-v>', load_from_clipboard)  
if sys.platform == 'darwin':
    root.bind('<Command-v>', load_from_clipboard)  

load_schedules_from_file()
root.mainloop()