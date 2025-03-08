from harvesttext import HarvestText
import pyhanlp
import re

# HarvestText 是一个文本处理工具库，通常用于文本数据的预处理、特征提取等任务。
ht = HarvestText()
# CharTable 类主要用于提供一些字符转换的功能，比如将繁体字转换为简体字
CharTable = pyhanlp.JClass('com.hankcs.hanlp.dictionary.other.CharTable')


def clearData(content=''):
    content = CharTable.convert(content)  # 繁体转化为简体
    content = ht.clean_text(content, emoji=False)  # 过滤@后最多6个字符
    # 去除网站链接，替换为空字符串
    content = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', content, flags=re.MULTILINE)
    content = re.sub(r'#.*?#', '', content) #去除两个#之间的内容
    content=content.replace('《》','')
    return content

