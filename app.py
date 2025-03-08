from flask import Flask,session,request,redirect,render_template
import re
from flask_socketio import SocketIO, emit
from views.page import page
from views.user import user

app = Flask(__name__)
app.secret_key = 'this is secret_key you know ?'

socketio = SocketIO(app)

app.register_blueprint(page.page_app)
app.register_blueprint(user.ub)


@app.route('/')
def hello_world():  # put application's code here
    return redirect('http://127.0.0.1:5000/user/login')

@app.before_request
def before_reuqest():
    pat = re.compile(r'^/static')
    if re.search(pat,request.path):return
    elif request.path == '/user/login' or request.path == '/user/register':return
    elif session.get('username'):return
    return redirect('/user/login')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('404.html')

if __name__ == '__main__':
    # app.run()
    # socketio.run(app)
    app.run(debug=True, host='0.0.0.0', port='5000')
