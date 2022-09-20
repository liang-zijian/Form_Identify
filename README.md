# 表单识别

> 本仓库是`表单识别`项目的源码
> 调用[百度云API](https://cloud.baidu.com/)实现图片`图像去噪`，`方向自适应`，`数据导入Excel`的功能

## 文件结构树：

表单识别

```
│  3.JPG  测试图片1
│  5.JPG  测试图片2
│  6.JPG  测试图片3
│  Access_token.py  获取token脚本
│  edged_bi.png 边缘检测+二值化结果
│  filtered.png	滤波结果
│  Lab_12.py 主函数
│  pre_done.png 初步预处理结果
│  README.md README
│  spinned.png 自适应旋转后结果
│
└─Pretreatment 预处理结果文件夹
        aaa.png API输入图片
        aaa.xls 输出excel表
```

## 使用说明

创建百度云账号，创建应用，获得API Key与Secret Key，替换掉`Access_token.py`中的AK与SK参数，运行该脚本，从控制台中找到返回的Access_token字段

```python
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=【AK】&client_secret=【SK】'
```



替换掉Lab_12.py中的若干参数

![image-20220919111224293](https://s2.loli.net/2022/09/19/cebviOgXyAUJ9rN.png)



运行脚本过程中，弹出两个对话框，分别选择输出文件夹和图片文件夹，

**推荐都选择Pretreatment文件夹！**



## 其他说明

注意解压时，3.JPG、Pretreatment文件夹要和代码处于同一路径下才可正常运行

运行代码后，需要先后选取图片文件夹和输出文件夹
图片文件夹选取本路径下的Pretreatment文件夹，输出文件夹任意，识别结果将以.xls文件的格式保存在输出文件夹下

若程序报错，可以试着重新运行。若连续3-5次左右报错，可能是因为百度Aip接口调用达到上限
