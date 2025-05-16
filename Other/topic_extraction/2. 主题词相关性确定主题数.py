import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
import jieba
from matplotlib import rcParams

# 设置中文字体支持
rcParams['font.sans-serif'] = ['SimHei']  # 可改为 'Microsoft YaHei'，取决于你系统的字体
rcParams['axes.unicode_minus'] = False

# 加载中文停用词
def load_stopwords(filepath='stopWords.txt'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

stopwords = load_stopwords()

# 自定义中文分词器
def chinese_tokenizer(text):
    return [word for word in jieba.cut(text) if word.strip() and word not in stopwords]

# 计算主题相似性
def calculate_topic_similarity(nmf_model):
    topic_similarity = cosine_similarity(nmf_model.components_)
    np.fill_diagonal(topic_similarity, 0)  # 忽略主题与自身的相似度
    return topic_similarity

# 读取中文文本数据
data = pd.read_csv('article.csv', encoding='utf-8')
documents = data['content'].dropna().tolist()

# 构建 TF-IDF 特征表示
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer, max_df=0.95, min_df=2)
tfidf_matrix = vectorizer.fit_transform(documents)

# 设置主题个数范围
min_topics = 3
max_topics = 20

'''最后取相似度最高的主题数作为最优主题数'''
# 评估不同主题数下的平均主题一致性
def evaluate_topic_coherence(tfidf_matrix, min_topics, max_topics):
    coherence_scores = []
    for num_topics in range(min_topics, max_topics + 1):
        nmf_model = NMF(n_components=num_topics, random_state=42)
        nmf_model.fit(tfidf_matrix)
        topic_similarity = calculate_topic_similarity(nmf_model)
        coherence_scores.append(np.mean(topic_similarity))
    return coherence_scores
    
# 计算主题一致性得分
coherence_scores = evaluate_topic_coherence(tfidf_matrix, min_topics, max_topics)

# 输出最佳主题数（取最大平均相似度）
best_num_topics = min_topics + np.argmax(coherence_scores)
print(f"最优主题数: {best_num_topics}")

# 绘制一致性得分变化图
plt.figure(figsize=(10, 6))
plt.plot(range(min_topics, max_topics + 1), coherence_scores, marker='o', linestyle='-')
plt.xlabel('主题个数')
plt.ylabel('平均主题一致性（余弦相似度）')
plt.title('不同主题数下的平均主题一致性评估')
plt.xticks(range(min_topics, max_topics + 1))
plt.grid(True)
plt.tight_layout()
plt.show()


# '''最后取相似度最低的主题数作为最优主题数'''
# # 计算每个主题数下的平均主题“分离度”
# def evaluate_topic_separation(tfidf_matrix, min_topics, max_topics):
#     separation_scores = []
#     for num_topics in range(min_topics, max_topics + 1):
#         nmf_model = NMF(n_components=num_topics, random_state=42)
#         nmf_model.fit(tfidf_matrix)
#         similarity_matrix = calculate_topic_similarity(nmf_model)
#         mean_similarity = np.mean(similarity_matrix)
#         separation_score = 1 - mean_similarity  # 越大表示主题差异越大
#         separation_scores.append(separation_score)
#     return separation_scores

# # 评估主题分离度
# separation_scores = evaluate_topic_separation(tfidf_matrix, min_topics, max_topics)

# # 输出最佳主题数（取最大平均分离度）
# best_num_topics = min_topics + np.argmax(separation_scores)
# print(f"最优主题数（主题最不相似）: {best_num_topics}")

# # 可视化
# plt.figure(figsize=(10, 6))
# plt.plot(range(min_topics, max_topics + 1), separation_scores, marker='o', linestyle='-')
# plt.xlabel('主题个数')
# plt.ylabel('平均主题分离度（1 - 相似度）')
# plt.title('不同主题数下的主题分离度评估')
# plt.xticks(range(min_topics, max_topics + 1))
# plt.grid(True)
# plt.tight_layout()
# plt.show()