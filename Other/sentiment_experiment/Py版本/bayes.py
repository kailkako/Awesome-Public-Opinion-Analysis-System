import pandas as pd
from utils import load_corpus, stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics

TRAIN_PATH = "./data/weibo_dataset/train.txt"
TEST_PATH = "./data/weibo_dataset/test.txt"

# 分别加载训练集和测试集
train_data = load_corpus(TRAIN_PATH)
test_data = load_corpus(TEST_PATH)

df_train = pd.DataFrame(train_data, columns=["words", "label"])
df_test = pd.DataFrame(test_data, columns=["words", "label"])

vectorizer = CountVectorizer(token_pattern='\[?\w+\]?', 
                             stop_words=stopwords)
X_train = vectorizer.fit_transform(df_train["words"])
y_train = df_train["label"]

X_test = vectorizer.transform(df_test["words"])
y_test = df_test["label"]

clf = MultinomialNB()
clf.fit(X_train, y_train)

# 在测试集上用模型预测结果
y_pred = clf.predict(X_test)

print(metrics.classification_report(y_test, y_pred, digits=3))
print("准确率:", metrics.accuracy_score(y_test, y_pred))

auc_score = metrics.roc_auc_score(y_test, y_pred)
print("AUC:", auc_score)