from get_apk import *
from configparser import ConfigParser


# 实例化ConfigParser对象
cf = ConfigParser()

# 读取config.ini文件
cf.read('config.ini')

# 读取file_name_list模块下的file_name字段的值
# file_name是以'/'分隔的一系列excel文件名
file_str = cf.get("file_name_list", 'file_name')
file_list = file_str.split('/')

for filename in file_list:
    # excel文件的保存路径
    filepath = os.path.dirname(os.path.realpath(__file__)) + '\\' + filename
    # 下载完成的apk的保存路径，以导入的Excel表格的文件名命名
    basepath = os.path.dirname(os.path.realpath(__file__)) + '\\%s' % os.path.splitext(filename)[0]
    f = os.path.splitext(filename)[0]
    try:
        main(basepath, filepath, f, sheet_name='Sheet1')
    except TypeError as e:
        print("Error: %s " % e)

