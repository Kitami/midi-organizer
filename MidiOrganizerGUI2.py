import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import mido
from mido import MidiFile, Message, MetaMessage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import io
from PIL import Image, ImageTk

class MidiOrganizerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("MIDI文件分析器")
        self.graphs = []
        self.chart_image = None
        self.data = None
        self.move_line = True

        # 创建文本框
        self.filepath_var = tk.StringVar()
        self.filepath_entry = ttk.Entry(self.window, textvariable=self.filepath_var)
        self.filepath_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # 创建“选择文件”按钮
        self.select_button = ttk.Button(self.window, text="选择文件", command=self.select_file)
        self.select_button.grid(row=0, column=1, padx=5, pady=5)

        # 创建用于显示图表区域的Notebook
        self.notebook = ttk.Notebook(self.window)
        self.notebook.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # 创建图表视图，并将其添加到Notebook
        self.create_graph_view("Graph 1")
        self.create_graph_view("Graph 2")
        self.create_graph_view("Graph 3")

        # 创建用于指定时值、力度和BPM的输入框
        self.velocity_threshold_var = tk.StringVar()
        self.duration_threshold_var = tk.StringVar()
        self.bpm_var = tk.StringVar()
        self.midi_file = None
        self.old_tempo = 0
        
        # 创建用于显示表格的Text
        # 创建用于显示表格的 Treeview
        self.table_columns = ("音符长度区间", "音符个数")
        self.table_tree = ttk.Treeview(self.graphs[1], columns=self.table_columns, show="headings")

        # 设置表头
        for col in self.table_columns:
            self.table_tree.heading(col, text=col)

        # 使用 grid 放置 Treeview 在 self.graphs[1] 中
        self.table_tree.grid(in_=self.graphs[1], row=1, column=0, padx=5, pady=5, sticky="w")

        # 用于存储红色横线的引用
        self.horizontal_line = None
        # 用于存储红色横线上的y轴坐标文本的引用
        self.y_label_text = None
        
        input_frame = ttk.Frame(self.window, padding=10)
        input_frame.grid(row=4, column=0, columnspan=2, sticky="we")
        ttk.Label(input_frame, text="Velocity:").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.velocity_threshold_var).grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(input_frame, text="Duration:").grid(row=1, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.duration_threshold_var).grid(row=1, column=1, padx=5, pady=5, sticky="we")
        ttk.Label(input_frame, text="BPM:").grid(row=2, column=0, padx=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.bpm_var).grid(row=2, column=1, padx=5, pady=5, sticky="we")

        # 创建“保存”按钮
        self.save_button = ttk.Button(self.window, text="保存", command=self.save)
        self.save_button.grid(row=8, column=0, padx=5, pady=5, sticky="w")

        # 绑定鼠标移动事件
        self.graphs[0].bind("<Motion>", self.on_mouse_move)
        
        # 绑定鼠标点击事件处理函数
        self.graphs[0].bind("<Button-1>", self.on_mouse_click)

    def calculate_note_statistics(self):
        # 初始化统计数据
        # 生成 n 分音符对应的时值误差区间
        note_lengths = [f"{2**i}分音符" for i in range(8)]
        note_counts = [0] * len(note_lengths)

        if self.midi_file:
            tick_per_beat = self.midi_file.ticks_per_beat

            # 存储每个音符的开始时间
            note_start_times = {}
            
            for track in self.midi_file.tracks:
                current_time = 0

                for msg in track:
                    current_time += msg.time

                    if msg.type == 'note_on':
                        note_start_times[msg.note] = current_time
                    elif msg.type == 'note_off' and msg.note in note_start_times:
                        note_start_time = note_start_times.pop(msg.note)
                        note_duration_ticks = current_time - note_start_time
                        note_duration_seconds = mido.tick2second(note_duration_ticks, tick_per_beat, self.old_tempo)

                        # 将时间转换为 BPM
                        bpm = mido.tempo2bpm(self.old_tempo)
                        beat_duration_seconds = 60 / bpm

                        # 将时间转换为拍数
                        note_duration_beats = note_duration_seconds / beat_duration_seconds
   
                        # 判断时值在误差区间内的音符
                        error_percentage = 0.2
                        for i in range(8):
                            n = 2**i
                            lower_bound = (1 - error_percentage) / n
                            upper_bound = (1 + error_percentage) / n
                            
                            if lower_bound <= note_duration_beats <= upper_bound:
                                note_counts[i] += 1

         # 清空 Treeview 中的所有项目
        self.table_tree.delete(*self.table_tree.get_children())

        # 将统计结果写入 Treeview
        for length, count in zip(note_lengths, note_counts):
            self.table_tree.insert("", "end", values=(length, count))
        
    def create_graph_view(self, graph_name):
        # 创建用于显示图表区域
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text=graph_name)

        # 在新的Frame中创建Canvas
        graph = tk.Canvas(graph_frame, width=800, height=300, borderwidth=2, relief="groove")
        graph.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.graphs.append(graph)
        
    def on_mouse_click(self, event):
            # 如果左键单击，切换横线移动状态
            if event.num == 1:
                self.move_line = not self.move_line

    def on_mouse_move(self, event):
        # 如果没有加载 MIDI 文件，不执行以下操作
        if not self.midi_file:
            return
        
        # 获取鼠标的坐标
        x = event.x
        y = event.y
        y_in_chart = int (-(y - 256) / 220 * 127)
        
        # 如果横线不可移动，不执行以下操作
        if not self.move_line:
            return

        # 如果红色横线不存在，创建它
        if not self.horizontal_line:
            self.horizontal_line = self.graphs[0].create_line(0, y, 800, y, fill="red", tag="line_tag")

        # 如果文本不存在，创建它
        if not self.y_label_text:
            self.y_label_text = self.graphs[0].create_text(10, 10, text=f"Y: {y}", anchor=tk.NW, fill="red", tag="text_tag")

        # 更新横线的位置
        self.graphs[0].coords("line_tag", 0, y, 800, y)
        self.velocity_threshold_var.set(str(y_in_chart))
        
        # 更新文本的位置和内容
        self.graphs[0].coords("text_tag", 10, 10)
        
        # 计算小于和大于 y_in_chart 的音符个数
        velocity_greater = sum(1 for velocity in self.data if velocity[1] > y_in_chart)
        velocity_less = sum(1 for velocity in self.data if velocity[1] < y_in_chart)
        
        # 计算占比
        total_notes = len(self.data)
        percent_greater = (velocity_greater / total_notes) * 100
        percent_less = (velocity_less / total_notes) * 100
        
        if (0 <= y_in_chart and y_in_chart <= 127):
            self.graphs[0].itemconfig("text_tag", text=f"Y: {y_in_chart}\n"
            f"Velocity > Y: {velocity_greater} ({percent_greater:.2f}%)\n"
            f"Velocity < Y: {velocity_less} ({percent_less:.2f}%)")

        # 确保红色横线和文本在最上层显示
        self.graphs[0].tag_raise("line_tag")
        self.graphs[0].tag_raise("text_tag")

    def plot_scatter(self, graph_index, x_label, y_label, data):
        if graph_index < 0 or graph_index >= len(self.graphs):
            print("Invalid graph_index")
            return
        
        x_values, y_values = zip(*data)

        fig, ax = plt.subplots(figsize=(800/100, 300/100))  # 将尺寸设置为graph1的尺寸
        ax.scatter(x_values, y_values)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title("note velocity")

        # 将图表显示在Tkinter窗口上
        self.show_plot(graph_index, fig)

    def show_plot(self, graph_index, fig):
        # 将Matplotlib图形转换为Tkinter PhotoImage
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        img = Image.open(buffer)
        self.chart_image = ImageTk.PhotoImage(img)
        
        # 清空指定图表区域
        graph_widget = self.graphs[graph_index]
        graph_widget.delete("all")

        # 将图表插入Tkinter窗口作为背景图片
        graph_widget.create_image(0, 0, anchor=tk.NW, image=self.chart_image)

        # 调整图表布局以适应Tkinter窗口
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    def plot_velocity_scatter(self):
        if not self.midi_file:
            print("Please analyze a MIDI file first.")
            return

        self.data = []
        tick_per_beat = self.midi_file.ticks_per_beat

        for track in self.midi_file.tracks:
            current_time = 0

            for msg in track:
                current_time += msg.time
                time_in_seconds = mido.tick2second(current_time, tick_per_beat, self.old_tempo)
                
                if msg.type == 'note_on':
                    self.data.append((time_in_seconds, msg.velocity))

        self.plot_scatter(0, "Time", "Velocity", self.data)

    def set_bpm(self):
        new_bpm = float(self.bpm_var.get())
        new_tempo = mido.bpm2tempo(new_bpm)
        
        for track in self.midi_file.tracks:
            for i, msg in enumerate(track):
                if msg.type == 'set_tempo':
                    track[i] = MetaMessage('set_tempo', tempo=new_tempo, time=msg.time)
                    break
                if hasattr(msg, 'time') and msg.time > 0:
                    new_time = round(msg.time * self.old_tempo / new_tempo )
                    
                    new_msg = Message(msg.type, time=new_time, **{
                        attr: getattr(msg, attr) 
                        for attr in ['channel', 'frame_type', 'frame_value', 'control', 'note', 'program', 'song', 'value', 'velocity', 'data', 'pitch', 'pos'] 
                        if hasattr(msg, attr)
                    })
                    
                    track[i] = new_msg

    def save(self):
        velocity_threshold = self.velocity_threshold_var.get()
        duration_threshold = self.duration_threshold_var.get()
        filepath = self.filepath_var.get()
        
        if not filepath:
            print("Please select a MIDI file first.")
            return
        
        self.midi_file.print_tracks(True)
        self.set_bpm()
        self.midi_file.print_tracks(True)
        
        try:
            new_filepath = filepath.replace('.midi', '_edited.midi')
            new_filepath = filepath.replace('.mid', '_edited.midi')
            self.midi_file.save(new_filepath)
            print(f"File saved successfully: {new_filepath}")

        except Exception as e:
            print(f"Error saving MIDI file: {e}")
        
    def analyze(self):
        filepath = self.filepath_var.get()
        
        if not filepath:
            return
        try:
            self.midi_file = MidiFile(filepath)
            bpm = self.calculate_bpm()
            self.bpm_var.set(str(bpm))
            self.plot_velocity_scatter()
            
            # 统计音符信息
            self.calculate_note_statistics()

        except Exception as e:
            print(f"Error analyzing MIDI file: {e}")
        
    def calculate_bpm(self):
        # 初始化 BPM 为 None
        bpm = 0
        for msg in self.midi_file:
            if msg.type == 'set_tempo':
                self.old_tempo = msg.tempo
                bpm = mido.tempo2bpm(msg.tempo)
        return round(bpm, 4) if bpm else 0
        
    def select_file(self):
        filepath = askopenfilename()
        if filepath:
            self.filepath_var.set(filepath)
            self.analyze()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = MidiOrganizerGUI()
    gui.run()
