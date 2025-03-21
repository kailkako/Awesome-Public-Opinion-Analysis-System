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
# train.py
# Description: 训练
# ==================================================================

import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import logging
from torch.utils.tensorboard import SummaryWriter

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 配置类
class Config:
    MAX_LEN = 128
    BATCH_SIZE = 20
    LEARNING_RATE = 2e-5
    EPOCHS = 5
    MODEL_PATH = 'google-bert/bert-base-chinese'
    DATA_FILE = './data.csv'
    SAVE_PATH = '.save_info'
    LOG_DIR = './tensorboard_logs'

if not os.path.exists(Config.SAVE_PATH):
    os.makedirs(Config.SAVE_PATH)

# 初始化和模型加载
tokenizer = BertTokenizer.from_pretrained(Config.MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(Config.MODEL_PATH, num_labels=3)
model.to('cuda')

# 初始化 TensorBoard Writer
writer = SummaryWriter(Config.LOG_DIR)

# 自定义数据集类
class ChineseTextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# 数据准备与加载
try:
    df = pd.read_csv(Config.DATA_FILE, encoding='utf-8')
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
except Exception as e:
    logging.error(f"Error reading the data file: {e}")
    raise e

train_dataset = ChineseTextDataset(
    df_train['text'].tolist(),
    df_train['label'].tolist(),
    tokenizer,
    Config.MAX_LEN
)
test_dataset = ChineseTextDataset(
    df_test['text'].tolist(),
    df_test['label'].tolist(),
    tokenizer,
    Config.MAX_LEN
)

train_loader = DataLoader(train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=Config.BATCH_SIZE)

optimizer = AdamW(model.parameters(), lr=Config.LEARNING_RATE)

# 训练函数
def train_epoch(model, data_loader, optimizer, device, writer, epoch):
    model.train()
    total_loss = 0
    total_correct = 0
    all_preds = []
    all_labels = []
    for step, batch in enumerate(data_loader):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()
        _, preds = torch.max(outputs.logits, dim=1)
        total_correct += torch.sum(preds == labels).item()

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

        accuracy = total_correct / ((step + 1) * data_loader.batch_size)
        precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
        recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
        f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)

        # 每100个step输出一次
        if (step + 1) % 100 == 0:
            logging.info(
                f'Step {step + 1}/{len(data_loader)}, Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}, '
                f'Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}'
            )

        # 记录到 TensorBoard
        writer.add_scalar('Loss/train', loss.item(), epoch * len(data_loader) + step)
        writer.add_scalar('Accuracy/train', accuracy, epoch * len(data_loader) + step)
        writer.add_scalar('Precision/train', precision, epoch * len(data_loader) + step)
        writer.add_scalar('Recall/train', recall, epoch * len(data_loader) + step)
        writer.add_scalar('F1/train', f1, epoch * len(data_loader) + step)

    return accuracy, total_loss / len(data_loader), precision, recall, f1

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

for epoch in range(Config.EPOCHS):
    accuracy, train_loss, precision, recall, f1 = train_epoch(model, train_loader, optimizer, device, writer, epoch)
    logging.info(
        f'Epoch {epoch + 1}, Loss: {train_loss:.4f}, Accuracy: {accuracy:.4f}, '
        f'Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}'
    )

# 关闭 TensorBoard Writer
writer.close()

model_directory = Config.SAVE_PATH
model.save_pretrained(model_directory)
tokenizer.save_pretrained(model_directory)
torch.save(model.state_dict(), model_directory + r'\pytorch_model.bin')
