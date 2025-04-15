#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Dict, List
import os
import sys

def check_environment() -> None:
    """检查运行环境"""
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python可执行文件: {sys.executable}")
    print(f"程序文件位置: {os.path.abspath(__file__)}")

class KTypeConverter:
    def __init__(self):
        self.types: Dict[str, Dict] = {}
        self.current_type: str = "K"
        self.load_data()
        
    def load_data(self) -> None:
        """加载热电偶分度表数据"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = Path(__file__).parent
                
            data_file = Path(base_path) / 'thermocouple_data.json'
            print(f"尝试加载数据文件: {data_file}")
            
            if not data_file.exists():
                raise FileNotFoundError(f"文件不存在: {data_file}")
                
            with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                if 'types' not in data:
                    raise json.JSONDecodeError("数据格式错误：缺少类型数据", "", 0)
                self.types = data['types']
                print("数据加载成功")
        except FileNotFoundError as e:
            raise RuntimeError(f"找不到数据文件: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"数据文件格式错误: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"加载数据时发生错误: {str(e)}")

    def set_type(self, type_name: str) -> None:
        """设置当前热电偶类型"""
        if type_name not in self.types:
            raise ValueError(f"不支持的热电偶类型: {type_name}")
        self.current_type = type_name

    def get_current_range(self) -> Dict[str, float]:
        """获取当前类型的范围"""
        return self.types[self.current_type]['range']

    def get_current_data(self) -> List[Dict[str, float]]:
        """获取当前类型的数据"""
        return self.types[self.current_type]['data']

    def temp_to_mv(self, temp: float) -> Optional[float]:
        """温度转换为热电势"""
        range_data = self.get_current_range()
        if not range_data['temp_min'] <= temp <= range_data['temp_max']:
            raise ValueError(
                f"温度超出范围 ({range_data['temp_min']}°C ~ {range_data['temp_max']}°C)"
            )
        
        data = self.get_current_data()
        for i in range(len(data) - 1):
            t1, t2 = data[i]['temp'], data[i + 1]['temp']
            if t1 <= temp <= t2:
                mv1, mv2 = data[i]['mv'], data[i + 1]['mv']
                return mv1 + (temp - t1) * (mv2 - mv1) / (t2 - t1)
        return None

    def mv_to_temp(self, mv: float) -> Optional[float]:
        """热电势转换为温度"""
        range_data = self.get_current_range()
        if not range_data['mv_min'] <= mv <= range_data['mv_max']:
            raise ValueError(
                f"热电势超出范围 ({range_data['mv_min']}mV ~ {range_data['mv_max']}mV)"
            )
        
        data = self.get_current_data()
        for i in range(len(data) - 1):
            mv1, mv2 = data[i]['mv'], data[i + 1]['mv']
            if mv1 <= mv <= mv2:
                t1, t2 = data[i]['temp'], data[i + 1]['temp']
                return t1 + (mv - mv1) * (t2 - t1) / (mv2 - mv1)
        return None

class ThermocoupleApp:
    def __init__(self):
        self.converter = KTypeConverter()
        self.window = tk.Tk()
        self.current_type = tk.StringVar(value="K")
        self.setup_ui()
        self.setup_style()

    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', 
                       font=('微软雅黑', 10),
                       padding=5,
                       background='#f0f0f0')
        style.configure('TEntry',
                       padding=5,
                       font=('Consolas', 10))
        style.configure('TButton',
                       padding=5,
                       font=('微软雅黑', 10))
        
        # 结果标签特殊样式
        style.configure('Result.TLabel',
                       font=('微软雅黑', 12, 'bold'),
                       foreground='#2E7D32',
                       padding=10)

    def setup_ui(self):
        """创建用户界面"""
        self.window.title("热电偶转换器")
        self.window.geometry("500x600")  # 增加窗口尺寸
        self.window.configure(bg='#f0f0f0')
        self.window.minsize(500, 600)  # 设置最小窗口尺寸
        
        # 主容器使用垂直方向的填充
        main_container = ttk.Frame(self.window)
        main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        notebook = ttk.Notebook(main_container)
        notebook.pack(expand=True, fill='both')
        
        # 创建温度->热电势选项卡
        temp_frame = self.create_temp_to_mv_tab(notebook)
        notebook.add(temp_frame, text=' 温度→热电势 ', padding=10)
        
        # 创建热电势->温度选项卡
        mv_frame = self.create_mv_to_temp_tab(notebook)
        notebook.add(mv_frame, text=' 热电势→温度 ', padding=10)
        
        # 添加版权信息
        footer = ttk.Label(self.window,
                          text="热电偶温度-热电势转换器 © 2024",
                          font=('微软雅黑', 8),
                          foreground='#666666')
        footer.pack(side='bottom', pady=10)

    def create_type_selector(self, parent):
        """创建热电偶类型选择器"""
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="热电偶类型:").pack(side='left', padx=5)
        
        type_combo = ttk.Combobox(
            frame, 
            textvariable=self.current_type,
            values=["K", "E", "S"],
            width=10,
            state='readonly'
        )
        type_combo.pack(side='left', padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_changed)
        
        return frame

    def on_type_changed(self, event):
        """热电偶类型改变时的处理"""
        self.converter.set_type(self.current_type.get())
        self.update_range_info()

    def update_range_info(self):
        """更新范围信息"""
        range_data = self.converter.get_current_range()
        temp_range = f"温度范围: {range_data['temp_min']}°C ~ {range_data['temp_max']}°C"
        mv_range = f"热电势范围: {range_data['mv_min']}mV ~ {range_data['mv_max']}mV"
        
        if hasattr(self, 'temp_range_label'):
            self.temp_range_label.config(text=temp_range)
        if hasattr(self, 'mv_range_label'):
            self.mv_range_label.config(text=mv_range)

    def create_temp_to_mv_tab(self, parent):
        """创建温度转换标签页"""
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        
        # 使用空白标签增加垂直间距，改进 pady
        ttk.Label(frame, text="").grid(row=0, pady=5)
        
        # 添加类型选择器
        type_frame = self.create_type_selector(frame)
        type_frame.grid(row=1, column=0, pady=15)
        
        # 添加范围信息
        range_data = self.converter.get_current_range()
        self.temp_range_label = ttk.Label(
            frame,
            text=f"温度范围: {range_data['temp_min']}°C ~ {range_data['temp_max']}°C"
        )
        self.temp_range_label.grid(row=2, column=0, pady=10)
        
        # 添加说明文字
        desc = ttk.Label(frame,
                        text="请输入温度:",
                        wraplength=400)
        desc.grid(row=3, column=0, pady=10)
        
        # 输入框容器
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=4, column=0, pady=15)
        
        ttk.Label(input_frame, text="温度(°C):").pack(side='left')
        self.temp_entry = ttk.Entry(input_frame, width=20)  # 增加输入框宽度
        self.temp_entry.pack(side='left', padx=10)
        
        # 计算按钮
        btn = ttk.Button(frame,
                        text="计算热电势",
                        command=self.calculate_mv,
                        width=20)  # 增加按钮宽度
        btn.grid(row=5, column=0, pady=20)
        
        # 结果显示
        self.mv_result = ttk.Label(frame,
                                 text="等待输入...",
                                 style='Result.TLabel')
        self.mv_result.grid(row=6, column=0, pady=15)
        
        return frame

    def create_mv_to_temp_tab(self, parent):
        """创建热电势转换标签页"""
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        
        # 使用空白标签增加垂直间距，改进 pady
        ttk.Label(frame, text="").grid(row=0, pady=5)
        
        # 添加类型选择器
        type_frame = self.create_type_selector(frame)
        type_frame.grid(row=1, column=0, pady=15)
        
        # 添加范围信息
        range_data = self.converter.get_current_range()
        self.mv_range_label = ttk.Label(
            frame,
            text=f"热电势范围: {range_data['mv_min']}mV ~ {range_data['mv_max']}mV"
        )
        self.mv_range_label.grid(row=2, column=0, pady=10)
        
        desc = ttk.Label(frame,
                        text="请输入热电势:",
                        wraplength=400)
        desc.grid(row=3, column=0, pady=10)
        
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=4, column=0, pady=15)
        
        ttk.Label(input_frame, text="热电势(mV):").pack(side='left')
        self.mv_entry = ttk.Entry(input_frame, width=20)  # 增加输入框宽度
        self.mv_entry.pack(side='left', padx=10)
        
        btn = ttk.Button(frame,
                        text="计算温度",
                        command=self.calculate_temp,
                        width=20)  # 增加按钮宽度
        btn.grid(row=5, column=0, pady=20)
        
        self.temp_result = ttk.Label(frame,
                               text="等待输入...",
                               style='Result.TLabel')
        self.temp_result.grid(row=6, column=0, pady=15)
        
        return frame

    def center_window(self):
        """使窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def calculate_mv(self):
        """计算热电势"""
        try:
            temp = float(self.temp_entry.get())
            mv = self.converter.temp_to_mv(temp)
            if mv is not None:
                self.mv_result.config(
                    text=f"{self.current_type.get()}型热电偶\n"
                         f"温度: {temp:.1f}°C\n"
                         f"热电势: {mv:.3f}mV"
                )
            else:
                self.mv_result.config(text="计算错误")
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def calculate_temp(self):
        """计算温度"""
        try:
            mv = float(self.mv_entry.get())
            temp = self.converter.mv_to_temp(mv)
            if temp is not None:
                self.temp_result.config(text=f"温度: {temp:.1f} °C")
            else:
                self.temp_result.config(text="计算错误")
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def run(self):
        """运行应用"""
        self.window.mainloop()

if __name__ == '__main__':
    try:
        app = ThermocoupleApp()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")