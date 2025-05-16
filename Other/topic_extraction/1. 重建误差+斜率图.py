import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import numpy as np
import matplotlib.pyplot as plt
import jieba
from matplotlib import rcParams

# 设置 matplotlib 中文字体支持
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
rcParams['axes.unicode_minus'] = False   # 正常显示负号

# 读取中文数据
data = pd.read_csv('article.csv', encoding='utf-8')
documents = data['content'].dropna().tolist()

# 加载中文停用词表
def load_stopwords(filepath='stopWords.txt'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

stopwords = load_stopwords()

# 中文分词函数
def chinese_tokenizer(text):
    return [word for word in jieba.cut(text) if word.strip() and word not in stopwords]

# 使用 TF-IDF 向量化
tfidf_vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer, max_df=0.95, min_df=2)
X = tfidf_vectorizer.fit_transform(documents)

# 定义主题个数范围
min_topics = 2
max_topics = 10

reconstruction_errors = []
slopes = []

# 训练 NMF 模型并记录误差
for num_topics in range(min_topics, max_topics + 1):
    nmf = NMF(n_components=num_topics, random_state=42)
    nmf.fit(X)
    error = nmf.reconstruction_err_
    reconstruction_errors.append(error)

    # 计算斜率（误差变化率）
    if num_topics > min_topics:
        slope = reconstruction_errors[-1] - reconstruction_errors[-2]
        slopes.append(slope)

'''画重建误差图和斜率变化图'''
# 创建两个子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))

# 重建误差图
ax1.plot(range(min_topics, max_topics + 1), reconstruction_errors, marker='o', linestyle='--')
ax1.set_title('重建误差和主题数的关系')
ax1.set_xlabel('主题数')
ax1.set_ylabel('重建误差')
ax1.set_xticks(range(min_topics, max_topics + 1))
ax1.grid(True)

# 斜率图
ax2.plot(range(min_topics + 1, max_topics + 1), slopes, marker='s', color='orange', linestyle='-.')
ax2.set_title('重建误差随主题数的变化率')
ax2.set_xlabel('主题数')
ax2.set_ylabel('重建误差的变化量')
ax2.set_xticks(range(min_topics + 1, max_topics + 1))
ax2.grid(True)

plt.tight_layout()
plt.subplots_adjust(wspace=0.2)  # 增加两个子图之间的水平间距

# '''只画重建误差图 '''
# plt.figure(figsize=(10, 6))
# plt.plot(range(min_topics, max_topics + 1), reconstruction_errors, marker='o', linestyle='--')
# plt.title('NMF 重建误差 vs 主题数')
# plt.xlabel('主题数')
# plt.ylabel('重建误差')
# plt.grid(True)

plt.show()

# 输出最优主题数
best_num_topics = np.argmin(reconstruction_errors) + min_topics
print(f"最优主题个数: {best_num_topics}")
