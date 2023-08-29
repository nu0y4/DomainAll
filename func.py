import base64
import os

import re
import subprocess
import sys
import time

import requests

# from lib.OneForAll.oneforall import OneForAll

# from FuckSubdomain.lib.OneForAll.oneforall import OneForAll

# fofa
fofa_email = ""
fofa_key = ""
# shodan
API_KEY = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.158 Safari/537.36 fanwe_app_sdk sdk_type/android sdk_version_name/4.0.1 sdk_version/2020042901 screen_width/720 screen_height/1280',
}

def filter_list(lst, keyword):
    filtered_list = [item for item in lst if keyword in item]
    return filtered_list


def out2txt(domainlists, domainname):
    # 标准输出函数 提供输出列表和输出文件路径的主域名名字
    import os
    import datetime
    # 创建以domainname和当前时间命名的文件夹
    folder_name = domainname + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    folder_path = os.path.join('output', folder_name)
    os.makedirs(folder_path)

    # 将路径保存为fileoutpath
    fileoutpath = os.path.join(folder_path, domainname + '.txt')

    # 标准输出函数的主要逻辑
    with open(fileoutpath, 'w') as outf:
        outf.write(domainname + '\n')
        for domain in domainlists:
            outf.write(domain + '\n')


def add2list(list_new, list_old):
    # 将新列表追加都旧的原有列表后，并去重
    for domain in list_new:
        if domain not in list_old:
            list_old.append(domain)
    return list_old

def 删除换行符(list_:list):
    co = []
    for i in list_:
        co.append(i.replace('\n',''))
    return co

def getsubdata(txt: list):
    li_url = list()
    for url in txt:
        url = str(url)[0:str(url).index(' ')]
        li_url.append(url)
    return li_url


def get_fofa(domain):
    fofa_domain = []
    query = 'domain="%s"' % (domain)  # fofa查询的语法
    query = (base64.b64encode(query.encode('utf-8'))).decode('utf-8')  # 语法需要经过base64编码
    url_api = 'https://fofa.info/api/v1/search/all?email=%s&key=%s&qbase64=%s&size=10000&fields=host,ip,port&full=true' % (
        fofa_email, fofa_key, query)
    for i in range(1,5):
        try:
            response = requests.get(url=url_api, headers=headers, timeout=15, verify=False).json()
            # print(response)
            if response.get('error') != False:
                print("fofa查询失败\r" + response)
                return '错误'
            # print('fofa查询成功!')
            subdomain = response.get("results")  # 查询的结果保留在列表中
            # print(subdomain)
            for list in subdomain:
                host = list[0]  # 子域
                ip = list[1]  # 子域所属ip
                port = list[2]  # 开放端口
                if "https" in host:
                    url = host
                else:
                    url = "http://" + host
                # print(url)
                fofa_domain.append(url)
            break
        except Exception as e:
            print("请求出错，正在尝试重新请求...", e)
    return fofa_domain

def get_shodan(domain):
    import shodan
    temp_list = []
    api = shodan.Shodan(API_KEY)
    results = api.search('hostname:' + domain, limit=1000, minify=True)
    for match in results["matches"]:
        add2list(match["hostnames"], temp_list)
    out_list = filter_list(temp_list, domain)
    return out_list


def run_oneforall(domain):
    print('[+]DNSX')
    """
    执行oneforall收集域名信息

    domain: 目标域名
    fmt: 输出文件格式,默认为csv
    """
    if not re.match(r'^[^\s<>]{1,}\.[^\s<>]{1,}$', domain):
        print('域名格式不正确')
        return

    # test = OneForAll(target=domain)
    # test.dns = True
    # test.brute = True
    # test.req = True
    # test.takeover = True
    # test.run()
    # return test.datas


# def use_subdomainsbrute(domain):
#     filename = f'{domain}-{time.time()}.txt'
#     run(f'python3 /home/lib/subDomainsBrute/subDomainsBrute.py -o /home/out/{filename} {domain}')
#     return filename


def run_subdomains_brute(domain):
    print('[+]Subdomain')
    filename = f'{domain}-{time.time()}.txt'
    command = f'python .\\lib\\subDomainsBrute\\subDomainsBrute.py -w -o .\\out\\{filename} {domain}'

    try:
        subprocess.run(command, shell=True, check=True)
        return filename
    except subprocess.CalledProcessError as e:
        return None


def dnsx(domain:str):
    print('[+]DNSX')
    filename = f'{domain}-{time.time()}.txt'
    # print(os.getcwd())
    command = f'{os.getcwd()}\\lib\\subfinder -silent -d {domain} | {os.getcwd()}\\lib\\dnsx\\dnsx.exe -silent > .\\out\\{filename}'

    try:
        subprocess.run(command, shell=True, check=True)
        return filename
    except subprocess.CalledProcessError as e:
        return None


def asset(domain:str):
    print('[+]AssetFinder')
    filename = f'{domain}-{time.time()}.txt'
    # print(os.getcwd())
    command = f'{os.getcwd()}\\lib\\assetfinder -subs-only {domain} > .\\out\\{filename}'

    try:
        subprocess.run(command, shell=True, check=True)
        return filename
    except subprocess.CalledProcessError as e:
        return None

def run(cmd) -> (int, str):
    """
    开启子进程，执行对应指令，控制台打印执行过程，然后返回子进程执行的状态码和执行返回的数据
    :param cmd: 子进程命令
    :param shell: 是否开启shell
    :return: 子进程状态码和执行结果
    """
    # print(f'\033[1;32m************** {name}开始扫描 **************\033[0m')

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = []
    while p.poll() is None:
        line = p.stdout.readline().strip()
        if line:
            line = _decode_data(line)
            result.append(line)
            print('\033[1;35m{0}\033[0m'.format(line))
        # 清空缓存
        sys.stdout.flush()
        sys.stderr.flush()
    # 判断返回码状态
    if p.returncode == 0:
        print('[+]成功')
    else:
        print('[+]失败')
    return p.returncode, '\r\n'.join(result)


def _decode_data(byte_data: bytes):
    """
    解码数据
    :param byte_data: 待解码数据
    :return: 解码字符串
    """
    try:
        return byte_data.decode('UTF-8')
    except UnicodeDecodeError:
        return byte_data.decode('GB18030')
