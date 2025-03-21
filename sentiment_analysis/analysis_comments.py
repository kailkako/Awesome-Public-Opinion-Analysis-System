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
# analysis_comments.py
# Description: 实现对评论的情感分析
# ==================================================================

import torch
import pandas as pd
from tqdm import tqdm 
from globalVariable import *
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset

# 模型和分词器所在的文件夹路径
model_directory = 'google-bert/bert-base-chinese'

# 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory, num_labels=3)
model.eval()  # 将模型设置为评估模式，在评估模式下，模型会关闭一些在训练时使用的特殊层（如 Dropout），以确保预测结果的稳定性。

# 检查是否有可用的GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


class TextDataset(Dataset):
    def __init__(self, texts):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")

    def __len__(self):
        return len(self.encodings.input_ids)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        return item

def main(articleCommentsFilePath):
    # 读取数据
    df = pd.read_csv(articleCommentsFilePath)

    # 创建数据加载器，将 df 中 content 列的数据转换为列表并传入
    text_dataset = TextDataset(df['content'].tolist())  # 使用 'content' 列

    # 若使用GPU，则设置多个工作进程：
    # text_loader = DataLoader(text_dataset, batch_size=80, num_workers=24)

    # 使用cpu：将 text_dataset 封装成可迭代的数据加载器。batch_size=1 表示每次处理一个样本，适用于CPU环境。
    text_loader = DataLoader(text_dataset, batch_size=1) 

    # 预测函数
    def predict(loader):
        model.eval()
        predictions = []
        with torch.no_grad(): # 在预测阶段，不需要计算梯度，关闭梯度计算可以减少内存消耗，提高计算速度。
            for batch in tqdm(loader, desc="Predicting"):  # 添加进度条，遍历 loader 中的每个批次数据。
                batch = {k: v.to(device) for k, v in batch.items()}  # 将批次数据中的每个张量移动到指定的设备（CPU 或 GPU）上。
                outputs = model(**batch) 
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1) # 使用 torch.argmax 函数找到 logits 中每个样本的最大值索引，作为预测的类别标签。
                predictions.extend(preds.cpu().numpy()) # 将预测结果从 GPU 移动到 CPU，并转换为 NumPy 数组，然后添加到 predictions 列表中。
        return predictions

    # 进行预测
    predictions = predict(text_loader)

    # 将数值标签映射为文本标签
    label_map = {0: '消极', 1: '中性', 2: '积极'}
    text_labels = [label_map[pred] for pred in predictions]

    # 将预测结果添加到DataFrame
    df['sentiment'] = text_labels

    # 保存预测结果到新的CSV文件
    df.to_csv(articleCommentsFilePath, index=False)


if __name__ == '__main__':
    main()
