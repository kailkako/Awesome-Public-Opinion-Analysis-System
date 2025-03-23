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
# wordCloudPicture.py
# Description: 生成文章分析词云图（如需改词云图形状：更换comment.jpg）
# ==================================================================

import jieba
from wordcloud import WordCloud
from PIL import Image
import numpy as np

import matplotlib
matplotlib.use('agg') # 后端渲染或者用'svg'
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def stopwordList():
    with open('utils/stopwords.txt', encoding='utf8') as f:
        return [line.strip() for line in f.readlines()]


def get_img(id, text):
    if not text.strip():  # 检查文本是否为空
        print(f"Text for article {id} is empty. Skipping word cloud generation.")
        return

    targetImgSrc = r'static\comment.jpg'  # 词云图的图形
    resImgSrc = f'static/WordCloud_article/{id}.jpg'

    try:
        # 使用 jieba 对文本进行分词
        cut = jieba.cut(text)
        newCut = [word for word in cut if word not in stopwordList()]

        # 将处理后的词用空格连接成一个字符串
        string = ' '.join(newCut)

        if not string.strip():
            print(f"No valid words to generate word cloud for article {id}.")
            return

        # 打开并处理目标图像
        img = Image.open(targetImgSrc)
        img_arr = np.array(img)

        # 创建词云对象
        wc = WordCloud(
            background_color="#fff",
            mask=img_arr,
            font_path='STHUPO.TTF',
            max_words=1000,  # 显示的最大词数
            max_font_size=150,  # 最大字体大小
            scale=5  # 图像缩放比例
        )

        # 从文本生成词云
        wc.generate_from_text(string)

        # 创建一个 Figure 对象并明确指定画布
        fig = plt.figure(1)
        canvas = FigureCanvas(fig)
        plt.imshow(wc, interpolation="bilinear")
        plt.axis('off')

        # 保存词云图像
        plt.savefig(resImgSrc, dpi=500)
        plt.close(fig)  # 关闭图像，以释放内存

    except Exception as e:
        print(f"Failed to generate word cloud for article {id}: {e}")
