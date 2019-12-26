from lxml import etree
import re
import random

file = 'D:\BaiduNetdiskDownload\enwiki\enwiki.xml'
tree = etree.iterparse(file)

title = ''#词条名
id = -1#词条id
out = ''#词条的出链
dic = {}#用字典存储每个词条的出链
pr = {}#用字典存储每个词条的pagerank值
NUM = 1e6#采样总数
d = 0.85#阻尼因子

def strip_tname(t):#提取tag中有效信息，只要"}"后的字符串
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx+1:]
    return t

for event, elem in tree:#遍历文件收集所需信息
    tname = strip_tname(elem.tag)
    if event == 'end':
        if tname == 'page':#统计该页面的信息
            if re.match(r'(?!File:|Image:|Wikipedia:|Category:|Portal:|Template:)(.*?)',title):#不含一些特殊的名字
                dic[title] = out
                pr[title] = 1/NUM
                out = ''
                if len(dic) % 10000 == 0:
                    print(len(dic))
        elif tname == 'title':
            title = elem.text
        elif tname == 'id':
            id = elem.text
        elif tname == 'text':#外链就在正文中(在[[]]中)
            p1 = re.compile(r'\[\[(?!File:|Image:|Wikipedia:|Category:|Portal:|Template:)(.*?)(?:\||]])', re.S)#正则表达式匹配出链的名称
            out = re.findall(p1, str(elem.text))
            _out = []
            for s in out:
                if '|' in s:#如果有|，取后面的内容
                    s = re.sub(u'.*\|', '', s)
                _out.append(s)
            out = _out
    elem.clear()
    if len(dic) > NUM:
        break

def calculate(cnt):#迭代计算pagerank，次数可以指定
    pr0 = pr.copy()
    for k in range(cnt):
        print (k)
        tmp = dict([(x, 0) for x in pr0])
        for i in dic:
            n = len(dic[i])
            for j in dic[i]:
                if j in pr0:
                    tmp[j] += pr0[i] / n
        for i in pr0:
            pr0[i] = d * tmp[i] + (1-d)/NUM

    res = sorted(pr0.items(), key=lambda d:d[1],reverse = True)#pr值从大到小排序

    with open('res'+str(cnt)+'.txt', 'w+', encoding='utf-8') as f:#存储到文件中
        for i in res:
            f.write(str(i[0])+'\t'+str(i[1])+'\n')

calculate(1)#分别迭代1、10、20、50次，看看输出的结果有何不同
calculate(10)
calculate(20)
calculate(50)
