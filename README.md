# Awesome-Public-Opinion-Analysis-System

基于Flask框架的微博舆情分析系统

## Setup

- **数据库准备**

【初始】数据库：新建连接——新建数据库——执行weiboarticles.sql文件；

【已初始化】每次只需要打开数据库连接即可。

- **运行**

```python
conda create --name Weibo_Project python=3.8   # 创建虚拟环境
conda activate Weibo_Project                   # 激活虚拟环境
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```

```python
# clone
git clone https://github.com/kailkako/Awesome-Public-Opinion-Analysis-System.git

# 切换目录
cd Awesome-Public-Opinion-Analysis-System

# 启动
python app.py
```

