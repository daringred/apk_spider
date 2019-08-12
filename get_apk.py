import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

"""
__author__: syyao
last updated: 07/22/2019
url: 'https://apkpure.com/cn/'
"""


def get_excel_data(file_path, sheet_name):
    """
    import data from excel
    :param file_path: excel file path
    :param sheet_name: sheet name
    :return: App ID, App Name (numpy series)
    """
    try:
        df = pd.read_excel(u'%s' % file_path, sheet_name)
        df = df.fillna(0)
        colname = df.columns
        return df[colname[0]], df[colname[1]]
    except IOError as e:
        print("Error: {0}".format(e))


def request_url(url):
    """
    请求下载页面的URL
    :param url: 待下载页面的URL
    :return: response
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                      Chrome/75.0.3770.142 Safari/537.36',
    }
    # 请求该url，会出现下载页面，但是还无法获取下载的文件流
    response = requests.get(url, headers=headers)
    return response


def get_all_apk(response, basepath, apk_name, no):
    """
    get the apk from url
    :param response: 请求下载页面获取的响应
    :param basepath: 存储apk的基本路径
    :param apk_name: apk的名字
    :param no: apk的序号
    :return: None
    """
    try:
        soup = BeautifulSoup(response.text, 'lxml')

        # 获取真正的下载链接，请求该链接才可以获得真正的apk
        real_downloading_url = soup.find('iframe', attrs={'id': 'iframe_download'})['src']
        # apk_name = soup.find('span', attrs={'class': 'file'}).text

        # get the size of the apk
        size_info = soup.find('span', attrs={'class': 'fsize'}).text
        size = size_info.split(' ')[0]

        # get the unit of the apk size (ie: GB or MB)?
        unit = size_info.split(' ')[1]
        apk_size = float(size[1:])
        apk_unit = unit[:-1]

        # 如果单位是GB，先转化成MB
        if apk_unit == 'GB':
            apk_size = apk_size * 1024

        # download big file
        # 流下载时为了避免文件过大占用内存，设置stream参数为True
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                              Chrome/75.0.3770.142 Safari/537.36',
        }
        # request the real downloading url
        new_res = requests.get(real_downloading_url, headers=headers, stream=True)

        # 构造apk的保存路径
        output_filename = ''.join([u'%s' % basepath, '\\', apk_name, '.apk'])

        # 先判断当前apk是否已经下载完成，已下载完则跳过，但是下载一半了或者没下载就重新开始下载
        if not os.path.exists(output_filename) or os.path.getsize(output_filename)/(1024*1024) <= apk_size - 1:
            # Downloading started
            print("Downloading NO.%s file: %s ..." % (no, apk_name))
            progress_count = 0
            with open(output_filename, 'wb') as f:
                #  流下载时为了避免文件过大占用内存，使用分块下载方式iter_content，边下载边存储到文件
                # request 10M every time
                for chunk in new_res.iter_content(chunk_size=10*1024*1024):
                    if chunk:
                        f.write(chunk)
                        progress_count = progress_count + len(chunk)
                        progress = round((progress_count / (apk_size * 1024 * 1024)) * 100)
                        print("\r 下载进度： {:.1f}%({:.1f} MB/{:.1f} MB)".format(progress,
                                                                             progress_count / (1024*1024), apk_size)
                              , end=" ")
            print("\n %s has been downloaded!" % apk_name)
    except IOError as e:
        print("Error: {}".format(e))
        print('-' * 80)

    except TypeError as e:
        print("Error: {}".format(e))
        print('-' * 80)


# if __name__ == '__main__':
#     file_path = r'E:\TT\亚太TOP游戏.xlsx'
#     sheet_name = 'Sheet1'
#     apk_name, app_name = get_excel_data(file_path, sheet_name)
#     num = len(apk_name)
#     basepath = r'E:\apk_spider\test'
#     for i in range(2):
#         app_name_ = '-'.join(app_name[i].split())
#         url = ''.join(['https://apkpure.com/cn/', app_name_, '/', apk_name[i], '/download?from=details'])
#         get_apk(url, basepath)


def main(basepath, filepath, filename, sheet_name):
    """
    this is the main function which downloads all of the apk
    :param basepath: 下载完成的apk的保存路径
    :param filepath: 待读取的保存包名的Excel文件的保存路径
    :param filename: 待读取的保存包名的Excel文件的文件名
    :param sheet_name: 表名
    :return: downloaded apk, this will create a current directory's sub-folder named by your excel file name
    """
    apk_name, app_name = get_excel_data(filepath, sheet_name)
    num = len(apk_name)
    # 判断该文件夹是否已经存在，不存在则新建
    if not os.path.exists(basepath):
        os.makedirs(basepath)
    for i in range(num):
        # 如果 app name为空，则去掉这个字段，生成的URL也可以访问
        if not app_name[i]:
            url = ''.join(['https://apkpure.com/cn/', apk_name[i], '/download?from=details'])
            response = request_url(url)
            # 如果状态码不为200，说明没有办法获得这个下载页面，可能需要去别的网站下载该游戏的apk
            if response.status_code != 200:
                # 在cmd输出错误信息
                print('-'*80)
                print("Error: couldn't find NO.{0} apk <{1}> on this web!".format(i+1, apk_name[i]))

                # 将错误信息导出为TXT，以download_failed_excel表格名的方式命名
                with open('download_failed_%s.txt' % filename, 'a') as f:
                    f.write("Error: couldn't find NO.{0} apk<{1}> on this web! \n".format(i + 1, apk_name[i]))
                print('-'*80)
            else:
                get_all_apk(response, basepath, apk_name[i], str(i+1))
        # 如果app name不为空，有可能是乱码或正常字段
        else:
            # 处理正常字段
            app_name_new = '-'.join(app_name[i].split())
            # generate the downloading url
            url = ''.join(['https://apkpure.com/cn/', app_name_new, '/', apk_name[i], '/download?from=details'])
            response = request_url(url)

            # 处理App name乱码问题导致找不到页面的问题，则去掉这个字段重新拼接URL
            # 也有可能该网站找不到该游戏的apk
            if response.status_code != 200:
                url = ''.join(['https://apkpure.com/cn/', apk_name[i], '/download?from=details'])
                response = request_url(url)

                # 如果还是404，则说明这个网站上可能没这个游戏
                if response.status_code != 200:
                    # 在cmd输出错误信息
                    print('-' * 80)
                    print("Error: couldn't find NO.{0} apk<{1}> on this web!".format(i+1, apk_name[i]))
                    # 将错误信息导出为TXT，以download_failed_excel表格名的方式命名
                    with open('download_failed_%s.txt' % filename, 'a') as f:
                        f.write("Error: couldn't find NO.{0} apk<{1}> on this web! \n".format(i+1, apk_name[i]))
            get_all_apk(response, basepath, apk_name[i], str(i+1))
