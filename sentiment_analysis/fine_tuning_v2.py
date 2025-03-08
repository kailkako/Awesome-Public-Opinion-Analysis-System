import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import logging

# 使用transformers库进行中文文本分类任务的标准流程，包括数据预处理、模型加载、训练、评估及模型保存。


# 日志配置
# 设置日志级别为INFO，更低级别的消息（如 DEBUG）将被忽略。格式化日志输出，包含时间、级别和消息。
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 配置类
# Config类用于集中管理训练配置信息，方便后续引用和修改
class Config:
    MAX_LEN = 128
    BATCH_SIZE = 20
    LEARNING_RATE = 2e-5
    EPOCHS = 5
    MODEL_PATH = 'bert-base-chinese'
    DATA_FILE = './data.csv'
    SAVE_PATH = './train_info'


if not os.path.exists(Config.SAVE_PATH):
    # 如果目录不存在，创建它
    os.makedirs(Config.SAVE_PATH)

# 初始化和模型加载
# 使用指定路径加载BERT的分词器和预训练模型，并将模型移至GPU以加速训练。
tokenizer = BertTokenizer.from_pretrained(Config.MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(Config.MODEL_PATH, num_labels=3)
model.to('cuda')


# 自定义数据集类
# 定义了一个处理中文文本数据的Dataset子类，包括数据加载、编码、填充等预处理步骤。
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
# 读取CSV文件，使用train_test_split分割训练集和测试集，并异常处理确保数据读取成功。
try:
    df = pd.read_csv(Config.DATA_FILE, encoding='utf-8')
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
except Exception as e:
    logging.error(f"Error reading the data file: {e}")
    raise e

# 数据加载器
# 创建训练和测试数据集实例，以及对应的DataLoader用于迭代数据。
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
# 优化器设置
# 使用AdamW优化器配置模型参数更新策略。
optimizer = AdamW(model.parameters(), lr=Config.LEARNING_RATE)


# 训练函数
# 实现了一个训练单个epoch的函数，计算损失、精度、召回率和F1分数。
def train_epoch(model, data_loader, optimizer, device):
    model.train()
    total_loss = 0
    total_correct = 0
    all_preds = []
    all_labels = []
    for batch in data_loader:
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

        # Collect predictions and labels to compute additional metrics
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    accuracy = total_correct / len(data_loader.dataset)
    precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    return accuracy, total_loss / len(data_loader), precision, recall, f1


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# 训练循环
# 循环遍历配置的epoch数，调用train_epoch函数进行训练，并记录训练日志。
for epoch in range(Config.EPOCHS):
    accuracy, train_loss, precision, recall, f1 = train_epoch(model, train_loader, optimizer, device)
    logging.info(
        f'Epoch {epoch + 1}, Loss: {train_loss:.4f}, Accuracy: {accuracy:.4f}, '
        f'Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}'
    )

# 模型保存
# 保存训练好的模型参数、分词器到指定目录，并且额外保存模型的状态字典。
model_directory = Config.SAVE_PATH
model.save_pretrained(model_directory)
tokenizer.save_pretrained(model_directory)
torch.save(model.state_dict(), model_directory + r'\pytorch_model.bin')
