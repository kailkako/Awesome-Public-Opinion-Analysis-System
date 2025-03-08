from utils.databaseManage import *
from datetime import datetime


allCommentsList = getAllCommentsData()
# articleList = getAllArticleData()


def getHomeTagsData():
    articleList = getAllArticleData()
    # 文章个数
    articleLenMax = len(articleList)

    # 最高点赞微博-作者
    likeCountMax = 0
    likeCountMaxAuthorName = ''
    # 最多城市
    cityDic = {}
    for article in articleList:
        if likeCountMax < int(article[1]):
            likeCountMax = int(article[1])
            likeCountMaxAuthorName = article[9]
        if article[4] != '无':
            if cityDic.get(article[4], -1) == -1:
                cityDic[article[4]] = 1
            else:
                cityDic[article[4]] += 1
    cityDicSorted = list(sorted(cityDic.items(), key=lambda x: x[1], reverse=True))
    if articleLenMax==0:
        return 0, '', '',[]
    else:
        return articleLenMax, likeCountMaxAuthorName, cityDicSorted[0][0],articleList


def getHomeCommentsLikeCountTopFore():
    return list(sorted(getAllCommentsData(), key=lambda x: int(x[2]), reverse=True))[:4]


def getHomeArticleCreatedAtChart(articleList):
    if len(articleList)==0 :
        return None,None
    xData = list(set([x[6] for x in articleList]))
    xData = list(sorted(xData, key=lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp(), reverse=True))
    yData = [0 for x in range(len(xData))]
    for article in articleList:
        for index, j in enumerate(xData):
            if article[6] == j:
                yData[index] += 1
    return xData, yData


def getHomeTypeChart(articleList):
    typeDic = {}
    for article in articleList:
        if typeDic.get(article[7], -1) == -1:
            typeDic[article[7]] = 1
        else:
            typeDic[article[7]] += 1
    resultData = []
    for key, value in typeDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData




# 文章情绪类别占比
def getEmotion():
    emotionDic = {}
    articleList = getAllArticleData()
    for article in articleList:
        emotion = article[14]
        if emotion not in emotionDic:
            emotionDic[emotion] = 1
        else:
            emotionDic[emotion] += 1
    resultData = []
    for key, value in emotionDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData


# if __name__ == '__main__':
#     resultData=getEmotion()
#     print(resultData)