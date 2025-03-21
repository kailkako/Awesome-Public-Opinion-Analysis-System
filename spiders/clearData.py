# Copyright 2025 kailkako/Awesome-Public-Opinion-Analysis-System
# Author：Licheng Yu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==================================================================
# clearDate.py
# Description: 数据清洗
# ==================================================================

import re
import pyhanlp    # CharTable 类主要用于提供一些字符转换的功能，比如将繁体字转换为简体字
from harvesttext import HarvestText # HarvestText 是一个文本处理工具库，通常用于文本数据的预处理、特征提取等任务

ht = HarvestText()
CharTable = pyhanlp.JClass('com.hankcs.hanlp.dictionary.other.CharTable')

def clearData(content=''):
    content = CharTable.convert(content)            # 繁体转化为简体
    content = ht.clean_text(content, emoji=False)   # 过滤@后最多6个字符
    content = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', content, flags=re.MULTILINE)  # 去除网站链接，替换为空字符串
    content = re.sub(r'#.*?#', '', content)         #去除两个#之间的内容
    content=content.replace('《》','')
    return content

