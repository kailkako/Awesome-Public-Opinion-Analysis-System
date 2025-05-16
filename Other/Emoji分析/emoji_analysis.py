import pandas as pd
import regex as re
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.font_manager as fm

# emoji计数-通过re实现
# 参考：https://segmentfault.com/a/1190000007594620
def count_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002600-\U000027BF"  # miscellaneous symbols
                               u"\U00002B50"             # star
                               "]+")
    emojis = emoji_pattern.findall(text)
    return emojis

df = pd.read_csv('D:\\VS_Project\\VS_Py_Project\\暂时觉得可用的\前段时间对英文数据集的一顿分析\\article.csv')  # 读取数据
# 统计所有推文中emoji表情的出现次数
all_emojis = df['content'].apply(count_emojis).sum()
emoji_counts = dict(Counter(all_emojis))

# 提取emoji和对应的出现次数（存在字典中），按出现次数降序排列
sorted_emojis = sorted(emoji_counts.items(), key=lambda x: x[1], reverse=True)
top_emojis = dict(sorted_emojis[:20])  # 切片，取出现次数最多的前20种

# 画图
plt.figure(figsize=(12, 7))
colors = plt.cm.tab20c.colors  # 配色
bars = plt.bar(top_emojis.keys(), top_emojis.values(), color=colors)
plt.rcParams['font.sans-serif'] = ['Segoe UI Emoji']  #  Windows显示emoji

from matplotlib.font_manager import FontProperties
font_chinese = FontProperties(fname=r"c:\\windows\\fonts\\msyh.ttc") 

plt.title('爬取的微博舆情文本中出现频率最高的二十个表情', fontproperties=font_chinese, fontsize=16, weight='bold')
plt.xlabel('表情', fontproperties=font_chinese, fontsize=14, weight='bold')
plt.ylabel('出现频率', fontproperties=font_chinese, fontsize=14, weight='bold')
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()  # 自动调整布局，防止文字显示不全
plt.show()
