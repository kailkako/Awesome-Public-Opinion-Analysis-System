import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")

# 设置中文字体，确保可以显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 选择中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 加载中文停用词
def load_stopwords(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return set(line.strip() for line in file)

# 读取数据
data = pd.read_csv('article.csv', encoding='utf-8')  # 导入数据
documents = data['content'].dropna().tolist()  # 提取text类信息的主题
stopwords = load_stopwords('stopWords.txt')  # 加载停用词

# 中文分词 & 去停用词
processed_docs = []
for text in documents:
    words = [w for w in jieba.cut(text) if w.strip() and w not in stopwords]
    processed_docs.append(" ".join(words))  # 拼接为一个字符串

# 将文本数据转换为TF-IDF特征表示
vectorizer = TfidfVectorizer(stop_words=None)  # 不使用英文停用词
X = vectorizer.fit_transform(processed_docs)

feature_names = vectorizer.get_feature_names_out()
n_top_words = 10  # 定义每个主题中要显示的前N个关键词数量

# NMF主题提取
nmf = NMF(n_components=6, random_state=42)
nmf_topics = nmf.fit_transform(X)

# 输出NMF主题下的关键词
print("\nNMF Top Topics:")
for topic_idx, topic in enumerate(nmf.components_):
    top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
    top_features = [feature_names[i] for i in top_features_ind]
    print(f"Topic {topic_idx+1}:")
    print(", ".join(top_features))

# # NMF主题分布聚类图
plt.figure(figsize=(12, 6))
for i in range(nmf_topics.shape[1]):
    plt.scatter(nmf_topics[:, i], range(len(nmf_topics)), label=f"主题 {i+1}")
plt.title('NMF 主题聚类')  # NMF聚类图标题
plt.xlabel('主题贡献度')  # X轴标签
plt.ylabel('文档')  # Y轴标签
plt.legend(title='主题')  # 图例标题

# 显示图形
plt.tight_layout()
plt.show()
