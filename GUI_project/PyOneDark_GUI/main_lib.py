# encoding: utf-8
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

#API参数
Your_Access_token = '24.64d898b3d528534d6217fc1f0b96eb4b.2592000.1666103970.282335-27525133'
Your_API_Key = 'CmR9rRV3dyScpO8HHiZ0u87m'
Your_App_Id = '27525133'
Your_Secret_Key = 'RY9vVX2VLdgbKznMGStIpl8EaMyFXZPp'



def order_points(pts):#计算表格顶点
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = pts[3]
        rect[2] = pts[1]
        rect[1] = pts[2]
        rect[3] = pts[0]
        return rect

def four_point_transform(image, pts):#计算偏转角度，旋转图像进行校正
        rect = order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped

def remove_noise_and_smooth(img):#降噪处理
        filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 30)
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        or_image = cv2.bitwise_or(img, closing)
        return or_image

    #检测图片旋转
def direction_detect(img_r,token):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
        # 二进制方式打开图片文件
        f = open(img_r, 'rb')
        img = base64.b64encode(f.read())
        params = {"image": img}
        direction = {"detect_direction": "true"}
        access_token = token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers, params=direction)
        json1 = response.json()
        print(json1)
        direct = json1['direction']
        print(direct)
        return direct


    # 读取图片
def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    #文件下载函数
def file_download(url, file_path):
        r = requests.get(url)
        with open(file_path, 'wb') as f:
            f.write(r.content)
#旋转图片
# def rotateAntiClockWise90(img):  # 顺时针旋转90度
#     #img = cv2.imread(img_file)
#     trans_img = cv2.transpose(img)
#     img90 = cv2.flip(trans_img, 0)
#     # cv2.imshow("rotate", img90)
#     # cv2.waitKey(0)
#     return img90


# if __name__ == "__main__":
#     img = cv2.imread(img_r, 0)
#     tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

#     # 降噪处理
#     gray = cv2.GaussianBlur(img, (5, 5), 0)
#     cv2.imwrite('./filtered.png', gray, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

#     # 边缘检测、二值化
#     edged = cv2.Canny(gray, 10, 50)
#     cv2.imwrite('./edged_bi.png', edged, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

#     # 对表单进行轮廓绘制
#     cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[1] if imutils.is_cv3() else cnts[0]
#     cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
#     screenCnt = None
#     for c in cnts:
#         peri = cv2.arcLength(c, True)
#         approx = cv2.approxPolyDP(c, 0.02 * peri, True)
#         if len(approx) == 4:
#             screenCnt = approx
#             break

#     # 寻找表格轮廓
#     cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 2)

#     img = four_point_transform(img, approx)



#     # 开闭运算降噪处理
#     img = remove_noise_and_smooth(img)
#     cv2.imwrite('./pre_done.png', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
#     imgr_pre_done = './pre_done.png'

#     #大方向检测旋转
#     direct = direction_detect(imgr_pre_done)
#     img_spined = cv2.imread('./pre_done.png')
#     for i in range(direct):
#         img_spined = cv2.rotate(img_spined, cv2.ROTATE_90_CLOCKWISE)
#     cv2.imwrite('./spinned.png', img_spined, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
#     img = img_spined
#     shutil.copyfile("./spinned.png", "./Pretreatment/aaa.png")

#     # 定义常量
#     APP_ID = Your_App_Id
#     API_KEY = Your_API_Key
#     SECRET_KEY = Your_Secret_Key
#     # 初始化AipFace对象
#     client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
#     root = tk.Tk()
#     root.withdraw()
#     data_dir = filedialog.askdirectory(title='请选择图片文件夹') + '/'
#     result_dir = filedialog.askdirectory(title='请选择输出文件夹') + '/'
#     num = 0
#     for name in os.listdir(data_dir):
#         print ('{0} : {1} 正在处理：'.format(num+1, name.split('.')[0]))
#         image = get_file_content(os.path.join(data_dir, name))
#         res = client.tableRecognitionAsync(image)
#         print ("res:", res)
#         if 'error_code' in res.keys():
#             print ('Error! error_code: ', res['error_code'])
#             sys.exit()
#         # 获取识别ID号
#         req_id = res['result'][0]['request_id']

#         # OCR识别需要一定时间，设定10秒内每隔1秒查询一次
#         for count in range(1, 20):
#             # 通过ID获取表格文件XLS地址
#             res = client.getTableRecognitionResult(req_id)
#             if res['result']['ret_msg'] == '已完成':
#                 # 云端处理完毕，成功获取表格文件下载地址，跳出循环
#                 break
#             else:
#                 time.sleep(1)

#         url = res['result']['result_data']
#         xls_name = name.split('.')[0] + '.xls'
#         file_download(url, os.path.join(result_dir, xls_name))
#         num += 1
#         print ('{0} : {1} 下载完成。'.format(num, xls_name))
#         time.sleep(1)
