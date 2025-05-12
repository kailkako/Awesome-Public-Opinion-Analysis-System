import os
import time
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import logging
from datasets import load_dataset

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 配置类
class Config:
    MAX_LEN = 128
    BATCH_SIZE = 16
    LEARNING_RATE = 1e-5
    EPOCHS = 3
    MODEL_PATH = 'google-bert/bert-base-chinese'
    SAVE_PATH = './BERT_Finetune'

if not os.path.exists(Config.SAVE_PATH):
    os.makedirs(Config.SAVE_PATH)

# 初始化 tokenizer 和模型
tokenizer = BertTokenizer.from_pretrained(Config.MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(Config.MODEL_PATH, num_labels=2)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

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

# 加载数据集
ds = load_dataset("dirtycomputer/weibo_senti_100k")
try:
    df = pd.DataFrame(ds['train'])
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
except Exception as e:
    logging.error(f"Error reading the data file: {e}")
    raise e

# 构建 Dataset 和 DataLoader
train_dataset = ChineseTextDataset(
    df_train['review'].tolist(),
    df_train['label'].tolist(),
    tokenizer,
    Config.MAX_LEN
)
test_dataset = ChineseTextDataset(
    df_test['review'].tolist(),
    df_test['label'].tolist(),
    tokenizer,
    Config.MAX_LEN
)

train_loader = DataLoader(train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=Config.BATCH_SIZE)

optimizer = AdamW(model.parameters(), lr=Config.LEARNING_RATE)

# 训练函数
def train_epoch(model, data_loader, optimizer, device, epoch):
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

        if (step + 1) % 100 == 0:
            logging.info(
                f'Step {step + 1}/{len(data_loader)}, Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}, '
                f'Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}'
            )

    return accuracy, total_loss / len(data_loader), precision, recall, f1

# ========= 开始训练并计时 =========
start_time = time.time()

for epoch in range(Config.EPOCHS):
    accuracy, train_loss, precision, recall, f1 = train_epoch(model, train_loader, optimizer, device, epoch)
    logging.info(
        f'Epoch {epoch + 1}, Loss: {train_loss:.4f}, Accuracy: {accuracy:.4f}, '
        f'Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}'
    )

end_time = time.time()
total_time = end_time - start_time
logging.info(f'Total training time: {total_time:.2f} seconds')

def evaluate(model, data_loader, device):
    model.eval()
    total_correct = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            _, preds = torch.max(outputs.logits, dim=1)
            total_correct += torch.sum(preds == labels).item()

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = total_correct / len(data_loader.dataset)
    precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)

    return accuracy, precision, recall, f1

evaluate_accuracy, evaluate_precision, evaluate_recall, evaluate_f1 = evaluate(model, test_loader, device)
logging.info(
    f'Evaluation Results: Accuracy: {evaluate_accuracy:.4f}, Precision: {evaluate_precision:.4f}, '
    f'Recall: {evaluate_recall:.4f}, F1 Score: {evaluate_f1:.4f}'
)

# ========= 保存模型和 tokenizer =========
model.save_pretrained(Config.SAVE_PATH)
tokenizer.save_pretrained(Config.SAVE_PATH)
