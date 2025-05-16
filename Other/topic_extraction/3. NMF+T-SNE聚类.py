import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# 设置中文字体，确保可以显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 选择中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 1. 读取数据
column_name = 'content'
documents = []
with open('article.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        text = row[column_name]
        documents.append(text)

# 2. 训练tfidf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(documents)

# 3. NMF模型
nmf_model = NMF(n_components=6, random_state=42)
W = nmf_model.fit_transform(tfidf)
H = nmf_model.components_

# 输出每个主题的关键词
feature_names = tfidf_vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(H):
    print(f"Topic #{topic_idx + 1}:")
    print([feature_names[i] for i in topic.argsort()[:-7:-1]])

# 4. KMeans聚类和T-SNE可视化
kmeans = KMeans(n_clusters=6, random_state=42)
kmeans.fit(W)
clusters = kmeans.predict(W)

tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
W_tsne = tsne.fit_transform(W)

# 绘制T-SNE聚类结果
plt.figure(figsize=(10, 6))
for i in range(6):  # 图例
    plt.scatter(W_tsne[clusters == i, 0], W_tsne[clusters == i, 1], label=f'聚类 {i+1}')
plt.legend(title='聚类')
plt.title('T-SNE 聚类可视化')
plt.xlabel('T-SNE 组件1')
plt.ylabel('T-SNE 组件2')
plt.show()
