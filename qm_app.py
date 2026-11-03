#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, font
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_qimen_image import get_all_gz, get_bureau_info
from qimen_engine_v2 import solve as solve_qimen

class QiMenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("奇门遁甲排盘")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # 设置背景颜色
        self.root.configure(bg="#F5E6D3")  # 米色背景
        
        # 设置字体
        self.font_large = font.Font(family="SimHei", size=12, weight="bold")
        self.font_normal = font.Font(family="SimHei", size=10)
        self.font_small = font.Font(family="SimHei", size=9)
        
        # 主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置样式
        self.setup_styles()
        
        # 日期时间输入区域
        self.create_time_input()
        
        # 创建顶部选项卡
        self.create_top_tabs()
        
        # 创建排盘结果显示区域
        self.create_pan_display()
        
        # 创建底部按钮
        self.create_bottom_buttons()
        
        # 初始化排盘
        # 延迟初始化，避免网络请求失败导致应用崩溃
        self.root.after(100, self.update_pan)
    
    def setup_styles(self):
        """配置样式"""
        style = ttk.Style()
        
        # 按钮样式
        style.configure("Tab.TButton", 
                       font=self.font_normal, 
                       background="#D4B996",  # 棕色背景
                       foreground="#333333",  # 深色文字
                       relief=tk.RAISED,
                       padding=5)
        
        # 标签框架样式
        style.configure("TLabelFrame", 
                       font=self.font_large,
                       background="#F5E6D3",
                       foreground="#333333")
        
        # 标签样式
        style.configure("TLabel", 
                       font=self.font_normal,
                       background="#F5E6D3",
                       foreground="#333333")
        
        # 输入框样式
        style.configure("TEntry", 
                       font=self.font_normal,
                       fieldbackground="#FFFFFF",
                       foreground="#333333")
    
    def create_top_tabs(self):
        """创建顶部选项卡"""
        tab_frame = ttk.Frame(self.main_frame, style="TFrame")
        tab_frame.pack(fill=tk.X, pady=5)
        
        # 按钮样式
        style = ttk.Style()
        style.configure("Tab.TButton", 
                       font=self.font_normal, 
                       background="#D4B996",  # 棕色背景
                       foreground="#333333",  # 深色文字
                       relief=tk.RAISED,
                       padding=5)
        
        self.zp_button = ttk.Button(tab_frame, text="转盘", style="Tab.TButton", width=10, command=lambda: self.set_tab("zp"))
        self.zp_button.pack(side=tk.LEFT, padx=5)
        
        self.cb_button = ttk.Button(tab_frame, text="拆补", style="Tab.TButton", width=10, command=lambda: self.set_tab("cb"))
        self.cb_button.pack(side=tk.LEFT, padx=5)
        
        self.sj_button = ttk.Button(tab_frame, text="时家", style="Tab.TButton", width=10, command=lambda: self.set_tab("sj"))
        self.sj_button.pack(side=tk.LEFT, padx=5)
        
        # 默认选中转盘
        self.zp_button.state(["pressed"])
        # 不再需要设置pan.PARAMS，使用自主排盘算法
    
    def set_tab(self, tab_type):
        """设置选中的选项卡"""
        # 重置所有按钮样式
        for btn in [self.zp_button, self.cb_button, self.sj_button]:
            btn.state(["!pressed"])
        
        # 设置选中的按钮
        if tab_type == "zp":
            self.zp_button.state(["pressed"])
        elif tab_type == "cb":
            self.cb_button.state(["pressed"])
        elif tab_type == "sj":
            self.sj_button.state(["pressed"])
        
        # 更新排盘
        self.update_pan()
    
    def create_time_input(self):
        """创建日期时间输入区域"""
        time_frame = ttk.LabelFrame(self.main_frame, text="时间设置", padding="10")
        time_frame.pack(fill=tk.X, pady=5)
        
        # 当前时间
        now = datetime.datetime.now()
        
        # 年份输入
        ttk.Label(time_frame, text="年:", font=self.font_normal).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.year_var = tk.StringVar(value=str(now.year))
        year_entry = ttk.Entry(time_frame, textvariable=self.year_var, width=6)
        year_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 月份输入
        ttk.Label(time_frame, text="月:", font=self.font_normal).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.month_var = tk.StringVar(value=str(now.month))
        month_entry = ttk.Entry(time_frame, textvariable=self.month_var, width=4)
        month_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 日期输入
        ttk.Label(time_frame, text="日:", font=self.font_normal).grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.day_var = tk.StringVar(value=str(now.day))
        day_entry = ttk.Entry(time_frame, textvariable=self.day_var, width=4)
        day_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 小时输入
        ttk.Label(time_frame, text="时:", font=self.font_normal).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hour_var = tk.StringVar(value=str(now.hour))
        hour_entry = ttk.Entry(time_frame, textvariable=self.hour_var, width=4)
        hour_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 分钟输入
        ttk.Label(time_frame, text="分:", font=self.font_normal).grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.minute_var = tk.StringVar(value=str(now.minute))
        minute_entry = ttk.Entry(time_frame, textvariable=self.minute_var, width=4)
        minute_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # 排盘按钮
        style = ttk.Style()
        style.configure("Pan.TButton", 
                       font=self.font_normal, 
                       background="#D4B996",  # 棕色背景
                       foreground="#333333",  # 深色文字
                       relief=tk.RAISED,
                       padding=5)
        
        pan_button = ttk.Button(time_frame, text="排盘", style="Pan.TButton", command=self.update_pan)
        pan_button.grid(row=1, column=4, columnspan=2, padx=5, pady=5)
    
    def create_pan_display(self):
        """创建排盘结果显示区域"""
        pan_frame = ttk.LabelFrame(self.main_frame, text="排盘结果", padding="10")
        pan_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 信息显示
        self.info_text = tk.Text(pan_frame, 
                                height=6, 
                                font=self.font_normal, 
                                wrap=tk.WORD,
                                bg="#FFFFFF",  # 白色背景
                                fg="#333333",  # 深色文字
                                relief=tk.SUNKEN,
                                borderwidth=2)
        self.info_text.pack(fill=tk.X, pady=5)
        self.info_text.config(state=tk.DISABLED)
        
        # 九宫格显示
        grid_frame = ttk.Frame(pan_frame, borderwidth=2, relief=tk.SUNKEN)
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 配置网格权重
        for i in range(3):
            grid_frame.grid_rowconfigure(i, weight=1)
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # 创建九宫格
        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                cell = tk.Text(grid_frame, 
                              height=4, 
                              width=12, 
                              font=self.font_small, 
                              wrap=tk.WORD, 
                              borderwidth=1, 
                              relief=tk.SOLID,
                              bg="#FFFFFF",  # 白色背景
                              fg="#333333")  # 深色文字
                cell.grid(row=i, column=j, sticky=tk.NSEW, padx=1, pady=1)
                cell.config(state=tk.DISABLED)
                row.append(cell)
            self.cells.append(row)
        
        # 格局显示
        self.geju_text = tk.Text(pan_frame, height=4, font=self.font_normal, wrap=tk.WORD)
        self.geju_text.pack(fill=tk.X, pady=5)
        self.geju_text.config(state=tk.DISABLED)
    
    def create_bottom_buttons(self):
        """创建底部选项按钮"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 按钮样式
        style = ttk.Style()
        style.configure("Bottom.TButton", font=self.font_normal)
        
        self.now_button = ttk.Button(button_frame, text="此时", style="Bottom.TButton", width=10, command=self.set_current_time)
        self.now_button.pack(side=tk.LEFT, padx=5)
        
        self.select_time_button = ttk.Button(button_frame, text="选时", style="Bottom.TButton", width=10, command=self.select_time)
        self.select_time_button.pack(side=tk.LEFT, padx=5)
        
        self.select_ju_button = ttk.Button(button_frame, text="选局", style="Bottom.TButton", width=10, command=self.select_ju)
        self.select_ju_button.pack(side=tk.LEFT, padx=5)
        
        self.options_button = ttk.Button(button_frame, text="选项", style="Bottom.TButton", width=10, command=self.show_options)
        self.options_button.pack(side=tk.LEFT, padx=5)
    
    def set_current_time(self):
        """设置为当前时间"""
        now = datetime.datetime.now()
        self.year_var.set(str(now.year))
        self.month_var.set(str(now.month))
        self.day_var.set(str(now.day))
        self.hour_var.set(str(now.hour))
        self.minute_var.set(str(now.minute))
        self.update_pan()
    
    def select_time(self):
        """选时功能"""
        # 简单实现，实际应用中可以添加更复杂的选时逻辑
        print("选时功能")
    
    def select_ju(self):
        """选局功能"""
        # 简单实现，实际应用中可以添加更复杂的选局逻辑
        print("选局功能")
    
    def show_options(self):
        """显示选项"""
        # 简单实现，实际应用中可以添加更多选项
        print("选项功能")
    
    def update_pan(self):
        """更新排盘结果（使用 qimen_engine_v2 引擎）"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
        except ValueError:
            self.show_error("请输入有效的日期时间数字")
            return

        try:
            # ── 构造 datetime 对象并计算四柱/节气/局数 ──
            dt = datetime.datetime(year, month, day, hour, minute)
            year_gz, month_gz, day_gz, hour_gz = get_all_gz(dt)
            jieqi_name, dun, bureau_num, yuan = get_bureau_info(dt)

            # ── 调用 qimen_engine_v2 排盘 ──
            result = solve_qimen(year_gz, month_gz, day_gz, hour_gz,
                                 jieqi_name, dun, bureau_num)
            ci = result['chart_info']

            # ── 更新顶部信息显示 ──
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"公历时间：{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}\n")
            self.info_text.insert(tk.END, f"{ci['time']}\n")
            self.info_text.insert(tk.END, f"节气：{jieqi_name}（{yuan}）  {dun}遁{bureau_num}局\n")
            self.info_text.insert(tk.END, f"值符：{ci['zhi_fu_star']}落{ci['zhi_fu_heaven_pos']}宫  "
                                           f"值使：{ci['zhi_shi_door']}落{ci['zhi_shi_pos']}宫\n")
            kong_str = ''.join(ci.get('kong_pair', ('', '')))
            self.info_text.insert(tk.END, f"旬空：{kong_str}  驿马：{ci.get('ma_zhi', '')}({ci.get('ma_palace', '')}宫)\n")
            self.info_text.config(state=tk.DISABLED)

            # ── 更新九宫格（洛书布局：4 9 2 / 3 5 7 / 8 1 6）──
            PALACE_TO_RC = {
                4: (0, 0), 9: (0, 1), 2: (0, 2),
                3: (1, 0), 5: (1, 1), 7: (1, 2),
                8: (2, 0), 1: (2, 1), 6: (2, 2),
            }

            pg = result['palace_gods']       # 天盘八神
            hs = result['hv_stars']          # 天盘星
            hv = result['hv_stems']          # 天盘干
            pd = result['palace_doors']      # 八门
            dp = result['di_pan']            # 地盘干

            grid_data = [['', '', ''], ['', '', ''], ['', '', '']]
            for palace in range(1, 10):
                rc = PALACE_TO_RC.get(palace)
                if rc is None:
                    continue
                r, c = rc

                god_name  = pg.get(palace, '')
                star_name = hs.get(palace, '')
                hv_stem   = hv.get(palace, '')
                door_name = pd.get(palace, '')
                dp_stem   = dp.get(palace, '')

                content = f"{god_name}\n"
                content += f"{hv_stem} {star_name}\n"
                content += f"{dp_stem} {door_name}"
                grid_data[r][c] = content

            for r in range(3):
                for c in range(3):
                    self.cells[r][c].config(state=tk.NORMAL)
                    self.cells[r][c].delete(1.0, tk.END)
                    self.cells[r][c].insert(tk.END, grid_data[r][c])
                    self.cells[r][c].config(state=tk.DISABLED)

            # ── 更新格局信息 ──
            self.geju_text.config(state=tk.NORMAL)
            self.geju_text.delete(1.0, tk.END)
            self.geju_text.insert(tk.END, f"格局：\n")
            self.geju_text.insert(tk.END, f"旬首干：{ci['xun_shou_gan']}（值符）  ")
            self.geju_text.insert(tk.END, f"驿马：{ci.get('ma_zhi', '')}宫({ci.get('ma_palace', '')})\n")
            kong_palaces = ci.get('kong_palaces', [])
            self.geju_text.insert(tk.END, f"空亡宫：{'、'.join(str(p)+'宫' for p in kong_palaces) if kong_palaces else '无'}\n")
            self.geju_text.config(state=tk.DISABLED)

        except Exception as e:
            self.show_error(f"排盘失败：{str(e)}")

    def show_error(self, msg):
        """显示错误信息"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"{msg}\n")
        self.info_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = QiMenApp(root)
    root.mainloop()