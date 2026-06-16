import os
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.scrolledtext as scrolledtext

def fix_win_korean_paths(target_dir, log_widget):
    files_changed = 0
    dirs_changed = 0

    for root, dirs, files in os.walk(target_dir, topdown=False):
        
        # 1. 파일 이름 변경 (윈도우 NFC -> 맥 NFD)
        for name in files:
            # 핵심 변경 포인트: NFC 대신 NFD를 사용합니다.
            normalized_name = unicodedata.normalize('NFD', name)
            if name != normalized_name:
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, normalized_name)
                os.rename(old_path, new_path)
                
                log_widget.insert(tk.END, f"📄 [파일] {name} -> 맥용으로 변환됨\n")
                log_widget.see(tk.END)
                files_changed += 1
        
        # 2. 폴더 이름 변경 (윈도우 NFC -> 맥 NFD)
        for name in dirs:
            normalized_name = unicodedata.normalize('NFD', name)
            if name != normalized_name:
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, normalized_name)
                os.rename(old_path, new_path)
                
                log_widget.insert(tk.END, f"📁 [폴더] {name} -> 맥용으로 변환됨\n")
                log_widget.see(tk.END)
                dirs_changed += 1
                
    return files_changed, dirs_changed

def select_folder_and_run():
    target_dir = filedialog.askdirectory(title="맥으로 보낼 최상위 폴더를 선택하세요")
    if not target_dir:
        return
    
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, f"🎯 선택된 폴더: {target_dir}\n작업을 시작합니다...\n\n")
    window.update() 
    
    f_count, d_count = fix_win_korean_paths(target_dir, log_text)
    
    log_text.insert(tk.END, f"\n✅ 맥(Mac) 호환용 변환 작업이 완료되었습니다!\n")
    log_text.insert(tk.END, f"(총 변환된 파일: {f_count}개, 폴더: {d_count}개)\n")
    log_text.see(tk.END)
    messagebox.showinfo("작업 완료", f"총 {f_count}개의 파일과 {d_count}개의 폴더 이름이 맥(NFD) 방식으로 변환되었습니다.")

# --- GUI 화면 설정 ---
window = tk.Tk()
window.title("윈도우 -> 맥(Mac) 파일명 변환기")
window.geometry("650x450")

instruction = tk.Label(window, text="버튼을 눌러 맥(Mac)으로 넘길 폴더를 선택하세요.\n(윈도우 한글을 맥이 좋아하는 NFD 방식으로 분해합니다)", font=("맑은 고딕", 11), pady=10)
instruction.pack()

run_button = tk.Button(window, text="폴더 선택 및 실행", command=select_folder_and_run, font=("맑은 고딕", 12, "bold"), bg="#2196F3", fg="white", padx=10, pady=5)
run_button.pack(pady=10)

log_text = scrolledtext.ScrolledText(window, width=80, height=20, font=("맑은 고딕", 10))
log_text.pack(padx=20, pady=10)
log_text.insert(tk.END, "대기 중...\n")

window.mainloop()
