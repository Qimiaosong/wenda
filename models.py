from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self,*args,**kwargs):
        telephone = kwargs.get('telephone')
        username = kwargs.get('username')
        password = kwargs.get('password')

        self.telephone = telephone
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self,raw_password):
        result = check_password_hash(self.password,raw_password)
        return result

# 写一张表用来保存发布问答表单的信息
# 一个用户可以对应多个问答，一对多的关系表，在一方定义db.relationship()，多方定义外键
class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text,nullable=False)
    # now()获取的是服务器第一次运行的时间
    create_time = db.Column(db.DateTime,default=datetime.now)
    # 指明作者id作为外键，是作者表的主键
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    author = db.relationship('User',backref=db.backref('questions'))

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)
    # 这个评论属于哪一个话题之下
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    # 这个评论的发布人是,因为所有人都可以任意评论
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 拿到一个话题下的所有评论
    question = db.relationship('Question', backref=db.backref('answers',
                                                order_by=id.desc()))
    # 拿到一个用户发表的所有评论
    author = db.relationship('User', backref=db.backref('answers'))


