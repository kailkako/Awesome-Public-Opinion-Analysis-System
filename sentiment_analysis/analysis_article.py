# Copyright 2025 kailkako/Awesome-Public-Opinion-Analysis-System made by Licheng Yu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==================================================================
# analysis_article.py
# Description: 实现对文章内容的情感分析
# ==================================================================

import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm  # 导入tqdm

# 模型和分词器所在的文件夹路径
model_directory = 'google-bert/bert-base-chinese'

# 读取数据
csv_file = '../spiders/articleData.csv'
df = pd.read_csv(csv_file)

# 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory, ignore_mismatched_sizes=True, num_labels=2)
model.eval()  # 将模型设置为评估模式，在评估模式下，模型会关闭一些在训练时使用的特殊层（如 Dropout），以确保预测结果的稳定性。

# 检查是否有可用的GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 自定义一个数据集类1
class TextDataset(Dataset):
    def __init__(self, texts):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt") #对输入的文本进行分词和编码，长文本截断，短文本填充
        
    def __len__(self):
        return len(self.encodings.input_ids)  # 返回数据集长度

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}  # 根据索引获取数据集中的一个样本
        return item

# 启动文章情感分析
def main():
    # 创建数据加载器，将 df 中 content 列的数据转换为列表并传入
    text_dataset = TextDataset(df['content'].tolist())  # 使用 'content' 列

    # 若使用GPU，则设置多个工作进程，：
    # text_loader = DataLoader(text_dataset, batch_size=80, num_workers=32)
    
    # 使用cpu：将 text_dataset 封装成可迭代的数据加载器。batch_size=1 表示每次处理一个样本，适用于CPU环境。
    text_loader = DataLoader(text_dataset, batch_size=1) 


    # 预测函数
    def predict(loader):
        model.eval()
        predictions = []
        with torch.no_grad():
            for batch in tqdm(loader, desc="Predicting"):  # 使用tqdm添加进度条
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1)
                predictions.extend(preds.cpu().numpy())
        return predictions

    # 进行预测
    predictions = predict(text_loader)

    # 将数值标签映射为文本标签
    label_map = {0: '负面', 1: '正面'}
    text_labels = [label_map[pred] for pred in predictions]

    # 将预测结果添加到DataFrame
    df['sentiment'] = text_labels

    # 保存预测结果到新的CSV文件
    df.to_csv('analysis_article.csv', index=False)

if __name__ == '__main__':
    main()
