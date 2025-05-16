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

# =======================================================================================
# page.py
# Description: 定义了一个名为 page_app的 Blueprint，用于处理与文章数据相关的各种Web请求
# =======================================================================================

from flask import Flask, session, render_template, redirect, Blueprint, request, jsonify, url_for
from spiders.main import save_to_sql, main_2
from utils.base_page import *
from utils.getEchartsData import *
from spiders.main import main as startSpider
from utils.topicAnalysis import *

page_app = Blueprint('page', __name__, url_prefix='/page', template_folder='templates')


@page_app.route('/yuqingChar')
def yuqingChar():
    username = session.get('username')
    negative_articleList = getAllNegativeArticle()
    positive_articleList = getAllPositiveArticle()
    return render_template('yuqingChar.html',
                           username=username,
                           negative_articleList=negative_articleList,
                           positive_articleList=positive_articleList
                           )


@page_app.route('/delete_all_articles', methods=['POST'])
def delete_all_articles_route():
    try:
        if delete_all_articles():
            return jsonify({'status': 'success', 'message': '所有文章成功删除'})
        else:
            return jsonify({'status': 'failure', 'message': '删除失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@page_app.route('/delete_articles', methods=['POST'])
def delete_articles_route():
    try:
        data = request.get_json()
        article_ids = data.get('articleIds', [])
        if delete_articles(article_ids):
            return jsonify({'status': 'success', 'message': '文章成功删除'})
        else:
            return jsonify({'status': 'failure', 'message': '文章删除失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@page_app.route('/deleteData')
def deleteData():
    username = session.get('username')
    articeList = getAllArticleData()
    return render_template('deleteData.html',
                           username=username,
                           articeList=articeList
                           )


@page_app.route('/commentsData')
def commentsData():
    username = session.get('username')
    top_comments_list = get_top_100_comments()
    print(top_comments_list[0])
    return render_template('commentsData.html',
                           username=username,
                           top_comments_list=top_comments_list
                           )


# 爬取指定文章
@page_app.route('/spiderArticle', methods=['GET'])
def spiderArticle():
    message = ''
    username = session.get('username')
    url = request.args.get('url')
    type_str = request.args.get('type')
    try:
        if url:
            if not url.startswith('https://weibo.com/'):
                message = '地址错误'
                return render_template('spiderData.html',
                                       username=username,
                                       message=message
                                       )
            articleId = main_2(url, type_str)
            # message = '成功爬取单个文章数据'
            return redirect(url_for('page.articleChar', articleId=articleId))
    except Exception as e:
        print(e)
        error_message = str(e)
        print(f"An unexpecccccccted error occurred: {error_message}")
        if error_message == 'You should supply an encoding or a list of encodings to this method that includes input_ids, but you provided []':
            return render_template('spiderData.html',
                                   username=username,
                                   message='地址错误'
                                   )
        return render_template('spiderData.html',
                               username=username,
                               message=error_message
                               )

    return render_template('spiderData.html',
                           username=username,
                           message=message
                           )


# 爬取多个文章
@page_app.route('/spiderArticles', methods=['GET'])
def spiderArticles():
    message = ''
    username = session.get('username')
    try:
        types = request.args.get('types')
        page = request.args.get('page')
        print("Selected types: {}, Selected page: {}".format(types, page))
        if page is not None:
            page = int(page)
        else:
            # 提供默认值或者进行错误处理
            page = 1  # 或者其他默认值
        if types is not None:
            startSpider(types, page)
            message = '爬取成功'
            return redirect(url_for('page.articleData_temp'))
    except Exception as e:
        error_message = str(e)
        print(f"An unexpected error occurred: {error_message}")
        if error_message == 'You should supply an encoding or a list of encodings to this method that includes input_ids, but you provided []':
            return render_template('spiderData.html',
                                   username=username,
                                   message='文章类型太少或页数太少'
                                   )
        elif error_message.find('Expecting value: line') == 0:
            return render_template('spiderData.html',
                                   username=username,
                                   message='Cookie失效'
                                   )
        return render_template('spiderData.html',
                               username=username,
                               message=error_message
                               )


@page_app.route('/articleData_temp', methods=['GET'])
def articleData_temp():
    username = session.get('username')
    articeList = getAllArticleData_temp()
    return render_template('articleData_temp.html',
                           username=username,
                           articeList=articeList
                           )


@page_app.route('/spiderData', methods=['GET'])
def spiderData():
    username = session.get('username')
    return render_template('spiderData.html',
                           username=username
                           )


@page_app.route('/topic')
def topic():
    username = session.get('username')
    try:
        ciTiaoList = getCiTiaoList()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return render_template('topic.html',
                           username=username,
                           ciTiaoList1=ciTiaoList[:10],
                           ciTiaoList2=ciTiaoList[10:]
                           )


@page_app.route('/analysisTopic')
def analysisTopic():
    username = session.get('username')
    try:
        ciTiao = request.args.get('ciTiao')
        description_list, emotion, word_cloud, typical_viewpoint_list = getWeiboAI(ciTiao)
        generate_wordcloud(word_cloud, ciTiao)
        names, nums = getCharData(emotion)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ciTiaoList = getCiTiaoList()
        return render_template('topic.html',
                               username=username,
                               ciTiaoList1=ciTiaoList[:10],
                               ciTiaoList2=ciTiaoList[10:]
                               )
    return render_template('analysisTopic.html',
                           username=username,
                           description_list=description_list[:5],
                           emotion=json.dumps(emotion),
                           names=names,
                           nums=nums,
                           ciTiao=ciTiao,
                           typical_viewpoint_list=typical_viewpoint_list[:10]
                           )


@page_app.route('/updateData')
def updateData():
    username = session.get('username')
    articeList = getAllArticleData()
    return render_template('updateData.html',
                           username=username,
                           articeList=articeList
                           )


@page_app.route('/home')
def home():
    username = session.get('username')
    articleLenMax, likeCountMaxAuthorName, cityMax, articleList = getHomeTagsData()
    commentsLikeCountTopFore = getHomeCommentsLikeCountTopFore()
    xData, yData = getHomeArticleCreatedAtChart(articleList)
    typeChart = getHomeTypeChart(articleList)
    emotionData = getEmotion()
    return render_template('index.html',
                           username=username,
                           articleLenMax=articleLenMax,
                           likeCountMaxAuthorName=likeCountMaxAuthorName,
                           cityMax=cityMax,
                           commentsLikeCountTopFore=commentsLikeCountTopFore,
                           xData=xData,
                           yData=yData,
                           typeChart=typeChart,
                           emotionData=emotionData
                           )


@page_app.route('/articleData')
def tableData():
    username = session.get('username')
    articeList = getAllArticleData()
    return render_template('articleData.html',
                           username=username,
                           articeList=articeList
                           )


@page_app.route('/articleChar', methods=['GET'])
def articleChar():
    username = session.get('username')
    articleIDList = getArticleID()
    typeList = getTypeList()
    defaultArticleID = articleIDList[0]
    if request.args.get('articleId'): defaultArticleID = request.args.get('articleId')
    commentsList = getCommentsData(str(defaultArticleID))
    article = getArticleData(str(defaultArticleID))
    commentRegionData = getIPCharByCommentsRegion(commentsList)
    sentimentData = getCommentSentimentData(commentsList)
    time_dates, time_counts = getTimeData(commentsList)
    return render_template('articleChar.html',
                           username=username,
                           articleIDList=articleIDList,
                           typeList=typeList,
                           defaultArticleID=defaultArticleID,
                           likeNum=article[0][1],
                           commentsLen=article[0][2],
                           reposts_count=article[0][3],
                           region=article[0][4],
                           content=article[0][5],
                           created_at=article[0][6],
                           type=article[0][7],
                           detailUrl=article[0][8],
                           authorName=article[0][9],
                           authorDetail=article[0][10],
                           commentsList=commentsList,
                           sentimentData=sentimentData,
                           commentRegionData=commentRegionData,
                           time_dates=time_dates,
                           time_counts=time_counts
                           )
