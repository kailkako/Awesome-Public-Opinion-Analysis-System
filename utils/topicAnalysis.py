import json
import matplotlib.pyplot as plt
import requests
from wordcloud import WordCloud
from globalVariable import headers


def getCiTiaoList():
    response = requests.get('https://weibo.com/ajax/side/hotSearch', headers=headers)
    text = response.json()
    realtime_list = text['data']['realtime']
    word_scheme_list = [entry['word_scheme'].strip('#') for entry in realtime_list if 'word_scheme' in entry]
    return word_scheme_list[:20]


def getWeiboAI(topicName):
    response = requests.get('https://ai.s.weibo.com/api/llm/analysis_tab.json?query=' + topicName, headers=headers)
    content = response.json()
    data = content['data']
    description = data['past_events']['desc']
    description_list = description.split('\n')
    emotion = data['stars']['desc']
    word_cloud = data['word_cloud']['desc']
    typical_viewpoint = data['typical_viewpoint']['desc']
    typical_viewpoint_list = typical_viewpoint.split('\n')
    return description_list, emotion, word_cloud, typical_viewpoint_list


def generate_wordcloud(data, topicName):
    # 将 JSON 字符串转换为 Python 对象
    data_list = json.loads(data)
    # 创建词频字典
    word_freq = {item['name']: item['value'] for item in data_list}
    # 生成词云
    wordcloud = WordCloud(font_path='msyh.ttc', width=800, height=400,
                          background_color='white').generate_from_frequencies(word_freq)
    # 保存词云图
    wordCloudPath='static/WordCloud_toplc/' + topicName + '.png'
    wordcloud.to_file(wordCloudPath)
    return True


def getCharData(data_str):
    data = json.loads(data_str)
    names = [item['name'] for item in data]
    nums = [item['num'] for item in data]
    print(names)
    print(nums)
    return names, nums


# if __name__ == '__main__':
#     # ciTiaoList = getCiTiaoList()
#     # topicName = '伊朗总统遇难'
#     # description, emotion, word_cloud, typical_viewpoint = getWeiboAI(topicName)
#     # generate_wordcloud(word_cloud, topicName)
#
#     data = [
#         {"dark_color": "#86BD6F", "num": 55, "name": "恐惧", "val": 55, "show": 1, "color": "#A8ED8B"},
#         {"dark_color": "#928BCB", "num": 22, "name": "悲伤", "val": 22, "show": 1, "color": "#B7AEFE"},
#         {"dark_color": "#74ADB1", "num": 14, "name": "平和", "val": 14, "show": 1, "color": "#91D9DE"},
#         {"dark_color": "#7490B1", "num": 6, "name": "疑惑", "val": 6, "show": 1, "color": "#91B5DE"},
#         {"dark_color": "#CC7979", "num": 2, "name": "生气", "val": 2, "show": 1, "color": "#FF9898"},
#         {"dark_color": "#B4B65D", "num": 1, "name": "感动", "val": 1, "show": 1, "color": "#E2E475"}
#     ]
#     getCharData(data)