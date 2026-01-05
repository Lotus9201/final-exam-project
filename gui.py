import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

API_URL = "http://127.0.0.1:8000/quotes"

def run_in_thread(target_func, *args):
    threading.Thread(target=target_func, args=args, daemon=True).start()

class QuoteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("名言佳句管理系統 (Threading 版)")
        self.root.geometry("800x600")
        
        # --- UI 佈局 ---
        # 1. 資料顯示區
        self.tree = ttk.Treeview(root, columns=("ID", "Author", "Text", "Tags"), show='headings')
        for col in ("ID", "Author", "Text", "Tags"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # 2. 編輯區
        edit_frame = tk.LabelFrame(root, text="編輯/新增區")
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(edit_frame, text="名言內容 (Text):").grid(row=0, column=0, sticky="nw")
        self.txt_content = tk.Text(edit_frame, height=5)
        self.txt_content.grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=2)
        
        tk.Label(edit_frame, text="作者 (Author):").grid(row=1, column=0)
        self.ent_author = tk.Entry(edit_frame)
        self.ent_author.grid(row=1, column=1, sticky="we", padx=5)
        
        tk.Label(edit_frame, text="標籤 (Tags):").grid(row=1, column=2)
        self.ent_tags = tk.Entry(edit_frame)
        self.ent_tags.grid(row=1, column=3, sticky="we", padx=5)
        edit_frame.columnconfigure((1, 3), weight=1)

        # 3. 按鈕區
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_refresh = tk.Button(btn_frame, text="重新整理", bg="lightblue", command=self.refresh_data)
        self.btn_refresh.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.btn_add = tk.Button(btn_frame, text="新增", bg="lightgreen", command=self.add_data)
        self.btn_add.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.btn_update = tk.Button(btn_frame, text="更新", bg="orange", state=tk.DISABLED, command=self.update_data)
        self.btn_update.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.btn_delete = tk.Button(btn_frame, text="刪除", bg="tomato", state=tk.DISABLED, command=self.delete_data)
        self.btn_delete.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 4. 狀態列
        self.status_var = tk.StringVar(value="準備就緒")
        self.status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.selected_id = None
        self.refresh_data()

    # --- 功能邏輯 ---
    def update_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            val = item['values']
            self.selected_id = val[0]
            self.ent_author.delete(0, tk.END); self.ent_author.insert(0, val[1])
            self.txt_content.delete("1.0", tk.END); self.txt_content.insert("1.0", val[2])
            self.ent_tags.delete(0, tk.END); self.ent_tags.insert(0, val[3])
            self.btn_update.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)

    def refresh_data(self):
        self.update_status("連線中，請稍候...")
        def worker():
            try:
                res = requests.get(API_URL, timeout=5)
                data = res.json()
                self.root.after(0, lambda: self.fill_tree(data))
                self.update_status("資料載入完成")
            except:
                self.update_status("錯誤：無法連線至 API")
        run_in_thread(worker)

    def fill_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", tk.END, values=(row['id'], row['author'], row['text'], row['tags']))

    def add_data(self):
        payload = {"text": self.txt_content.get("1.0", tk.END).strip(), 
                   "author": self.ent_author.get(), "tags": self.ent_tags.get()}
        def worker():
            try:
                requests.post(API_URL, json=payload)
                self.update_status("新增成功！")
                self.refresh_data()
            except: self.update_status("新增失敗")
        run_in_thread(worker)

    def update_data(self):
        if not self.selected_id: return
        payload = {"text": self.txt_content.get("1.0", tk.END).strip(), 
                   "author": self.ent_author.get(), "tags": self.ent_tags.get()}
        def worker():
            requests.put(f"{API_URL}/{self.selected_id}", json=payload)
            self.update_status("更新成功！")
            self.refresh_data()
        run_in_thread(worker)

    def delete_data(self):
        if not self.selected_id: return
        def worker():
            requests.delete(f"{API_URL}/{self.selected_id}")
            self.update_status("刪除成功！")
            self.refresh_data()
        run_in_thread(worker)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGUI(root)
    root.mainloop()