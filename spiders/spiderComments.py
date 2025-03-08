import random
import time
import requests
import csv
from .clearData import clearData
from globalVariable import *
from datetime import datetime

from utils.wordCloudPicture import get_img

max_id = ''
articleId = ''
commentUrl = 'https://weibo.com/ajax/statuses/buildComments'
text = ''


def init(articleCommentsFilePath):
    if not os.path.exists(articleCommentsFilePath):
        with open(articleCommentsFilePath, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([
                'articleId',
                'created_at',
                'likes_counts',
                'region',
                'content',
                'authorName',
                'authorGender',
                'authorAddress'
            ])


def writerRow(row, articleCommentsFilePath):
    with open(articleCommentsFilePath, 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
        csvFile.flush()
        csvFile.close()


def get_data(url, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        global max_id
        max_id = response_json['max_id']
        return response_json['data']
    else:
        return None


def getAllArticleList(articleDataFilePath):
    artileList = []
    with open(articleDataFilePath, 'r', encoding='utf-8') as reader:
        reader.flush()
        readerCsv = csv.reader(reader)
        for nav in readerCsv:
            # print(nav)
            artileList.append(nav)
            # print(artileList)
    return artileList


def parse_json(response, articleId, articleCommentsFilePath):
    if response is None: return
    for comment in response:
        global region
        created_at = datetime.strptime(comment['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        likes_counts = comment['like_counts']
        try:
            region = comment['source'].replace('来自', '')
        except:
            region = '无'
        content = comment['text_raw']
        content = clearData(content)  # 数据清洗
        if content == "": continue  # 判空
        global text
        text += content

        authorName = comment['user']['screen_name']
        authorGender = comment['user']['gender']
        authorAddress = comment['user']['location']
        writerRow([
            articleId,
            created_at,
            likes_counts,
            region,
            content,
            authorName,
            authorGender,
            authorAddress
        ], articleCommentsFilePath)


def start(articleDataFilePath, articleCommentsFilePath):
    init(articleCommentsFilePath)
    articleList = getAllArticleList(articleDataFilePath)
    for article in articleList[1:]:
        global articleId
        articleId = article[0]

        global text
        text = ''

        start_time = time.time()
        print('正在爬取id值为%s的文章评论' % articleId)
        time.sleep(random.uniform(0, 1))
        params = {
            'id': int(articleId),
            'is_show_bulletin': 2
        }
        response = get_data(commentUrl, params)
        parse_json(response, articleId, articleCommentsFilePath)

        max_page = 100
        max_id_last = 0
        while max_id != 0:
            max_page -= 1
            if max_page < 0:
                break
            print(max_id)
            if max_id_last == max_id: break
            max_id_last = max_id
            params = {
                'id': int(articleId),
                'is_show_bulletin': 2,
                'max_id': int(max_id)
            }
            response = get_data(commentUrl, params)
            parse_json(response, articleId, articleCommentsFilePath)
            time.sleep(random.uniform(0, 0.5))

        end_time = time.time()
        print('耗时：' + str(end_time - start_time))
        print()
        get_img(articleId,text)

#
# if __name__ == '__main__':
#     start()
