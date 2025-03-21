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
# main.py
# Description: 爬虫和情感分析主入口，调用爬虫模块和情感分析模块进行处理
# ==================================================================

from globalVariable import *
from utils.databaseManage import *
from .spiderContent import start as spiderContentStart                      # 批量爬取文章数据  
from .spiderContent import start_2 as spidertargetContentStart              # 指定单篇文章爬取数据
from .spiderComments import start as spiderCommentsStart                    # 爬取评论数据
from sentiment_analysis.analysis_comments import main as sentimentAnalysis  # 情感分析

# 对csv文件中的内容去重
def remove_duplicates_from_csv(input_csv_path, output_csv_path, unique_column):
    df = pd.read_csv(input_csv_path)
    # 删除重复行，保留最后出现的行
    df.drop_duplicates(subset=[unique_column], keep='last', inplace=True)
    # 保存去重后的数据到新的CSV文件
    df.to_csv(output_csv_path, index=False)

# 文章批量爬取+情感分析
def main(types=[], page=0):
    # 文件路径初始化
    articleCategoryFilePath, articleDataFilePath, articleCommentsFilePath = initGlobalVariable()
    print('开始爬取文章数据')
    spiderContentStart(types, page, articleCategoryFilePath, articleDataFilePath)
    print('文章数据爬取完毕')
    remove_duplicates_from_csv(articleDataFilePath,articleDataFilePath,'id')

    print('开始爬取文章评论数据')
    spiderCommentsStart(articleDataFilePath,articleCommentsFilePath)
    print('文章评论数据爬取完毕')

    print('开始分析评论情感')
    sentimentAnalysis(articleCommentsFilePath)
    emotion_ratio(articleDataFilePath, articleCommentsFilePath)
    print('情感分析结束')

    print('开始存储数据')
    save_to_sql(articleDataFilePath,articleCommentsFilePath)
    save_to_sql_temp(articleDataFilePath, articleCommentsFilePath)
    print('存储数据完毕')
    return True

# 指定单篇文章爬取+情感分析
def main_2(url,type):
    # 文件路径初始化
    articleCategoryFilePath, articleDataFilePath, articleCommentsFilePath = initGlobalVariable()
    print('开始爬取文章数据')
    articleId=spidertargetContentStart(url,articleDataFilePath,type)
    print('文章数据爬取完毕')

    print('开始爬取文章评论数据')
    spiderCommentsStart(articleDataFilePath, articleCommentsFilePath)
    print('文章评论数据爬取完毕')

    print('开始分析评论情感')
    sentimentAnalysis(articleCommentsFilePath)
    emotion_ratio(articleDataFilePath, articleCommentsFilePath)
    print('情感分析结束')

    print('开始存储数据')
    save_to_article(articleDataFilePath, articleCommentsFilePath, articleId)
    print('存储数据完毕')
    return articleId

# 情感分析
def emotion_ratio(articleDataFilePath, articleCommentsFilePath):
    # 读取comments CSV文件
    comments_df = pd.read_csv(articleCommentsFilePath)

    # 使用groupby和value_counts来统计每个articleId下的每种情绪的个数
    sentiment_counts = comments_df.groupby('articleId')['sentiment'].value_counts().unstack(fill_value=0)

    # 计算每个articleId的总评论数
    total_counts = sentiment_counts.sum(axis=1)

    # 计算情绪的占比
    positive_ratio = (sentiment_counts.get('积极', 0) / total_counts * 100).round(2)
    neutral_ratio = (sentiment_counts.get('中性', 0) / total_counts * 100).round(2)
    negative_ratio = (sentiment_counts.get('消极', 0) / total_counts * 100).round(2)

    # 将情绪占比添加到 sentiment_counts DataFrame 中
    sentiment_counts['negative_ratio'] = negative_ratio
    sentiment_counts['neutral_ratio'] = neutral_ratio
    sentiment_counts['positive_ratio'] = positive_ratio

    # 确定每个articleId的主情绪类别
    sentiment_counts['emotion'] = sentiment_counts[['negative_ratio', 'neutral_ratio', 'positive_ratio']].idxmax(axis=1)
    sentiment_counts['emotion'] = sentiment_counts['emotion'].map({
        'negative_ratio': '消极',
        'neutral_ratio': '中性',
        'positive_ratio': '积极'
    })

    # 读取article CSV文件
    article_df = pd.read_csv(articleDataFilePath)

    # 将 sentiment_counts 中的情绪占比数据和主情绪类别合并到 article_df 中
    article_df = article_df.merge(sentiment_counts[['negative_ratio', 'neutral_ratio', 'positive_ratio', 'emotion']],
                                  left_on='id', right_index=True, how='left')

    # 如果某些文章没有对应的情绪数据，将占比填充为0，并设置emotion为'未知'
    article_df[['negative_ratio', 'neutral_ratio', 'positive_ratio']] = article_df[['negative_ratio', 'neutral_ratio', 'positive_ratio']].fillna(0)
    article_df['emotion'] = article_df['emotion'].fillna('未知')

    # 将更新后的数据保存到新的 CSV 文件
    article_df.to_csv(articleDataFilePath, index=False)

    return article_df