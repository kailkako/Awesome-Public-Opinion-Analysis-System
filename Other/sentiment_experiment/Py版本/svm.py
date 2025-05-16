import pandas as pd
from sklearn import svm
from sklearn import metrics
from utils import load_corpus, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

TRAIN_PATH = "./data/weibo_dataset/train.txt"
TEST_PATH = "./data/weibo_dataset/test.txt"

# 分别加载训练集和测试集
train_data = load_corpus(TRAIN_PATH)
test_data = load_corpus(TEST_PATH)

df_train = pd.DataFrame(train_data, columns=["words", "label"])
df_test = pd.DataFrame(test_data, columns=["words", "label"])

vectorizer = TfidfVectorizer(token_pattern='\[?\w+\]?', 
                             stop_words=stopwords)
X_train = vectorizer.fit_transform(df_train["words"])
y_train = df_train["label"]

X_test = vectorizer.transform(df_test["words"])
y_test = df_test["label"]

clf = svm.SVC()
clf.fit(X_train, y_train)

# 在测试集上用模型预测结果
y_pred = clf.predict(X_test)

# 测试集效果检验
print(metrics.classification_report(y_test, y_pred, digits=3))
print("准确率: {:.3f}".format(metrics.accuracy_score(y_test, y_pred)))

auc_score = metrics.roc_auc_score(y_test, y_pred)
print("AUC:", auc_score)