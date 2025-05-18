import pandas as pd
from sklearn import metrics
from utils import load_corpus, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

TRAIN_PATH = "./data/weibo_dataset/train.txt"
TEST_PATH = "./data/weibo_dataset/test.txt"

# 分别加载训练集和测试集
train_data = load_corpus(TRAIN_PATH)
test_data = load_corpus(TEST_PATH)

df_train = pd.DataFrame(train_data, columns=["words", "label"])
df_test = pd.DataFrame(test_data, columns=["words", "label"])

# TF-IDF 向量化文本数据
tfidf_vectorizer = TfidfVectorizer(
    token_pattern=r'(?u)\b\w\w+\b',  # 匹配两个及以上字符的词
    stop_words=stopwords
)
X_train = tfidf_vectorizer.fit_transform(df_train["words"])
y_train = df_train["label"]

X_test = tfidf_vectorizer.transform(df_test["words"])
y_test = df_test["label"]

# 定义并训练逻辑回归模型
model = LogisticRegression(
    max_iter=1000,
    solver='lbfgs',
    C=1.0,
    class_weight='balanced'  # 自动调整类别权重
)

model.fit(X_train, y_train)

# 预测并评估
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # 获取正类概率，用于计算AUC

print(metrics.classification_report(y_test, y_pred, digits=3))
print("准确率:", metrics.accuracy_score(y_test, y_pred))
print("AUC:", metrics.roc_auc_score(y_test, y_prob))