from utils.databaseManage import *

articleList = getAllArticleData()
allCommentList = getAllCommentsData()


def getArticleID():
    articleIDList = []
    for article in articleList:
        articleIDList.append(article[0])
    return articleIDList


def getTypeList():
    return list(set([x[8] for x in getAllArticleData()]))


def getArticleByType(type):
    articles = []
    for i in articleList:
        if i[8] == type:
            articles.append(i)
    return articles


def getIPCharByCommentsRegion(commentsList):
    commentRegionDic = {}
    for i in commentsList:
        if i[3] != '无':
            if commentRegionDic.get(i[3], -1) == -1:
                commentRegionDic[i[3]] = 1
            else:
                commentRegionDic[i[3]] += 1
    resultData = []
    for key, value in commentRegionDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData


def getCommentSentimentData(commentsList):
    # 统计评论情感
    sentiment_counts = {'消极': 0, '中性': 0, '积极': 0}
    for item in commentsList:
        sentiment = item[-1]
        sentiment_counts[sentiment] += 1
    # 转换为输出格式
    sentimentData = [{'name': k, 'value': v} for k, v in sentiment_counts.items()]
    return sentimentData


def getTimeData(commentsList):
    # 初始化日期计数字典
    date_counts = {}

    # 遍历每个评论数据
    for comment in commentsList:
        # 获取日期字段（第二个字段，索引为1）
        date = comment[1]
        # 更新日期计数
        if date in date_counts:
            date_counts[date] += 1
        else:
            date_counts[date] = 1

    # 构建时间和次数列表
    dates = list(date_counts.keys())
    counts = list(date_counts.values())

    return dates, counts
