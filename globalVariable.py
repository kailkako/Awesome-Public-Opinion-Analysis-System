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

# ================================================================================
# globalVariable.py
# Description: 定义和初始化系统中所需的全局变量，包括 HTTP 请求头信息和文件路径
# ================================================================================

import os
from datetime import datetime

headers = {
    'Cookie': 'SINAGLOBAL=5751723973106.176.1733579323768; ULV=1734857665779:2:2:1:3674643683183.17.1734857665778:1733579323796; PC_TOKEN=87d901794c; SUB=_2AkMQ2BWGf8NxqwFRmfwVzmLibYh-wgnEieKmhORdJRMxHRl-yT9yqmIAtRB6O1g7aRLS_6L2Gx7itrd90QWMKaoLqGad; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9Whw5cfbAdKHTnyJF3gYZi1.; WBPSESS=Wk6CxkYDejV3DDBcnx2LOYhKwneXAvU0U5M4cO8JjUov8YL9f1hVjgzK0ZZaBbjWPF1kZTZ228txCAvThX_W2SgjqG5gqG5MyNKPv_TpDdjGCW-jFFrfvT7s4EEY6gd9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
}

def initGlobalVariable():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    articleDataFilePath = r'spiders\data\articleContent_' + formatted_time + '.csv'
    articleCommentsFilePath = r'spiders\data\articleComments_' + formatted_time + '.csv'
    articleCategoryFilePath = r'spiders\data\articleCategory.csv'
    return articleCategoryFilePath, articleDataFilePath, articleCommentsFilePath

if __name__ == '__main__':
    initGlobalVariable()

