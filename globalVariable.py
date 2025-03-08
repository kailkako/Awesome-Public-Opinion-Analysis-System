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

