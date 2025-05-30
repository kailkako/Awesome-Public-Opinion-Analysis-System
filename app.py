# Copyright 2025 kailkako/Awesome-Public-Opinion-Analysis-System
# Author：Licheng Yu
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
# app.py
# Description: 整个系统的主应用程序入口，负责初始化Flask应用
# ==================================================================

from flask import Flask, session, request, redirect, render_template
import re
from flask_socketio import SocketIO, emit
from views.page import page
from views.user import user
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'this is secret_key you know ?'  # 为会话数据提供加密

socketio = SocketIO(app)

# 注册blueprint
app.register_blueprint(page.page_app)
app.register_blueprint(user.ub)

# 记录页面总响应时间
@app.before_request
def start_timer():
    """在每个请求开始时记录时间"""
    request.start_time = datetime.now()  # 记录请求的起始时间

@app.after_request
def log_response_time(response):
    """在每个请求结束时计算并记录响应时间"""
    if hasattr(request, 'start_time'):
        total_time = datetime.now() - request.start_time  # 计算从请求到响应的总时间
        print(f"请求路径：{request.path}，方法：{request.method}，总响应时间：{total_time.total_seconds()} 秒")
    return response

@app.route('/')
def login():
    return redirect('http://127.0.0.1:5000/user/login')

@app.before_request
def before_request():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    elif request.path in ['/user/login', '/user/register', '/user/retrieve_pwd']:
        return
    elif session.get('username'):
        return
    return redirect('/user/login')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
