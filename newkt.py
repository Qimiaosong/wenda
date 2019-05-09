from flask import Flask, render_template, request, redirect, url_for, session,g
import config
from models import User, Question, Answer
from exts import db
from decorators import login_required
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by(Question.create_time.desc()).all()
        # 'questions': Question.query.all()
    }
    return render_template('index.html', **context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # 验证数据的第一步是获取数据
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        # user = User.query.filter(User.telephone == telephone,
        #                          User.password == password).first()
        user = User.query.filter(User.telephone == telephone).first()
        # 如果用户注册成功，设置cookie保存，因为有登录限制
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 在31天内不用登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return '手机号码或者密码错误，请确认后再登录'

@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        # 获得前端的数据以便之后进行验证
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 查看手机号码是否被注册,查看数据库中是否有同样的手机号码数据
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return '该手机号码已被注册'
        else:
            # 验证两个密码是否相同
            if password1 != password2:
                return '两次密码不等，请核对后再填写'
            else:
                # 通过验证后的数据都是合法的，将其存入到数据库中
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                # 注册成功跳转到登录页面
                return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    # 删除user_id的三种方式
    # session.pop('user_id')
    # del session['user_id']
    session.clear()
    return redirect(url_for('login'))

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        # 获取发布问答表单的数据
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        # 获取符合条件的用户值
        # user_id = session.get('user_id')
        # user = User.query.filter(User.id == user_id).first()
        question.author = g.user
        # 保存数据到库中
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question=question_model)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    # user_id = session['user_id']
    # # 其他表里面的信息都是通过查询来获取的
    # user = User.query.filter(User.id == user_id).first()
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))

@app.route('/search/')
def search():
    # 获取前台用户输入的关键字的值,因为表单是get请求而非post请求，用request.args.get()方法
    q = request.args.get('q')
    condition = or_(Question.title.contains(q),Question.content.contains(q))
    questions = Question.query.filter(condition).order_by(Question.create_time.desc())
    # 返回只有符合条件的数据的首页
    return render_template('index.html', questions=questions)

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    # 如果用户已登录
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 把用户绑定到全局属性g对象中(记得要在开头导入g)
            g.user = user

# 定义上下文处理器在所有其他页面使用户一直保持登录状态
@app.context_processor
def my_context_processor():
    # # 通过cookie查看用户是否登录,先获取值再进行验证
    # user_id =  session.get('user_id')
    # # 如果用户已登录,获取一条用户数据
    # if user_id:
    #     user = User.query.filter(User.id == user_id).first()
    #     if user:
    #         return {'user': user}
    if hasattr(g,'user'):
        return {'user':g.user}
    return {}

if __name__ == '__main__':
    app.run()
