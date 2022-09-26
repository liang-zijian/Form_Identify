# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from cgi import print_form
from gui.widgets.py_table_widget.py_table_widget import PyTableWidget
from . functions_main_window import *
import main_lib as lib
import os
import sys
import requests
import time
import tkinter as tk
from tkinter import filedialog
from aip import AipOcr
import cv2
import imutils as imutils
import numpy as np
import shutil
import requests
import base64
import pandas as pd

# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from qt_core import *

# IMPORT SETTINGS
# ///////////////////////////////////////////////////////////////
from gui.core.json_settings import Settings

# IMPORT THEME COLORS
# ///////////////////////////////////////////////////////////////
from gui.core.json_themes import Themes

# IMPORT PY ONE DARK WIDGETS
# ///////////////////////////////////////////////////////////////
from gui.widgets import *

# LOAD UI MAIN
# ///////////////////////////////////////////////////////////////
from . ui_main import *

# MAIN FUNCTIONS 
# ///////////////////////////////////////////////////////////////
from . functions_main_window import *

import tkinter as tk
from tkinter import filedialog

 # MAIN ALGORITHM
def main_start(img_r, token, app_id, api_key, secret_key):
        img = cv2.imread(img_r, 0)
        tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
        # 降噪处理
        gray = cv2.GaussianBlur(img, (5, 5), 0)
        cv2.imwrite('./filtered.png', gray, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

         # 边缘检测、二值化
        edged = cv2.Canny(gray, 10, 50)
        cv2.imwrite('./edged_bi.png', edged, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # 对表单进行轮廓绘制
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1] if imutils.is_cv3() else cnts[0]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
        screenCnt = None
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                break

        # 寻找表格轮廓
        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 2)

        img = lib.four_point_transform(img, approx)

        # 开闭运算降噪处理
        img = lib.remove_noise_and_smooth(img)
        cv2.imwrite('./pre_done.png', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        imgr_pre_done = './pre_done.png'

        #大方向检测旋转
        direct = lib.direction_detect(imgr_pre_done,token)
        img_spined = cv2.imread('./pre_done.png')
        for i in range(direct):
            img_spined = cv2.rotate(img_spined, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite('./spinned.png', img_spined, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        img = img_spined
        shutil.copyfile("./spinned.png", "./Pretreatment/aaa.png")

        # 定义常量
        APP_ID = app_id
        API_KEY = api_key
        SECRET_KEY = secret_key
        # 初始化AipFace对象
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        root = tk.Tk()
        root.withdraw()
        data_dir = './Pretreatment/'
        result_dir = './Pretreatment/'
        num = 0
        for name in os.listdir(data_dir):
            print ('{0} : {1} 正在处理：'.format(num+1, name.split('.')[0]))
            image = lib.get_file_content(os.path.join(data_dir, name))
            res = client.tableRecognitionAsync(image)
            print ("res:", res)
            if 'error_code' in res.keys():
                print ('Error! error_code: ', res['error_code'])
                sys.exit()
            # 获取识别ID号
            req_id = res['result'][0]['request_id']

            # OCR识别需要一定时间，设定10秒内每隔1秒查询一次
            for count in range(1, 20):
                # 通过ID获取表格文件XLS地址
                res = client.getTableRecognitionResult(req_id)
                if res['result']['ret_msg'] == '已完成':
                    # 云端处理完毕，成功获取表格文件下载地址，跳出循环
                    break
                else:
                    time.sleep(1)

            url = res['result']['result_data']
            xls_name = name.split('.')[0] + '.xls'
            lib.file_download(url, os.path.join(result_dir, xls_name))
            num += 1
            print ('{0} : {1} 下载完成。'.format(num, xls_name))
            time.sleep(1)

# Generate Table
def creat_table_show(obj):
        path_openfile_name = r"C:\Users\29255\Desktop\Form identification\Pretreatment\aaa.xls"
        ###===========读取表格，转换表格，===========================================
        if len(path_openfile_name) > 0:
            input_table = pd.read_excel(path_openfile_name)
        #print(input_table)
            input_table_rows = input_table.shape[0]
            input_table_colunms = input_table.shape[1]
        #print(input_table_rows)
        #print(input_table_colunms)
            input_table_header = input_table.columns.values.tolist()
        #print(input_table_header)
 
        ###===========读取表格，转换表格，============================================
        ###======================给tablewidget设置行列表头============================
 
            obj.res_table.setColumnCount(input_table_colunms)
            obj.res_table.setRowCount(input_table_rows)
            obj.res_table.setHorizontalHeaderLabels(input_table_header)
 
        ###======================给tablewidget设置行列表头============================
 
        ###================遍历表格每个元素，同时添加到tablewidget中========================
            for i in range(input_table_rows):
                input_table_rows_values = input_table.iloc[[i]]
                #print(input_table_rows_values)
                input_table_rows_values_array = np.array(input_table_rows_values)
                input_table_rows_values_list = input_table_rows_values_array.tolist()[0]
            #print(input_table_rows_values_list)
                for j in range(input_table_colunms):
                    input_table_items_list = input_table_rows_values_list[j]
                #print(input_table_items_list)
                # print(type(input_table_items_list))
 
        ###==============将遍历的元素添加到tablewidget中并显示=======================
 
                    input_table_items = str(input_table_items_list)
                    newItem = QTableWidgetItem(input_table_items) 
                    newItem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                    obj.res_table.setItem(i, j, newItem)  
 
# Reset folder

def del_file(path_data):
    for i in os.listdir(path_data) :# os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "\\" + i#当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:#os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)


# PY WINDOW
# ///////////////////////////////////////////////////////////////
class SetupMainWindow:
    def __init__(self):
        super().__init__()
        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

    # ADD LEFT MENUS
    # ///////////////////////////////////////////////////////////////
    add_left_menus = [
        {
            "btn_icon" : "icon_home.svg",
            "btn_id" : "btn_home",
            "btn_text" : "Home",
            "btn_tooltip" : "Home page",
            "show_top" : True,
            "is_active" : True
        },
        {
            "btn_icon" : "icon_settings.svg",
            "btn_id" : "btn_setting",
            "btn_text" : "Setting",
            "btn_tooltip" : "Show custom widgets",
            "show_top" : True,
            "is_active" : False
        },
        {
            "btn_icon" : "icon_info.svg",
            "btn_id" : "btn_info",
            "btn_text" : "Info",
            "btn_tooltip" : "Add users",
            "show_top" : True,
            "is_active" : False
        },
       
    ]

     # ADD TITLE BAR MENUS
    # ///////////////////////////////////////////////////////////////
    add_title_bar_menus = [
        {
            "btn_icon" : "icon_search.svg",
            "btn_id" : "btn_search",
            "btn_tooltip" : "Search",
            "is_active" : False
        },
        {
            "btn_icon" : "icon_settings.svg",
            "btn_id" : "btn_top_settings",
            "btn_tooltip" : "Top settings",
            "is_active" : False
        }
    ]

    # SETUP CUSTOM BTNs OF CUSTOM WIDGETS
    # Get sender() function when btn is clicked
    # ///////////////////////////////////////////////////////////////
    def setup_btns(self):
        if self.ui.title_bar.sender() != None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() != None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() != None:
            return self.ui.left_column.sender()

    # SETUP MAIN WINDOW WITH CUSTOM PARAMETERS
    # ///////////////////////////////////////////////////////////////
    def setup_gui(self):
        # APP TITLE
        # ///////////////////////////////////////////////////////////////
        self.setWindowTitle(self.settings["app_name"])
        
        # REMOVE TITLE BAR
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

        # ADD GRIPS
        # ///////////////////////////////////////////////////////////////
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)

        # LEFT MENUS / GET SIGNALS WHEN LEFT MENU BTN IS CLICKED / RELEASED
        # ///////////////////////////////////////////////////////////////
        # ADD MENUS
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)

        # SET SIGNALS
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)

        # TITLE BAR / ADD EXTRA BUTTONS
        # ///////////////////////////////////////////////////////////////
        # ADD MENUS
        self.ui.title_bar.add_menus(SetupMainWindow.add_title_bar_menus)

        # SET SIGNALS
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)

        # ADD Title
        if self.settings["custom_title_bar"]:
            self.ui.title_bar.set_title(self.settings["app_name"])
        else:
            self.ui.title_bar.set_title("Welcome to PyOneDark")

        # LEFT COLUMN SET SIGNALS
        # ///////////////////////////////////////////////////////////////
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)

        # SET INITIAL PAGE / SET LEFT AND RIGHT COLUMN MENUS
        # ///////////////////////////////////////////////////////////////
        MainFunctions.set_page(self, self.ui.load_pages.page_1)
        MainFunctions.set_left_column_menu(
            self,
            menu = self.ui.left_column.menus.menu_1,
            title = "Settings Left Column",
            icon_path = Functions.set_svg_icon("icon_settings.svg")
        )
        MainFunctions.set_right_column_menu(self, self.ui.right_column.menu_1)

        # ///////////////////////////////////////////////////////////////
        # EXAMPLE CUSTOM WIDGETS
        # Here are added the custom widgets to pages and columns that
        # were created using Qt Designer.
        # This is just an example and should be deleted when creating
        # your application.
        #
        # OBJECTS FOR LOAD PAGES, LEFT AND RIGHT COLUMNS
        # You can access objects inside Qt Designer projects using
        # the objects below:
        #
        # <OBJECTS>
        # LEFT COLUMN: self.ui.left_column.menus
        # RIGHT COLUMN: self.ui.right_column
        # LOAD PAGES: self.ui.load_pages
        # </OBJECTS>
        # ///////////////////////////////////////////////////////////////

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        themes = Themes()
        self.themes = themes.items

        # LEFT COLUMN
        # ///////////////////////////////////////////////////////////////

        # BTN 1
        self.left_btn_1 = PyPushButton(
            text="Btn 1",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.left_btn_1.setMaximumHeight(40)
        self.ui.left_column.menus.btn_1_layout.addWidget(self.left_btn_1)

        # BTN 2
        self.left_btn_2 = PyPushButton(
            text="Btn With Icon",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon = QIcon(Functions.set_svg_icon("icon_settings.svg"))
        self.left_btn_2.setIcon(self.icon)
        self.left_btn_2.setMaximumHeight(40)
        self.ui.left_column.menus.btn_2_layout.addWidget(self.left_btn_2)

        # BTN 3 - Default QPushButton
        self.left_btn_3 = QPushButton("Default QPushButton")
        self.left_btn_3.setMaximumHeight(40)
        self.ui.left_column.menus.btn_3_layout.addWidget(self.left_btn_3)

        # PAGES
        # ///////////////////////////////////////////////////////////////

        # PAGE 1 - ADD LOGO TO MAIN PAGE
        # self.logo_svg = QSvgWidget(Functions.set_svg_image("logo_home.svg"))
        # self.ui.load_pages.logo_layout.addWidget(self.logo_svg, Qt.AlignCenter, Qt.AlignCenter)

        # Main Button
        self.main_btn = PyPushButton(
            text = "Select Image File",
            radius=20,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["blue"],
            bg_color_hover=self.themes["app_color"]["blue"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.main_btn.setMinimumHeight(120)
        self.main_btn.setMinimumWidth (350)
        self.ui.load_pages.main_btn_layout.addWidget(self.main_btn, Qt.AlignCenter,Qt.AlignCenter)
        def main_btn_clicked():
            print("main button is pressed!")
            '''打开选择文件夹对话框'''
            root = tk.Tk()
            root.withdraw()
            img_dir = filedialog.askopenfilename(title='请选择图片')
            #print(img_dir)
            del_file(r'Pretreatment')
            self.main_btn.setText('Proccessing')
            '''开始'''
            if(self.line_edit1.text()==''):
                token='24.64d898b3d528534d6217fc1f0b96eb4b.2592000.1666103970.282335-27525133'
            else:
                token = self.line_edit1.text()
            if(self.line_edit3.text()==''):
                app_id='27525133'
            else:
                app_id=self.line_edit3.text()
            if(self.line_edit2.text()==''):
                app_key='CmR9rRV3dyScpO8HHiZ0u87m'
            else:
                app_key = self.line_edit2.text()
            if(self.line_edit4.text()==''):
                secret_key='RY9vVX2VLdgbKznMGStIpl8EaMyFXZPp'
            else:
                secret_key=self.line_edit4.text()
            main_start(img_dir,token,app_id,app_key,secret_key)
            creat_table_show(self)
            self.main_btn.setText('Select Image File')
        self.main_btn.clicked.connect(main_btn_clicked)


        # PAGE 2
        # PY LINE EDIT
        self.line_edit1 = PyLineEdit(
            text = "",
            place_holder_text = "Your_Access_token",
            radius = 8,
            border_size = 4,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.line_edit2 = PyLineEdit(
            text = "",
            place_holder_text = "Your_API_Key",
            radius = 8,
            border_size = 4,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.line_edit3 = PyLineEdit(
            text = "",
            place_holder_text = "Your_App_Id",
            radius = 8,
            border_size = 4,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.line_edit4 = PyLineEdit(
            text = "",
            place_holder_text = "Your_Secret_Key",
            radius = 8,
            border_size = 4,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["white"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_active = self.themes["app_color"]["dark_three"],
            context_color = self.themes["app_color"]["context_color"]
        )
        
        self.line_edit1.setMinimumHeight(50)
        self.ui.load_pages.row_4_layout.addWidget(self.line_edit1,Qt.AlignTop,Qt.AlignTop)
        self.line_edit2.setMinimumHeight(50)
        self.ui.load_pages.row_3_layout.addWidget(self.line_edit2,Qt.AlignTop,Qt.AlignTop)
        self.line_edit3.setMinimumHeight(50)
        self.ui.load_pages.row_2_layout.addWidget(self.line_edit3,Qt.AlignTop,Qt.AlignTop)
        self.line_edit4.setMinimumHeight(50)
        self.ui.load_pages.row_1_layout.addWidget(self.line_edit4,Qt.AlignTop,Qt.AlignTop)

        #PAGE 3
        # TABLE WIDGETS
        self.res_table = PyTableWidget(
            radius = 8,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["context_color"],
            bg_color = self.themes["app_color"]["bg_two"],
            header_horizontal_color = self.themes["app_color"]["dark_two"],
            header_vertical_color = self.themes["app_color"]["bg_three"],
            bottom_line_color = self.themes["app_color"]["bg_three"],
            grid_line_color = self.themes["app_color"]["bg_one"],
            scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
            scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
            context_color = self.themes["app_color"]["context_color"]
        )
        self.res_table.setColumnCount(3)
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.res_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.res_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.load_pages.table_layout.addWidget(self.res_table)

        '''
        # CIRCULAR PROGRESS 1
        # self.circular_progress_1 = PyCircularProgress(
        #     value = 80,
        #     progress_color = self.themes["app_color"]["context_color"],
        #     text_color = self.themes["app_color"]["text_title"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["dark_four"]
        # )
        # self.circular_progress_1.setFixedSize(200,200)

        # # CIRCULAR PROGRESS 2
        # self.circular_progress_2 = PyCircularProgress(
        #     value = 45,
        #     progress_width = 4,
        #     progress_color = self.themes["app_color"]["context_color"],
        #     text_color = self.themes["app_color"]["context_color"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["bg_three"]
        # )
        # self.circular_progress_2.setFixedSize(160,160)

        # # CIRCULAR PROGRESS 3
        # self.circular_progress_3 = PyCircularProgress(
        #     value = 75,
        #     progress_width = 2,
        #     progress_color = self.themes["app_color"]["pink"],
        #     text_color = self.themes["app_color"]["white"],
        #     font_size = 14,
        #     bg_color = self.themes["app_color"]["bg_three"]
        # )
        # self.circular_progress_3.setFixedSize(140,140)

        # # PY SLIDER 1
        # self.vertical_slider_1 = PySlider(
        #     margin=8,
        #     bg_size=10,
        #     bg_radius=5,
        #     handle_margin=-3,
        #     handle_size=16,
        #     handle_radius=8,
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_four"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_1.setMinimumHeight(100)

        # # PY SLIDER 2
        # self.vertical_slider_2 = PySlider(
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_2.setMinimumHeight(100)

        # # PY SLIDER 3
        # self.vertical_slider_3 = PySlider(
        #     margin=8,
        #     bg_size=10,
        #     bg_radius=5,
        #     handle_margin=-3,
        #     handle_size=16,
        #     handle_radius=8,
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_four"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_3.setOrientation(Qt.Horizontal)
        # self.vertical_slider_3.setMaximumWidth(200)

        # # PY SLIDER 4
        # self.vertical_slider_4 = PySlider(
        #     bg_color = self.themes["app_color"]["dark_three"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     handle_color = self.themes["app_color"]["context_color"],
        #     handle_color_hover = self.themes["app_color"]["context_hover"],
        #     handle_color_pressed = self.themes["app_color"]["context_pressed"]
        # )
        # self.vertical_slider_4.setOrientation(Qt.Horizontal)
        # self.vertical_slider_4.setMaximumWidth(200)

        # # ICON BUTTON 1
        # self.icon_button_1 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_heart.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "Icon button - Heart",
        #     width = 40,
        #     height = 40,
        #     radius = 20,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["icon_active"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["pink"]
        # )

        # # ICON BUTTON 2
        # self.icon_button_2 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_add_user.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "BTN with tooltip",
        #     width = 40,
        #     height = 40,
        #     radius = 8,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["white"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["green"],
        # )

        # # ICON BUTTON 3
        # self.icon_button_3 = PyIconButton(
        #     icon_path = Functions.set_svg_icon("icon_add_user.svg"),
        #     parent = self,
        #     app_parent = self.ui.central_widget,
        #     tooltip_text = "BTN actived! (is_actived = True)",
        #     width = 40,
        #     height = 40,
        #     radius = 8,
        #     dark_one = self.themes["app_color"]["dark_one"],
        #     icon_color = self.themes["app_color"]["icon_color"],
        #     icon_color_hover = self.themes["app_color"]["icon_hover"],
        #     icon_color_pressed = self.themes["app_color"]["white"],
        #     icon_color_active = self.themes["app_color"]["icon_active"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["context_color"],
        #     is_active = True
        # )

        # # PUSH BUTTON 1
        # self.push_button_1 = PyPushButton(
        #     text = "Button Without Icon",
        #     radius  =8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["dark_four"]
        # )
        # self.push_button_1.setMinimumHeight(40)

        # # PUSH BUTTON 2
        # self.push_button_2 = PyPushButton(
        #     text = "Button With Icon",
        #     radius = 8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_hover = self.themes["app_color"]["dark_three"],
        #     bg_color_pressed = self.themes["app_color"]["dark_four"]
        # )
        # self.icon_2 = QIcon(Functions.set_svg_icon("icon_settings.svg"))
        # self.push_button_2.setMinimumHeight(40)
        # self.push_button_2.setIcon(self.icon_2)

        # # PY LINE EDIT
        # self.line_edit = PyLineEdit(
        #     text = "",
        #     place_holder_text = "Place holder text",
        #     radius = 8,
        #     border_size = 2,
        #     color = self.themes["app_color"]["text_foreground"],
        #     selection_color = self.themes["app_color"]["white"],
        #     bg_color = self.themes["app_color"]["dark_one"],
        #     bg_color_active = self.themes["app_color"]["dark_three"],
        #     context_color = self.themes["app_color"]["context_color"]
        # )
        # self.line_edit.setMinimumHeight(30)

        # # TOGGLE BUTTON
        # self.toggle_button = PyToggle(
        #     width = 50,
        #     bg_color = self.themes["app_color"]["dark_two"],
        #     circle_color = self.themes["app_color"]["icon_color"],
        #     active_color = self.themes["app_color"]["context_color"]
        # )

        # # TABLE WIDGETS
        # self.table_widget = PyTableWidget(
        #     radius = 8,
        #     color = self.themes["app_color"]["text_foreground"],
        #     selection_color = self.themes["app_color"]["context_color"],
        #     bg_color = self.themes["app_color"]["bg_two"],
        #     header_horizontal_color = self.themes["app_color"]["dark_two"],
        #     header_vertical_color = self.themes["app_color"]["bg_three"],
        #     bottom_line_color = self.themes["app_color"]["bg_three"],
        #     grid_line_color = self.themes["app_color"]["bg_one"],
        #     scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
        #     scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
        #     context_color = self.themes["app_color"]["context_color"]
        # )
        # self.table_widget.setColumnCount(3)
        # self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # # Columns / Header
        # self.column_1 = QTableWidgetItem()
        # self.column_1.setTextAlignment(Qt.AlignCenter)
        # self.column_1.setText("NAME")

        # self.column_2 = QTableWidgetItem()
        # self.column_2.setTextAlignment(Qt.AlignCenter)
        # self.column_2.setText("NICK")

        # self.column_3 = QTableWidgetItem()
        # self.column_3.setTextAlignment(Qt.AlignCenter)
        # self.column_3.setText("PASS")

        # # Set column
        # self.table_widget.setHorizontalHeaderItem(0, self.column_1)
        # self.table_widget.setHorizontalHeaderItem(1, self.column_2)
        # self.table_widget.setHorizontalHeaderItem(2, self.column_3)

        # for x in range(10):
        #     row_number = self.table_widget.rowCount()
        #     self.table_widget.insertRow(row_number) # Insert row
        #     self.table_widget.setItem(row_number, 0, QTableWidgetItem(str("Wanderson"))) # Add name
        #     self.table_widget.setItem(row_number, 1, QTableWidgetItem(str("vfx_on_fire_" + str(x)))) # Add nick
        #     self.pass_text = QTableWidgetItem()
        #     self.pass_text.setTextAlignment(Qt.AlignCenter)
        #     self.pass_text.setText("12345" + str(x))
        #     self.table_widget.setItem(row_number, 2, self.pass_text) # Add pass
        #     self.table_widget.setRowHeight(row_number, 22)

        # # ADD WIDGETS
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_1)
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_2)
        # self.ui.load_pages.row_1_layout.addWidget(self.circular_progress_3)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_1)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_2)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_3)
        # self.ui.load_pages.row_2_layout.addWidget(self.vertical_slider_4)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_1)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_2)
        # self.ui.load_pages.row_3_layout.addWidget(self.icon_button_3)
        # self.ui.load_pages.row_3_layout.addWidget(self.push_button_1)
        # self.ui.load_pages.row_3_layout.addWidget(self.push_button_2)
        # self.ui.load_pages.row_3_layout.addWidget(self.toggle_button)
        # self.ui.load_pages.row_4_layout.addWidget(self.line_edit)
        # self.ui.load_pages.row_5_layout.addWidget(self.table_widget)
        '''

        # RIGHT COLUMN
        # ///////////////////////////////////////////////////////////////

        # BTN 1
        self.right_btn_1 = PyPushButton(
            text="Show Menu 2",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon_right = QIcon(Functions.set_svg_icon("icon_arrow_right.svg"))
        self.right_btn_1.setIcon(self.icon_right)
        self.right_btn_1.setMaximumHeight(40)
        self.right_btn_1.clicked.connect(lambda: MainFunctions.set_right_column_menu(
            self,
            self.ui.right_column.menu_2
        ))
        self.ui.right_column.btn_1_layout.addWidget(self.right_btn_1)

        # BTN 2
        self.right_btn_2 = PyPushButton(
            text="Show Menu 1",
            radius=8,
            color=self.themes["app_color"]["text_foreground"],
            bg_color=self.themes["app_color"]["dark_one"],
            bg_color_hover=self.themes["app_color"]["dark_three"],
            bg_color_pressed=self.themes["app_color"]["dark_four"]
        )
        self.icon_left = QIcon(Functions.set_svg_icon("icon_arrow_left.svg"))
        self.right_btn_2.setIcon(self.icon_left)
        self.right_btn_2.setMaximumHeight(40)
        self.right_btn_2.clicked.connect(lambda: MainFunctions.set_right_column_menu(
            self,
            self.ui.right_column.menu_1
        ))
        self.ui.right_column.btn_2_layout.addWidget(self.right_btn_2)

        # ///////////////////////////////////////////////////////////////
        # END - EXAMPLE CUSTOM WIDGETS
        # ///////////////////////////////////////////////////////////////

    # RESIZE GRIPS AND CHANGE POSITION
    # Resize or change position when window is resized
    # ///////////////////////////////////////////////////////////////
    def resize_grips(self):
        if self.settings["custom_title_bar"]:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)