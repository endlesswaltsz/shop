import datetime

from sqlalchemy_utils import ChoiceType, generic_relationship
from whoosh.analysis import SimpleAnalyzer

# import flask_whooshalchemy
from . import db






class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # id
    username = db.Column(db.String(20), unique=True)  # 登录名&昵称
    password = db.Column(db.String(128))  # 密码
    email = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(11), unique=True)
    uuid = db.Column(db.String(255), unique=True)  # 用户唯一标识
    detail = db.relationship('UserDetail', backref='user', uselist=False)  # 用户详情一对一

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, pwd)

    def __repr__(self):
        return self.username


class UserDetail(db.Model):
    __tablename__ = 'userdetail'
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(256))  # 头像
    plus_vip = db.Column(db.Boolean, default=False)  # plus会员
    vip_expired = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键关联


class AlipayOrder(db.Model):
    __tablename__ = 'aplipayorder'
    id = db.Column(db.Integer, primary_key=True)
    sum = db.Column(db.DECIMAL(8, 2))


class Order(db.Model):
    STATUS = [('0', '待付款'), ('1', '交易关闭'), ('2', '已支付'), ('3', '交易成功')]
    __tablename__ = 'userorder'  ###order是关键字！
    id = db.Column(db.Integer, primary_key=True)  # id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键关联到用户表
    user = db.relationship('Users', backref='orders')  # 辅助查询
    pay_money = db.Column(db.DECIMAL(8, 2))  # 付款金额
    count = db.Column(db.Integer)
    ordered_time = db.Column(db.DateTime, default=datetime.datetime.now)  # 订单提交时间
    status = db.Column(ChoiceType(STATUS))  # 订单状态
    detail = db.relationship('OrderDetail', uselist=False, backref='order')
    alipay_id = db.Column(db.Integer, db.ForeignKey('aplipayorder.id'))
    alipay_order = db.relationship('AlipayOrder', backref='orders')


class OrderDetail(db.Model):
    __tablename__ = 'orderdetail'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('userorder.id'))  # 外键关联到订单表
    pay_time = db.Column(db.DateTime)  # 支付时间
    # pay_money=db.Column(db.DECIMAL(8,2))
    object_type = db.Column(db.Unicode(255))
    object_id = db.Column(db.Integer)
    object = generic_relationship(object_type, object_id)  # 关联到任意表的一条数据（商品）


class Store(db.Model):
    __tablename__ = 'store'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    nav_bar_image = db.Column(db.String(256), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    admin_username = db.Column(db.String(32), nullable=False)
    admin_password = db.Column(db.String(32), nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='comment')


class ProductID(db.Model):
    __tablename__ = 'PID'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))
    object_type = db.Column(db.Unicode(255))
    object_id = db.Column(db.Integer)
    object = generic_relationship(object_type, object_id)  # 关联到任意表的一条数据（商品）


class DetailImage(db.Model):
    __tablename__ = 'detailimage'
    id = db.Column(db.Integer, primary_key=True)
    PID_id = db.Column(db.Integer, db.ForeignKey('PID.id'))
    PID = db.relationship('ProductID', backref='detail_image')  # 辅助查询
    path = db.Column(db.String(256))  # 图片储存路径
    order = db.Column(db.Integer)  # 详情图片顺序

    def __str__(self):
        return self.path

class CpuProduct(db.Model):
    __tablename__ = 'cpuproduct'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))  # 商品名
    PID = db.Column(db.Integer, db.ForeignKey('PID.id'))  # 商品编号
    slogan = db.Column(db.String(128))  # 商品简略描述
    sale_price = db.Column(db.DECIMAL(8, 2))  # 商品售价
    commodity_figure_path = db.Column(db.String(256))  # 商品图路径
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    store = db.relationship('Store', backref='cpu')  # 辅助查询
    detail = db.relationship('CpuDetail', uselist=False, backref='cpu')


class CpuDetail(db.Model):
    __tablename__ = 'cpudetail'
    id = db.Column(db.Integer, primary_key=True)
    cpu_id = db.Column(db.Integer, db.ForeignKey('cpuproduct.id'))
    brand = db.Column(db.String(32))  # 品牌
    interface = db.Column(db.String(32))  # 接口类型
    match_mainboard = db.Column(db.String(32))  # 搭配主板
    series = db.Column(db.String(32))  # 系列
    model = db.Column(db.String(32))  # 型号
    core_count = db.Column(db.String(32))  # 核心数量
    GHz = db.Column(db.String(32))  # 主频
    manufacturing_technique = db.Column(db.String(32))  # 制造工艺
    power = db.Column(db.String(32))  # 功率


class GpuProduct(db.Model):
    __tablename__ = 'gpuproduct'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))  # 商品名
    PID = db.Column(db.Integer, db.ForeignKey('PID.id'))  # 商品编号
    slogan = db.Column(db.String(128))  # 商品简略描述
    sale_price = db.Column(db.DECIMAL(8, 3))  # 商品售价
    commodity_figure_path = db.Column(db.String(256))  # 商品图路径
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    store = db.relationship('Store', backref='gpu')  # 辅助查询
    detail = db.relationship('GpuDetail', uselist=False, backref='gpu')


class GpuDetail(db.Model):
    __tablename__ = 'gpudetail'
    id = db.Column(db.Integer, primary_key=True)
    cpu_id = db.Column(db.Integer, db.ForeignKey('gpuproduct.id'))
    brand = db.Column(db.String(32))  # 品牌
    interface = db.Column(db.String(32))  # 接口类型
    chip_manufacturers = db.Column(db.String(32))  # 芯片厂家
    chip_model = db.Column(db.String(32))  # 核心芯片
    bit = db.Column(db.String(32))  # 显存位宽
    GRAM = db.Column(db.String(32))  # 显存容量
