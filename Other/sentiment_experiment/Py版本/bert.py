from utils import load_corpus_bert
import pandas as pd

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

import os
from transformers import BertTokenizer, BertModel

TRAIN_PATH = "./data/weibo2018/train.txt"
TEST_PATH = "./data/weibo2018/test.txt"

# 分别加载训练集和测试集
train_data = load_corpus_bert(TRAIN_PATH)
test_data = load_corpus_bert(TEST_PATH)

df_train = pd.DataFrame(train_data, columns=["text", "label"])
df_test = pd.DataFrame(test_data, columns=["text", "label"])

device = 'cuda' if torch.cuda.is_available() else "cpu"

MODEL_PATH = "bert-base-chinese" 

# 加载
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)   # 分词器
model = BertModel.from_pretrained(MODEL_PATH, num_labels=2)
model.to('cuda')

# 超参数
learning_rate = 1e-3
input_size = 768
num_epoches = 10
batch_size = 100
decay_rate = 0.9

# 数据集
class MyDataset(Dataset):
    def __init__(self, df):
        self.data = df["text"].tolist()
        self.label = df["label"].tolist()

    def __getitem__(self, index):
        data = self.data[index]
        label = self.label[index]
        return data, label

    def __len__(self):
        return len(self.label)

# 训练集
train_data = MyDataset(df_train)
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

# 测试集
test_data = MyDataset(df_test)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=True)

# 网络结构
class Net(nn.Module):
    def __init__(self, input_size):
        super(Net, self).__init__()
        self.fc = nn.Linear(input_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.fc(x)
        out = self.sigmoid(out)
        return out

net = Net(input_size).to(device)

from sklearn import metrics

# 测试集效果检验
def test():
    y_pred, y_true = [], []

    with torch.no_grad():
        for words, labels in test_loader:
            tokens = tokenizer(words, padding=True)
            input_ids = torch.tensor(tokens["input_ids"]).to(device)
            attention_mask = torch.tensor(tokens["attention_mask"]).to(device)
            labels = labels.float().to(device)

            last_hidden_states = model(input_ids, attention_mask=attention_mask)
            bert_output = last_hidden_states[0][:, 0]
            outputs = net(bert_output)          # 前向传播
            outputs = outputs.view(-1)          # 将输出展平
            y_pred.append(outputs.cpu())        # 确保移动到 CPU
            y_true.append(labels.cpu())         # 确保移动到 CPU

    y_prob = torch.cat(y_pred).numpy()          # 转换为 NumPy 数组
    y_true = torch.cat(y_true).numpy()          # 转换为 NumPy 数组
    y_pred = y_prob.copy()                      # 创建一个副本
    y_pred[y_pred > 0.5] = 1
    y_pred[y_pred <= 0.5] = 0
    
    print(metrics.classification_report(y_true, y_pred, digits=3))
    print(f"准确率: {metrics.accuracy_score(y_true, y_pred):.3f}")
    print("AUC:", metrics.roc_auc_score(y_true, y_prob))

# 定义损失函数和优化器
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)
scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=decay_rate)

# 迭代训练
for epoch in range(num_epoches):
    total_loss = 0
    for i, (words, labels) in enumerate(train_loader):
        tokens = tokenizer(words, padding=True)
        input_ids = torch.tensor(tokens["input_ids"]).to(device)
        attention_mask = torch.tensor(tokens["attention_mask"]).to(device)
        labels = labels.float().to(device)
        with torch.no_grad():
            last_hidden_states = model(input_ids, attention_mask=attention_mask)
            bert_output = last_hidden_states[0][:, 0]
        optimizer.zero_grad()               # 梯度清零
        outputs = net(bert_output)          # 前向传播
        logits = outputs.view(-1)           # 将输出展平
        loss = criterion(logits, labels)    # loss计算
        total_loss += loss
        loss.backward()                     # 反向传播，计算梯度
        optimizer.step()                    # 梯度更新
        if (i+1) % 10 == 0:
            print("epoch:{}, step:{}, loss:{}".format(epoch+1, i+1, total_loss/10))
            total_loss = 0
    
    # learning_rate decay
    scheduler.step()
    
    # test
    test()
    
    # save model
    model_path = "./model/bert_dnn_{}.model".format(epoch+1)
    torch.save(net, model_path)
    print("saved model: ", model_path)