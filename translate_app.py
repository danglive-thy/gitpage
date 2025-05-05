import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from ttkthemes import ThemedTk  # 需要安装 ttkthemes 模块
# 或者使用 tkinter 的 ttk.Style() 自定义样式
import os
import translate  # 引入你提供的 translate.py 模块
import time
import threading

# 支持的目标语言列表
LANGUAGES = {
    "英语 (en)": "en",
    "俄语 (ru)": "ru",
    "阿拉伯语 (ar)": "ar",
    "印尼语 (id)": "id",
    "越南语 (vi)": "vi",
    "泰语 (th)": "th",
    "马来语 (ms)": "ms",
    "西班牙语 (es)": "es",
    "葡萄牙语 (pt)": "pt"
}

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML 翻译工具 - © 2025 CMC-MAC.COM    作者：Haiyang Tang")
        self.root.option_add("*Font", "Helvetica 10")
        self.root.configure(bg="#f5f5f5")
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        style.configure("TEntry", padding=6)
        
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menubar)

        # 文件选择区域
        file_frame = ttk.Frame(root)
        file_frame.pack(pady=10, fill=tk.X, padx=10)

        # 文件路径输入框（宽度增加到75）
        self.file_paths_var = ""  # 存储单个文件路径
        ttk.Label(file_frame, text="源文件路径:").pack(anchor=tk.W)
        self.path_entry = ttk.Entry(file_frame)
        self.path_entry.pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="浏览", command=self.select_files).pack(anchor=tk.E)
        # tk.Label(root, text="源文件路径:").pack(pady=5)
        # self.path_entry = tk.Entry(root, width=100)
        # self.path_entry.pack(pady=5, fill=tk.X)
        # tk.Button(root, text="浏览", command=self.select_files).pack(pady=5)

        # 语言选择区域
        lang_frame = ttk.Frame(root)
        lang_frame.pack(pady=10, fill=tk.X, padx=10)

        # 多选框区域
        self.check_vars = {}
        for lang_name in LANGUAGES:
            var = tk.IntVar()
            ttk.Checkbutton(lang_frame, text=lang_name, variable=var).pack(anchor='w')
            # tk.Checkbutton(root, text=lang_name, variable=var).pack(anchor='w')
            self.check_vars[lang_name] = var
        
        # 按钮区域
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10, fill=tk.X, padx=10)
        self.select_all_button = ttk.Button(btn_frame, text="全选", command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=5)
        self.toggle_all_button = ttk.Button(btn_frame, text="反选", command=self.toggle_all)
        self.toggle_all_button.pack(side=tk.LEFT, padx=5)
        # 全选 / 反选按钮
        # control_frame = tk.Frame(root)
        # control_frame.pack(pady=5)
        # tk.Button(control_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        # tk.Button(control_frame, text="反选", command=self.toggle_all).pack(side=tk.LEFT, padx=5)

        # 进度条
        # self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        # self.progress.pack(pady=10)

        # 日志输出区域
        self.log_area = ScrolledText(root, height=30, wrap=tk.WORD)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 执行按钮
        self.translate_button = ttk.Button(
            root, 
            text="开始翻译", 
            command=self.start_translation,
            style="TButton"
        )
        self.translate_button.pack(pady=20, ipadx=10, ipady=5)
        # self.translate_button = tk.Button(root, text="开始翻译", command=self.start_translation)
        # self.translate_button.pack(pady=20)
    def show_about(self):
        """显示关于窗口"""
        about_text = (
            "HTML 翻译工具\n"
            "版本 1.0\n"
            "© 2025 CMC-MAC.COM\n"
            "作者：Haiyang Tang\n"
            "本软件的翻译功能依赖于通过Ollama部署的本地LLM\n"
            "建议使用ollama run qwen3:14b\n"
            "\n"
            "翻译结果存储在源文件所在目录\n"
            "翻译结果文件名将包含原文件名，后缀为翻译语言的缩写\n"
            "新的翻译结果将直接覆盖旧的翻译结果，对于文件覆盖不会提示\n"
        )
        messagebox.showinfo("关于", about_text)
    def log(self, message):
        """向日志区域添加消息"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()  # 实时刷新界面
    def select_files(self):
        """打开文件对话框选择单个 HTML 文件"""
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if file_path:
            self.file_path_var = file_path  # 存储单个路径
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

    def select_all(self):
        """全选语言选项"""
        for var in self.check_vars.values():
            var.set(1)

    def toggle_all(self):
        """反选语言选项"""
        for name, var in self.check_vars.items():
            var.set(0 if var.get() == 1 else 1)

    def start_translation(self):
        if not hasattr(self, "file_path_var"):
            messagebox.showerror("错误", "请选择一个 HTML 文件")
            return

        selected_langs = [LANGUAGES[name] for name, var in self.check_vars.items() if var.get() == 1]
        if not selected_langs:
            messagebox.showwarning("警告", "请选择至少一种目标语言")
            return

        # 禁用按钮
        self.translate_button.config(state=tk.DISABLED)

        src_file = self.file_path_var
        self.log(f"📄 正在处理文件: {src_file}\n")

        # 启动子线程执行翻译任务
        threading.Thread(
            target=self.run_translations,
            args=(src_file, selected_langs),
            daemon=True
        ).start()

    def enable_translate_button(self):
        """重新启用翻译按钮"""
        self.translate_button.config(state=tk.NORMAL)
    def run_translations(self, src_file, selected_langs):
        try:
            for lang in selected_langs:
                try:
                    output_path = f"{os.path.splitext(src_file)[0]}_{lang}.html"
                    self.log(f"🌐 正在翻译 {src_file} -> {output_path} ({lang})\n")
                    start = time.time()
                    success = translate.translate_html_file(src_file, output_path, src_lang="zh", dest_lang=lang)
                    time_for_translate = time.time() - start

                    if success:
                        self.log(f"✅ 完成-耗时{time_for_translate:.2f}s：zh -> {lang}\n")
                    else:
                        self.log(f"❌ 翻译失败: zh -> {lang}\n")
                except Exception as e:
                    self.log(f"❗ 错误: {e}\n")

            self.log(f"\n✅ 文件翻译完成: {src_file}\n")
        finally:
            # 确保无论是否出错，按钮都会恢复可用
            self.root.after(0, self.enable_translate_button)
            self.root.after(0, lambda: messagebox.showinfo("完成", "翻译已完成！"))


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()