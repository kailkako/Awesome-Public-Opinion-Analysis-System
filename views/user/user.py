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

# =======================================================================================
# user.py
# Description: 定义了一个名为 ub的 Blueprint，用于处理用户的登录、注册和注销功能
# =======================================================================================

from flask import Flask,session,render_template,redirect,Blueprint,request
from utils.databaseManage import query
import time
from utils.errorResponse import errorResponse
ub = Blueprint('user',__name__,url_prefix='/user',template_folder='templates')

@ub.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        def filter_fn(user):
            return request.form['username'] in user and request.form['password'] in user
        users = query('select * from user', [], 'select')
        login_success = list(filter(filter_fn,users))
        if not len(login_success):return errorResponse('账号或密码错误')

        session['username'] = request.form['username']
        return redirect('/page/home')

@ub.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        if request.form['password'] != request.form['checkPassword']:return errorResponse('两次密码不符合')
        def filter_fn(user):
            return request.form['username'] in user

        users = query('select * from user',[],'select')
        filter_list = list(filter(filter_fn,users))
        if len(filter_list):
            return errorResponse('该用户名已被注册')
        else:
            time_tuple = time.localtime(time.time())
            query('''
                insert into user(username,password,createTime) values(%s,%s,%s)
            ''',[request.form['username'],request.form['password'],str(time_tuple[0]) + '-' + str(time_tuple[1]) + '-' + str(time_tuple[2])])

        return redirect('/user/login')

@ub.route('/logOut')
def logOut():
        session.clear()
        return redirect('/user/login')