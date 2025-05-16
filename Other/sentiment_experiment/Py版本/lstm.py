import pandas as pd
from utils import load_corpus, stopwords
from gensim import models

TRAIN_PATH = "./data/weibo_dataset/train.txt"
TEST_PATH = "./data/weibo_dataset/test.txt"

# 分别加载训练集和测试集
train_data = load_corpus(TRAIN_PATH)
test_data = load_corpus(TEST_PATH)

df_train = pd.DataFrame(train_data, columns=["text", "label"])
df_test = pd.DataFrame(test_data, columns=["text", "label"])

# word2vec要求的输入格式: list(word)
wv_input = df_train['text'].map(lambda s: s.split(" "))   # [for w in s.split(" ") if w not in stopwords]                       

# Word2Vec
word2vec = models.Word2Vec(wv_input, 
                           vector_size=64,   # 词向量维度
                           min_count=1,      # 最小词频, 因为数据量较小, 这里卡1
                           epochs=1000)      # 迭代轮次

import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence,pad_packed_sequence
from torch.utils.data import Dataset, DataLoader
from sklearn import metrics

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# 超参数
learning_rate = 5e-4
input_size = 768
num_epoches = 3
batch_size = 100
embed_size = 64
hidden_size = 64
num_layers = 2


# 数据集
class MyDataset(Dataset):
    def __init__(self, df):
        self.data = []
        self.label = df["label"].tolist()
        for s in df["text"].tolist():
            vectors = []
            for w in s.split(" "):
                if w in word2vec.wv.key_to_index:
                    vectors.append(word2vec.wv[w])   # 将每个词替换为对应的词向量
            vectors = torch.Tensor(vectors)
            self.data.append(vectors)
    
    def __getitem__(self, index):
        data = self.data[index]
        label = self.label[index]
        return data, label

    def __len__(self):
        return len(self.label)

def collate_fn(data):
    """
    :param data: 第0维-data 第1维-label
    :return: 序列化的data、记录实际长度的序列、以及label列表
    """
    data.sort(key=lambda x: len(x[0]), reverse=True) # pack_padded_sequence要求要按照序列的长度倒序排列
    data_length = [len(sq[0]) for sq in data]
    x = [i[0] for i in data]
    y = [i[1] for i in data]
    data = pad_sequence(x, batch_first=True, padding_value=0)   # 用RNN处理变长序列的必要操作
    return data, torch.tensor(y, dtype=torch.float32), data_length


# 训练集
train_data = MyDataset(df_train)
train_loader = DataLoader(train_data, batch_size=batch_size, collate_fn=collate_fn, shuffle=True)

# 测试集
test_data = MyDataset(df_test)
test_loader = DataLoader(test_data, batch_size=batch_size, collate_fn=collate_fn, shuffle=True)

# 网络结构
class LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, 1)  # 双向, 输出维度要*2
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, lengths):
        h0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(device)  # 双向, 第一个维度要*2
        c0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(device)
        
        packed_input = torch.nn.utils.rnn.pack_padded_sequence(input=x, lengths=lengths, batch_first=True)
        packed_out, (h_n, h_c) = self.lstm(packed_input, (h0, c0))

        lstm_out = torch.cat([h_n[-2], h_n[-1]], 1)  # 双向, 所以要将最后两维拼接, 得到的就是最后一个time step的输出
        out = self.fc(lstm_out)
        out = self.sigmoid(out)
        return out

lstm = LSTM(embed_size, hidden_size, num_layers)

# 在测试集效果检验
def test():
    y_pred, y_true = [], []

    with torch.no_grad():
        for x, labels, lengths in test_loader:
            x = x.to(device)
            outputs = lstm(x, lengths)          # 前向传播
            outputs = outputs.view(-1)          # 将输出展平
            y_pred.append(outputs)
            y_true.append(labels)

    y_prob = torch.cat(y_pred)
    y_true = torch.cat(y_true)
    y_pred = y_prob.clone()
    y_pred[y_pred > 0.5] = 1
    y_pred[y_pred <= 0.5] = 0
    
    print(metrics.classification_report(y_true, y_pred, digits=3))
    print("准确率: {:.3f}".format(metrics.accuracy_score(y_true, y_pred)))
    print("AUC:", metrics.roc_auc_score(y_true, y_prob) )

    # 定义损失函数和优化器
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(lstm.parameters(), lr=learning_rate)

# 迭代训练
for epoch in range(num_epoches):
    total_loss = 0
    for i, (x, labels, lengths) in enumerate(train_loader):
        x = x.to(device)
        labels = labels.to(device)
        outputs = lstm(x, lengths)          # 前向传播
        logits = outputs.view(-1)           # 将输出展平
        loss = criterion(logits, labels)    # loss计算
        total_loss += loss
        optimizer.zero_grad()               # 梯度清零
        loss.backward(retain_graph=True)    # 反向传播，计算梯度
        optimizer.step()                    # 梯度更新
        if (i+1) % 10 == 0:
            print("epoch:{}, step:{}, loss:{}".format(epoch+1, i+1, total_loss/10))
            total_loss = 0
    
    # test
    test()
    
    # save model
    model_path = "./model/lstm_{}.model".format(epoch+1)
    torch.save(lstm, model_path)
    print("saved model: ", model_path)