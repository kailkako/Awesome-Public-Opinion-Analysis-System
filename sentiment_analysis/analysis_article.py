import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm  # 导入tqdm

# 模型和分词器所在的文件夹路径
model_directory = 'bert-base-chinese'

# 读取数据
csv_file = '../spiders/articleData.csv'
df = pd.read_csv(csv_file)

# 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory, num_labels=3)
model.eval()  # 将模型设置为评估模式

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


def main():
    # 创建数据加载器
    text_dataset = TextDataset(df['content'].tolist())  # 使用 'content' 列
    # text_loader = DataLoader(text_dataset, batch_size=80, num_workers=32)  # gpu-使用多个工作进程
    text_loader = DataLoader(text_dataset, batch_size=1) # cpu-用这行

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
    label_map = {0: '负面', 1: '中性', 2: '正面'}
    text_labels = [label_map[pred] for pred in predictions]

    # 将预测结果添加到DataFrame
    df['sentiment'] = text_labels

    # 保存预测结果到新的CSV文件
    df.to_csv('analysis_article.csv', index=False)


if __name__ == '__main__':
    main()
