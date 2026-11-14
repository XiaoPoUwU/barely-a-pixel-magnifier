import ctypes
import time
#import pyautogui
import tkinter as tk
from PIL import Image, ImageGrab, ImageTk


"""

左键    ·   拖动

右键    -   打开菜单

-       -   减小截图范围

=	        增大截图范围

空格	-   暂停画面

双击	-   复制「物理坐标 / 逻辑坐标 / HEX / RGB」到剪贴板



^
[*聚焦窗口时有效]


"""

# 窗口 root

# 屏幕 screen

# 缩放 scale

# 屏幕  Screen

# 像素  Pixel

# 放大  Zoom

# 坐标  Coordinate

# 显示  Display

# 键/工具  Tool

# PixelCoord	像素坐标

#last       上一个






#声明 DPI 感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # 每显示器 DPI 感知
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()         # 旧系统备用

# 定义 POINT 结构体对应 Win32 里的坐标点
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class UwU:


    #初始化
    def __init__(self):

        # print("1")

        # 是否启用终端输出
        self.ison_cmd = False
        
        #信息面板颜色
        self.text_color = "#55E2C9"


        self.grid_color = '#333333'      # 普通格子线颜色

        self.grid_color_major = '#707070'    # 每隔 unit 格的主线颜色

        self.center_color = "#FFFDFD"        # 中心像素框颜色






        # 设置透明色
        self.transparent_color = "#373737"
        

        self.base_img = None     # 缓存截图



        # 初始放大倍数
        self.win_scale = 1

        self.img_scale = 1


        # 初始截图边长
        #self.img_c = 15
        #
        
        self.n = 5          # [必须是奇数]

        self.img_c = (3*self.n)*self.win_scale              # [必须是5^n (n = 奇数)]

        self.mouse = None
        self.img = None
        self.mouse_last = None
        self.screen_x = 0
        self.screen_y = 0
        self.img_color = (0, 0, 0)
        self.img_x = 0
        self.img_y = 0
        self.hex_color = None
        self.mouse_old = POINT()
        # self.mouse_old.x = 0
        # self.mouse_old.y = 0

        self.ison_Pause = False     # 是否有被暂停[空格]

        # 主窗口相关


        self.win = tk.Tk()       #创建主窗口

        self.win.geometry(f"{int(375 * self.win_scale)}x{int(375 * self.win_scale)}")         # 初始尺寸

        self.win.overrideredirect(True)                   # 无边框

        self.win.attributes('-topmost', True)          # 置顶


        self.canvas = tk.Canvas(self.win, highlightthickness=0, bd=0)    #创建画布
        self.canvas.pack(fill='both', expand=True)       #显示图像

        # self.win.withdraw()      # 隐藏主窗口



        # Info Panel     信息面板


        # 面板信息显示相关


        self.Info_Panel = tk.Toplevel(self.win)     # 创建面板窗口

        self.Info_Panel.geometry("375x100")   # 宽x高+x坐标+y坐标

        self.Info_Panel.overrideredirect(True)       #无边框
        self.Info_Panel.attributes('-topmost', True) # 置顶
    
        # self.Info_Panel.attributes('-alpha', 1)    #透明
        #self.Info_Panel.update_idletasks()       #刷新窗口
        self.Info_Panel.config(bg=self.transparent_color)   # 设置窗口背景颜色
        self.Info_Panel.wm_attributes("-transparentcolor", self.transparent_color)  #应用透明色


        #创建画布
        self.info_canvas = tk.Canvas(self.Info_Panel,
                                bg=self.transparent_color,          # 面板底色
                                highlightthickness=0,
                                bd=0)
        self.info_canvas.pack(fill='both', expand=True)

        # 边框
        self.info_canvas.create_rectangle(0,0,375,100,
                                    outline=self.text_color, # 边框颜色
                                    width=10,           # 边框粗细
                                    tags="panel_border")
        # #计算窗口相关函数调用
        # self.win_calculate()



        # 按键绑定相关


        self.win.bind("<ButtonPress-1>", self.on_press)   # 左键按下时[记录偏移]
        self.win.bind("<B1-Motion>", self.mouse_drag)     # 左键拖动时[更新窗口位置]

        self.canvas.bind("<Motion>", self.on_motion)    # 鼠标在窗口内时

        self.win.bind("<minus>", self.on_minus)   # 减号键

        #self.win.bind("<plus>", self.on_plus)     # 等号键
        
        self.win.bind("<equal>", self.on_plus)    # 加号键

    
        self.win.bind("<space>", self.on_space)   # 绑定空格键

        self.canvas.bind("<Double-Button-1>", self.copy_info)     # 绑定双击事件

        # self.win.bind("<MouseWheel>", self.on_mousewheel)#绑定鼠标滚轮




        self.win.bind("<Button-3>", self._menu)   # 右键绑定菜单




        #菜单函数相关
        self.menu_Info_Panel_switch_var = tk.BooleanVar(value=True)   # 默认勾选
        self.menu_wireframe_switch_var = tk.BooleanVar(value=True)
        self.menu_center_wireframe_switch_var = tk.BooleanVar(value=True)
        self.ison_Info_Panel = True
        self.ison_wireframe = True
        self.ison_center_wireframe = True



        # 启动！
        self._refresh()
        #初始化绘制窗口线框
        if self.ison_wireframe == True:
            # print("2")
            
            self.win.after(150,self.screenshot_calculate)    #截图计算相关
            self.win.after(150,self.wireframe)      # 绘制窗口线框
            

        # self.win.after(1000, self.show_win)   # 1000 ms = 1 s 后显示主窗口
        pass





    #获取鼠标坐标位置[物理像素]
    def get_cursor_pos(self):

        pt = POINT()# 调用 API
        
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        
        return pt   #返回坐标

    
    #获取电脑屏幕缩放[逻辑]
    def get_dpi_scale(self):
        
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0



    # calculate     计算
    # win_area	    窗口区域
    

    #计算窗口相关
    def win_calculate(self):

        
        # 窗口宽
        self.win_w = self.win.winfo_width()

        # 窗口高
        self.win_h = self.win.winfo_height()
        
        # 窗口左上角 x 坐标
        self.win_left = self.win.winfo_rootx()

        # 窗口左上角 y 坐标
        self.win_top = self.win.winfo_rooty()

        # 窗口右下角 x 坐标
        self.win_right = self.win_left + self.win.winfo_width()

        # 窗口右下角 y 坐标
        self.win_bottom = self.win_top + self.win.winfo_height()

        # 判断鼠标是否在窗口内
        self.ison_mouse_in_win = (self.mouse.x > self.win_left and self.mouse.x < self.win_right and self.mouse.y > self.win_top and self.mouse.y < self.win_bottom)

        # 判断鼠标是否在之前的位置
        self.ison_mouse_in_mouse_old = (self.mouse_old.x != self.mouse.x or self.mouse_old.y != self.mouse.y)


        
    #截图计算相关
    def screenshot_calculate(self):
        # print("6")


        self.img_c = (3*self.n)*self.win_scale

        self.half = self.img_c // 2       # 中心偏移 默认= 7


        #截图左上角 = 光标像素 - half
        self.img_x = int(self.mouse.x) - self.half
        self.img_y = int(self.mouse.y) - self.half
        self.img_dx = self.img_x + self.img_c
        self.img_dy = self.img_y + self.img_c
        # 截图范围
        self.img_w = self.img_c
        self.img_h = self.img_c

        #放大倍数 x 截图原尺寸 = 窗口尺寸

        self.img_scale = self.win_w / self.img_c

        # self.wireframe()

        if self.img_scale <= 0:
            self.img_scale = 25



        pass


    # 截图屏幕显示
    def screenshot_screen_display(self):
        # print(self.mouse_old.x)

        #screenshot     截图/屏幕截图
        #screen display	    屏幕显示

        
        # self.half = self.img_c // 2       # 中心偏移 = 7


        # print(self.win_w)


        # if self.img_win_h != self.win_h:


        #     self.win.geometry(f"{self.img_win_w}x{self.img_win_h}")         # 应用尺寸位置

        #     #print(self.img_win_w)
            
        #     #print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        #     pass
        # else:
        #     pass
        #     #print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")


        # 截图
    

        # print("8")
        # #截图左上角 = 光标像素 - half
        # self.img_x = int(self.mouse.x) - self.half
        # self.img_y = int(self.mouse.y) - self.half
        # self.img_dx = self.img_x + self.img_c
        # self.img_dy = self.img_y + self.img_c
        # # 截图范围
        # self.img_w = self.img_c
        # self.img_h = self.img_c

        # #放大倍数 x 截图原尺寸 = 窗口尺寸

        # self.img_scale = self.win_w / self.img_c

        # 计算截图相关参数
        self.screenshot_calculate()
        # print(self.img_scale)



        # self.img_win_w = self.img_w * self.img_scale   # 默认计算结果为 375
        # self.img_win_h = self.img_h * self.img_scale

        # 截取指定区域
        self.base_img = ImageGrab.grab(bbox=(self.img_x, self.img_y,
                                            self.img_dx, self.img_dy
                                            ))

        #显示截图
        self._screen_display()


    #屏幕显示截图
    def _screen_display(self):
    
        # 图片等比放大或缩小
        self.img = self.base_img.resize((int(self.base_img.width * self.img_scale),
                                        int(self.base_img.height * self.img_scale)),
                                        Image.NEAREST      # 最近邻插值[防止图片模糊]
                                        )


        # print("图片w:",self.img.width)
        # print("窗口w:",self.win_w)
        photo = ImageTk.PhotoImage(self.img)

        # 删除画布
        self.canvas.delete("screenshot")
        # 显示图片
        self.canvas.create_image(0, 0, image=photo, anchor='nw', tags="screenshot")
        
        #将网格提升到最上面的图层
        self.canvas.tag_raise("wireframe")
        self.canvas.tag_raise("win_border")
        self.canvas.tag_raise("center_wireframe")   # 中心框
        # 取图片中心像素
        self.img_color = self.base_img.getpixel((self.half, self.half))


        # 防回收
        self.canvas.image = photo




    #绘制窗口线框
    def wireframe(self):
        # print("10")


        self.canvas.delete("wireframe")      #清除网格

        # self.grid_color = '#333333'      # 普通格子线颜色

        # self.grid_color_major = '#707070'    # 每隔 unit 格的主线颜色

        # self.center_color = "#8F4040"        # 中心像素框颜色

        

        #     #wireframe	线框
        #     "#FFFFFF"

        self.unit = int(self.img_c // 3)        # 每 unit 格主线


        # 普通格子绘画
        for i in range(int(self.img_c) + 1):
            dx = i * self.img_scale


            self.canvas.create_line(dx, 0, dx, int(self.img_c) * self.img_scale,
                                    fill=self.grid_color,
                                    tags="wireframe"        # 标签
                                    )

            self.canvas.create_line(0, dx, int(self.img_c) * self.img_scale, dx,
                                    fill=self.grid_color,
                                    tags="wireframe"        # 标签
                                    )

        # 每 unit 格主线
        for i in range(1, int(self.img_c) // self.unit + 1):
            dy = i * self.unit * self.img_scale


            
            self.canvas.create_line(dy, 0, dy, int(self.img_c) * self.img_scale,
                                    fill=self.grid_color_major,
                                    width=2,
                                    tags="wireframe"
                                    )
            self.canvas.create_line(0, dy, int(self.img_c) * self.img_scale, dy,
                                    fill=self.grid_color_major,
                                    width=2,
                                    tags="wireframe"
                                    )

                
        # 绘制中心像素框
        self.center_wireframe()

    # 绘制中心像素框
    def center_wireframe(self):

        self.canvas.delete("center_wireframe")      #清除网格

        center = int(self.img_c / 2) * self.img_scale

        self.canvas.create_rectangle(center, center,
                                     center + self.img_scale, center + self.img_scale,
                                     outline=self.center_color,
                                     width=3,
                                     tags="center_wireframe"
                                     )

        #绘制窗口边框
        
        self.canvas.delete("win_border")      #清除网格
        # 框

        self.canvas.create_rectangle(0, 0,
                                     int(self.win_w), int(self.win_h),
                                     outline=self.center_color,
                                     width=10,
                                     tags="win_border"        # 标签
                                     )

                



    #刷新循环函数
    def _refresh(self,t=60,topmost = False):
        # print("11")
        """
        t      #刷新时间
        """
        if topmost == True:
            self.Info_Panel.attributes('-topmost', True) # 置顶
            self.win.attributes('-topmost', True) # 置顶

        self.mouse = self.get_cursor_pos()    #获取鼠标位置[物理像素]


        self.dpi_scale = self.get_dpi_scale()    #获取电脑屏幕缩放[逻辑]


        #计算窗口相关函数调用
        self.win_calculate()



        if self.ison_Pause == False:    # 如果没有按下空格时
            
            
            # if self.mouse_old.x != self.mouse.x or self.mouse_old.y != self.mouse.y:
            # 如果在窗口内
            if self.ison_mouse_in_win == True:

                # print("lllllllllllllllllll")
                pass
                # 如果鼠标不在上一个位置时时
            elif self.ison_mouse_in_mouse_old == True:
            
                
                # print("12")
                # # 截图屏幕并且显示
                self.screenshot_screen_display()


        self.mouse_old.x = self.mouse.x
        self.mouse_old.y = self.mouse.y

        # #绘制窗口线框
        # self.wireframe()

        # 如果鼠标不在上一个位置时时
        if self.ison_mouse_in_mouse_old == True:
            # 获取截图中间的颜色
            self._img_color()

            # print("wwwwwwwwwwwwwwwwwwwwwww")

            #刷新信息面板
            self._refresh_Info_Panel_txt()





        #cmd调试显示
        if self.ison_cmd == True:
            print("13")
            self.print_to_cmd()

        # 回调
        self.win.after(t,self._refresh)
        pass



    # 鼠标左键按下
    def on_press(self,e):
        # print("14")

        # 拖拽	drag    .v
        # 鼠标拖拽	mouse drag

        # win_left = win.winfo_rootx()    # 窗口左上角 x 坐标
        # win_top = win.winfo_rooty() # 窗口左上角 y 坐标




        self.drag_c_x = e.x_root - self.win_left
        self.drag_c_y = e.y_root - self.win_top

        #print("wwwwwwwwwwwwwwwwwwww")



    # 鼠标左键按下拖拽时
    def mouse_drag(self,e):

        #     print(c_y)
        #应用窗口位置
        self.win.geometry(f"+{e.x_root-self.drag_c_x}+{e.y_root-self.drag_c_y}")         # 位置
        # else:


        #刷新信息面板的位置
        self.Info_Panel.geometry(f"+{self.win.winfo_rootx()}+{self.win.winfo_rooty() + self.win.winfo_height() + 10}")         # 位置
        #self._refresh_Info_Panel_pos()
        #win.after(10, lambda: mouse_drag(c_x,c_y))

    #按下了空格时
    def on_space(self,e):
        # print("16")
  
        #Pause 暂停画面
        self.ison_Pause = not self.ison_Pause



        #print("按下了空格！")

        # canvas.delete("The_Chosen_Frame")




    # 按下"-"时
    def on_minus(self,e):
        # print("17")

        if self.ison_Pause == True:
            pass
        elif self.n > 2:

            self.n -= 2
            
            

            # 重新计算截图相关参数
            self.screenshot_calculate()
            
            # # 如果不在窗口内
            # if self.ison_mouse_in_win == True:
            #显示重新截图
            self.screenshot_screen_display()
            # 绘制中心像素框
            if self.ison_center_wireframe == False:
                self.canvas.delete("center_wireframe")      #清除网格
            else:
                self.center_wireframe()
            # 重新绘制网格
            if self.ison_wireframe == True:

                self.wireframe()

        # print("-")



    # 按下"+"时
    def on_plus(self,e):
        # print("20")
        if self.ison_Pause == True:
            pass
        elif self.n < 120:

            self.n += 2

            # 重新计算截图相关参数
            self.screenshot_calculate()
            #显示重新截图
            self.screenshot_screen_display()
            # 绘制中心像素框
            if self.ison_center_wireframe == False:
                self.canvas.delete("center_wireframe")      #清除网格
            else:
                self.center_wireframe()

            # 重新绘制网格
            if self.ison_wireframe == True:

                self.wireframe()
            # print("+")




    # def on_mousewheel(self,e):
    #     if e.delta > 0:

    #         self.win_scale += 0.1      # 向上滚放大

    #     else:
    #         self.win_scale  -= 0.1      # 向下滚缩小

    #     # 限制大小
    #     if self.win_scale < 0.5:
    #         self.win_scale = 0.5
    #     if self.win_scale > 1.5:
    #         self.win_scale = 1.5

    #     self.win.geometry(f"{int(375 * self.win_scale)}x{int(375 * self.win_scale)}") 
    #     # 重新计算截图相关参数
    #     self.screenshot_calculate()

    #     # 重新绘制网格
    #     self.wireframe()
    #     # # 按下滚轮时
    #     # ison_on_mousewheel = True
    #     # 截图屏幕并且显示
    #     self.screenshot_screen_display()
    #     # if  == False:
    #     #     ison_on_mousewheel = True
    #     # else:
    #     #     ison_on_mousewheel = False
    #     pass


    #双击时
    def copy_info(self, e):
        # print("23")

        if self.screen_x == 0:

            txt = "还没有初始化"
            pass
        else:
            txt = (f"物理坐标:{self.screen_x}, {self.screen_y}\n"
                    f"逻辑坐标:{int(self.screen_x / self.dpi_scale)}, {int(self.screen_y / self.dpi_scale)}\n"
                    f"十六进制颜色:[{self.hex_color}]\n"
                    f"R G B : ({self.img_color[0]}, {self.img_color[1]}, {self.img_color[2]})")
                
        self.win.clipboard_clear()

        self.win.clipboard_append(txt)

        self.win.update()
        print(f"已复制: {txt}")

    #菜单函数相关
    def _menu(self, e):
        # print("25")

        #   switch - 开关


        #置顶
            # ison_topmost = self.win.attributes('-topmost')

            # if ison_topmost == True:
            #     self.win.attributes("-topmost",False)
            # else:
            #     self.win.attributes("-topmost",True)
            
        #_菜单_信息面板_是否开启
        def _menu_Info_Panel_ison():
            # print("26")

            self.ison_Info_Panel = not self.ison_Info_Panel

            if self.ison_Info_Panel == False:

                self.Info_Panel.withdraw()
            else:
                self.Info_Panel.deiconify()
            pass



        def _menu_wireframe_ison():

            self.ison_wireframe = not self.ison_wireframe

            # print(self.ison_wireframe)
            if self.ison_wireframe == False:
                # print("29")
                self.canvas.delete("wireframe")      #清除网格
            else:
                self.wireframe()          # 重新绘制

            pass

        def _menu_center_wireframe_ison():
            

            self.ison_center_wireframe = not self.ison_center_wireframe

            # print(self.ison_wireframe)
            if self.ison_center_wireframe == False:
            
                self.canvas.delete("center_wireframe")      #清除网格
            else:

                # 绘制中心像素框
                self.center_wireframe()

            pass


    
        def _exit():
            # print("30")
            self.Info_Panel.destroy()  # 关闭信息面板
            self.win.destroy()         # 关闭主窗口

        menu = tk.Menu(self.win, tearoff=0)
        
        # menu.add_checkbutton(label="置顶",
        #                 variable=self.menu_topmost_switch_var,
        #                 command=_menu_topmost_ison)

        #网格显示

        menu.add_checkbutton(label="网格显示",
                        variable=self.menu_wireframe_switch_var,
                        command=_menu_wireframe_ison)


        #显示中心网格

        menu.add_checkbutton(label="中心网格显示",
                        variable=self.menu_center_wireframe_switch_var,
                        command=_menu_center_wireframe_ison)

        
        #面板信息显示

        menu.add_checkbutton(label="面板信息显示",
                        variable=self.menu_Info_Panel_switch_var,
                        command=_menu_Info_Panel_ison)



        menu.add_separator()    #分隔线

        menu.add_command(label="退出程序", command=_exit)  # 绑定退出函数
        
        menu.post(e.x_root, e.y_root)   #在鼠标处弹出
    


    #天选之格[划掉]
    def on_motion(self, e):
        # print("31")
        # 就决定是你了，上吧！天选之..格！?
        self.canvas.delete("The_Chosen_Frame")      # 清除之前的网格

        s = self.img_scale   # 局部变量
        dx = int(e.x / s) * s
        dy = int(e.y / s) * s
        self.canvas.create_rectangle(
            dx, dy, dx + s, dy + s,
            outline="#64C1FF",
            width=3,
            tags="The_Chosen_Frame",
        )


        j = int(dx / s)      # 列号
        i = int(dy / s)      # 行号


        # self.ison_cmd = False
        # print(self.img_x)


        self.screen_x = self.img_x + j
        self.screen_y = self.img_y + i

        # 取图片像素颜色
        self.img_color = self.base_img.getpixel((j,i))


        #print(f"蓝框像素物理坐标: ({screen_x}, {screen_y})")






    def _img_color(self):
        # print("32")

        
        # self.img_color = self.base_img.getpixel((self.half, self.half))   # 取图片中心像素
        #print(self.img_color)                   # (R, G, B)

        # RGB 转十六进制
        R = self.img_color[0]
        G = self.img_color[1]
        B = self.img_color[2]

        # print(R)

        # 十六进制颜色
        self.hex_color = "#{:02X}{:02X}{:02X}".format(R, G, B)
        #print(self.hex_color)   # #87CEEB


    #刷新信息面板相关
    def _refresh_Info_Panel_txt(self):
        # print("33")
        
        #删除文字
        self.info_canvas.delete("info_text")
        #清除画布
        self.info_canvas.delete("info_color")

        #显示文字

        # 鼠标不在窗口内时
        if self.ison_mouse_in_win == False:
        
            # 没有按下空格暂停时
            if self.ison_Pause == False:
                x = self.mouse.x
                y = self.mouse.y

            else:
                x = self.half + self.img_x
                y = self.half + self.img_y

            self.txt_1 = "[中心]物理坐标: ("
            self.info_text_id = self.info_canvas.create_text(10, 10,
                                                text=(f"{self.txt_1}{x}, {y})"),
                                                fill=self.text_color,
                                                font=("微软雅黑", 10, "bold"),
                                                anchor="nw",     # 左上角对齐
                                                tags="info_text")


            self.txt_1 = "[中心]逻辑坐标: ("
            self.info_text_id = self.info_canvas.create_text(10, 60,
                                                text=(f"{self.txt_1}{x / self.dpi_scale}, {y / self.dpi_scale})"),
                                                fill=self.text_color,
                                                font=("微软雅黑", 10, "bold"),
                                                anchor="nw",     # 左上角对齐
                                                tags="info_text")


            self.canvas.delete("The_Chosen_Frame")      # 清除之前的网格
        else:


            self.txt_1 = "[蓝框]物理坐标: ("
            self.info_text_id = self.info_canvas.create_text(10, 10,
                                                text=(f"{self.txt_1}{self.screen_x}, {self.screen_y})"),
                                                fill=self.text_color,
                                                font=("微软雅黑", 10, "bold"),
                                                anchor="nw",     # 左上角对齐
                                                tags="info_text")

            self.txt_1 = "[蓝框]逻辑坐标: ("
            self.info_text_id = self.info_canvas.create_text(10, 60,
                                                text=(f"{self.txt_1}{self.screen_x / self.dpi_scale}, {self.screen_y / self.dpi_scale})"),
                                                fill=self.text_color,
                                                font=("微软雅黑", 10, "bold"),
                                                anchor="nw",     # 左上角对齐
                                                tags="info_text")

        self.txt_1 = "[缩放]"
        self.info_text_id = self.info_canvas.create_text(10, 35,
                                            text=(f"{self.txt_1}{int(self.dpi_scale*100)}%"),
                                            fill=self.text_color,
                                            font=("微软雅黑", 10, "bold"),
                                            anchor="nw",     # 左上角对齐
                                            tags="info_text")

        Info_Panel_w = self.Info_Panel.winfo_width()
        Info_Panel_h = self.Info_Panel.winfo_height()
        c = 30
        dxy = 30
        # 选中颜色预览[矩形]
        self.info_canvas.create_rectangle(int(Info_Panel_w-dxy-c), int(Info_Panel_h-dxy-c),
                                          Info_Panel_w-c, Info_Panel_h-c,
                                          fill=self.hex_color,         # 填充颜色
                                          outline=self.text_color,        # 边框颜色
                                          width=3,                 # 边框粗细
                                          tags="info_color"
                                          )

        # 十六进制颜色
        self.hex_color


        c = 60
        # 显示文字
        self.info_text_id = self.info_canvas.create_text(int(Info_Panel_w-dxy-c-10), int(Info_Panel_h-dxy-c),
                                            text=(f"[{self.hex_color}]"),
                                            fill=self.text_color,
                                            font=("微软雅黑", 10, "bold"),
                                            anchor="nw",     # 左上角对齐
                                            tags="info_text")

    #应用面板窗口位置
    def _refresh_Info_Panel_pos(self):
        print("35")

        
        # 窗口左上角 x 坐标
        #self.Info_Panel_left = self.Info_Panel.winfo_rootx()
        #if self.Info_Panel_left != self.win_left:
        #    print("qsfty")
        self.Info_Panel.geometry(f"+{self.win_left}+{self.win_bottom+20}")         # 位置




    #cmd调试显示
    def print_to_cmd(self):
        # print("36")

        print("\n\n\n\n\n")
        print("鼠标坐标位置：（",self.mouse.x,",",self.mouse.y,")    [物理像素]")    #获取鼠标位置[物理像素]


        print("当前电脑屏幕缩放：",self.dpi_scale,"         [",int(self.dpi_scale*100),"%]")    #获取电脑屏幕缩放[逻辑]
        pass


    


    pass



if __name__ == "__main__":
    # print("0")
    
    UwU = UwU()     # 初始化



    UwU.win.mainloop()