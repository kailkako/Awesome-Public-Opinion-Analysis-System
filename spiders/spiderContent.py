import re
import time
import requests
import csv
import random
from .clearData import clearData
from globalVariable import *


def init(articleDataFilePath):
    if not os.path.exists(articleDataFilePath):
        with open(articleDataFilePath, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([
                'id',  # 作者id
                'likeNum',  # 点赞数
                'commentsLen',  # 评论数
                'reposts_count',  # 转发量
                'region',  # 地区
                'content',  # 文章内容
                'created_at',  # 发布时间
                'type',  # 文章类型
                'detailUrl',  # followBtnCode>uid + mblogid 文章详情地址
                'authorName',  # 作者名字
                'authorDetail'  # 作者主页地址
            ])


def writerRow(row, articleDataFilePath):
    with open(articleDataFilePath, 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)  # 写入数据到文件
        # 刷新缓冲区
        csvFile.flush()


def get_data(url, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['statuses']
    else:
        return None


def getTypeList(types=[], articleCategoryFilePath=''):
    type_list = []
    with open(articleCategoryFilePath, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in types:
                type_list.append(row)
    return type_list


def parse_json(response, articleDataFilePath, type='无'):
    for article in response:
        commentsLen = article['comments_count']
        if int(commentsLen) < 100: break
        id = article['id']
        likeNum = article['attitudes_count']
        reposts_count = article['reposts_count']
        mblogid = article['mblogid']
        try:
            region = article['region_name'].replace('发布于 ', '')
        except:
            region = '无'
        content = article['text']
        # content = article['text'].replace(' ', '').replace('\u200b', '').replace('\n', '')


        if '...<span class="expand">展开</span>' in content:
            response_longTextContent = requests.get(
                'https://weibo.com/ajax/statuses/longtext',
                headers=headers,
                params={'id': mblogid}
            )
            if response_longTextContent.status_code == 200:
                content = response_longTextContent.json()['data']['longTextContent']
        else:
            content = article['text_raw']

        created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        type = type
        try:
            detailUrl = 'https://weibo.com/' + str(id) + '/' + str(mblogid)
        except:
            detailUrl = '无'
        authorName = article['user']['screen_name']
        authorDetail = 'https://weibo.com/u/' + str(article['user']['id'])
        # 数据清洗
        content = clearData(content)
        if content=='': continue
        if content == " ": continue


        writerRow([
            id,
            likeNum,
            commentsLen,
            reposts_count,
            region,
            content,
            created_at,
            type,
            detailUrl,
            authorName,
            authorDetail
        ], articleDataFilePath)


def start(types=[], page=0, articleCategoryFilePath='', articleDataFilePath=''):
    articleUrl = 'https://weibo.com/ajax/feed/hottimeline'
    init(articleDataFilePath)
    typeList = getTypeList(types, articleCategoryFilePath)
    print(typeList)
    for type in typeList:
        time.sleep(random.uniform(0, 1))
        for currentPage in range(0, page):
            print('正在爬取的类型：%s 中的第%s页文章数据' % (type[0], currentPage + 1))
            time.sleep(random.uniform(0, 1))
            parmas = {
                'group_id': type[1],
                'containerid': type[2],
                'max_id': page,
                'count': 10,
                'extparam': 'discover|new_feed'
            }
            response = get_data(articleUrl, parmas)
            parse_json(response, articleDataFilePath, type[0])


def start_2(url, articleDataFilePath,type):
    init(articleDataFilePath)
    mblogid = getId(url)
    if mblogid is None: return False
    response = requests.get('https://weibo.com/ajax/statuses/show?id=' + mblogid, headers=headers)
    article = response.json()
    articleId = article['id']
    likeNum = article['attitudes_count']
    commentsLen = article['comments_count']
    reposts_count = article['reposts_count']
    try:
        region = article['region_name'].replace('发布于 ', '')
    except:
        region = '无'

    content = article['text']
    # content = article['text'].replace(' ', '').replace('\u200b', '').replace('\n', '')

    if content.find("...<span class=\"expand\">展开</span>") != -1:
        response_longTextContent = requests.get('https://weibo.com/ajax/statuses/longtext', headers=headers,
                                                params={'id': mblogid})
        if response_longTextContent.status_code == 200:
            content = response_longTextContent.json()['data']['longTextContent']
    else:
        content = article['text_raw']

    created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
    if type=='':
        type = '无'
    detailUrl = url
    authorName = article['user']['screen_name']
    authorDetail = 'https://weibo.com/u/' + str(article['user']['id'])
    content = clearData(content)
    if content == "": content = 'error'



    writerRow([
        articleId,
        likeNum,
        commentsLen,
        reposts_count,
        region,
        content,
        created_at,
        type,
        detailUrl,
        authorName,
        authorDetail
    ], articleDataFilePath)

    return articleId


def getId(url):
    '''
        获取文章ID
        具体文章格式:【https://weibo.com/用户ID/文章ID; 如https://weibo.com/1784473157/Ph0NTo2Ba】
    '''
    # 找到最后一个斜杠的位置
    last_slash_pos = url.rfind('/')

    # 提取斜杠后
    if last_slash_pos != -1:
        return url[last_slash_pos + 1:]
    return None

# if __name__ == '__main__':
#     start(['热门', '动漫', '美食'], 1)
