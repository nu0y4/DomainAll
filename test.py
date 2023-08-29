import os

from DomainAll.func import dnsx, getsubdata, 删除换行符

contont = []
domain = 'baidu.com'
dnsx_file = dnsx(domain)
if dnsx_file:
    file = open(f'.\\out\\{dnsx_file}', 'r')
    if os.path.isfile(f'.\\out\\{dnsx_file}'):
        contont = file.readlines()
        contont = 删除换行符(contont)
else:
    print('[+]读取失败')
for i in contont:
    print(i)

