import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

class MidiOrganizerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("MIDI文件分析器")

        # 创建文本框
        self.filepath_var = tk.StringVar()
        self.filepath_entry = ttk.Entry(self.window, textvariable=self.filepath_var)
        self.filepath_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # 创建“选择文件”按钮
        self.select_button = ttk.Button(self.window, text="选择文件", command=self.select_file)
        self.select_button.grid(row=0, column=1, padx=5, pady=5)

        # 创建“开始分析”按钮
        self.analyze_button = ttk.Button(self.window, text="开始分析", command=self.analyze)
        self.analyze_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # 创建分析结果的框
        self.velocity_fig = ttk.Frame(self.window, width=400, height=300, borderwidth=2, relief="groove")
        self.velocity_fig.grid(row=2, column=0, padx=5, pady=5)

        self.duration_fig = ttk.Frame(self.window, width=400, height=300, borderwidth=2, relief="groove")
        self.duration_fig.grid(row=2, column=1, padx=5, pady=5)

        # 创建用于指定时值、力度和BPM的输入框
        velocity_threshold_var=0
        duration_threshold_var=0
        bpm_var=0
        quantize_var=0
        
        input_frame = ttk.Frame(self.window, padding=10)
        input_frame.grid(row=3, column=0, columnspan=2, sticky="we")

        ttk.Label(input_frame, text="Velocity threshold:").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=velocity_threshold_var).grid(row=0, column=1, padx=5, pady=5, sticky="we")

        ttk.Label(input_frame, text="Duration threshold:").grid(row=1, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=duration_threshold_var).grid(row=1, column=1, padx=5, pady=5, sticky="we")

        ttk.Label(input_frame, text="BPM:").grid(row=2, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=bpm_var).grid(row=2, column=1, padx=5, pady=5, sticky="we")
        
        # 创建下拉菜单，用于选择Quantize单位
        ttk.Label(input_frame, text="Quantize unit:").grid(row=3, column=0, padx=5, sticky="w")
        ttk.Combobox(input_frame, textvariable=quantize_var, values=["16分音符", "32分音符"]).grid(row=3, column=1, padx=5, pady=5, sticky="we")

        # 创建“执行”按钮
        self.execute_button = ttk.Button(self.window, text="执行", command=self.execute)
        self.execute_button.grid(row=7, column=0, padx=5, pady=5, sticky="w")

    def select_file(self):
        filepath = askopenfilename()
        if filepath:
            self.filepath_var.set(filepath)

    def analyze(self):
        filepath = self.filepath_var.get()
        # 执行分析操作并在分析结果框中显示图表

    def execute(self):
        velocity_threshold = self.velocity_threshold_var.get()
        duration_threshold = self.duration_threshold_var.get()
        bpm = self.bpm_var.get()
        quantize_unit = self.quantize_var.get()
        # 执行Quantize操作

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = MidiOrganizerGUI()
    gui.run()
