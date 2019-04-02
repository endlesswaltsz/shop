import io
import pickle
import random
import uuid

from PIL import Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet
from flask import render_template, request, session, redirect, flash, jsonify, url_for
from werkzeug.security import generate_password_hash

from manage import app
from myutils.pay import AliPay
from proj.models import Users, UserDetail, ProductID, Order, CpuProduct
from . import web
from .forms import RegistForm, LoginForm
from .. import rd, db


@web.route('/test/')
def test():
    return 'ok'


@web.route('/register/', methods=['get', 'post'])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = Users(
            username=data["username"],
            email=data["email"],
            phone=data["phone"],
            password=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        rd.hset('email_auth_userlist', data["username"], pickle.dumps(user))
        from proj.celery_task.emails import register_email_auth
        url = app.config['INDEX_URL'] + '/valid_email?code=' + (generate_regist(data["username"]))
        register_email_auth.delay(data["email"], url)
        return render_template('email_auth.html')
    return render_template('web/regist.html', form=form)


@web.route('/login/', methods=['get', 'post'])
def login():
    form = LoginForm()
    return_url = request.args.get('return_url')
    if return_url:
        session['return_url'] = return_url
    if form.validate_on_submit():
        data = form.data
        user = Users.query.filter_by(username=data["name"]).first()
        if data['code'].upper() != session['random_code'].upper():
            flash('验证码错误', 'err')
            return redirect(url_for('web.login'))
        if not user:
            flash('不存在的用户名', 'err')
            return redirect(url_for('web.login'))
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for('web.login'))
        session["user"] = user.username
        session["avatar"] = user.detail.avatar
        session["user_id"] = user.id
        from ..usr.views import get_cart_count
        session["cart_count"] = get_cart_count(user.id)
        return_url = session.get('return_url', None)
        if not return_url:
            return redirect(url_for('web.index'))
        return_url = session.pop('return_url')
        return redirect(return_url)
    return render_template('web/login.html', form=form)


@web.route('/logout/')
def logout():
    session.clear()
    return redirect(app.config['INDEX_URL'])


@web.route('/')
def index():
    # rd.sadd('email_auth_userlist','hzx hxy')
    # rd.srem('email_auth_userlist','hzx')删除
    # print(rd.sismember('email_auth_userlist','hzx'))判断是否存在
    # print(rd.sismember('email_auth_userlist', 'hyz'))

    return render_template('web/index.html', index=True)


@web.route('/valid_email/')
def valid_email():
    code = request.args.get('code')
    user = valid_regist(code)
    if user:
        obj = pickle.loads(user)
        rd.hdel('email_auth_userlist', obj.username)
        db.session.add(obj)
        db.session.commit()
        detail = UserDetail(user_id=obj.id, )
        db.session.add(detail)
        db.session.commit()
        return '激活成功！'
    return '发生未知错误'


@web.route('/random_image/')
def random_image():
    img = Image.new('RGB', (150, 30), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    image_font = ImageFont.truetype(font='proj/static/base/fonts/genesis.woff.ttf', size=25)
    image_draw = ImageDraw.Draw(img)
    text = random_code()
    session['random_code'] = text
    for i in range(4):
        image_draw.text((25 + i * 30, 0), text[i], font=image_font)
    f = io.BytesIO()
    img.save(f, 'png')
    return f.getvalue()


def valid_regist(encrypted_text):
    try:
        cipher_key = rd.get('cipher_key')
        if not cipher_key:
            cipher_key = Fernet.generate_key()
            rd.set('cipher_key', cipher_key, 60 * 60)
            return
        cipher = Fernet(cipher_key)
        encrypted_text = bytes(encrypted_text, encoding='utf-8')
        res = cipher.decrypt(encrypted_text)
        res = res.decode('utf-8')
        user = rd.hget('email_auth_userlist', res)
        if user:
            return user
        return
    except Exception:
        return


def generate_regist(username):
    try:
        cipher_key = rd.get('cipher_key')
        if not cipher_key:
            cipher_key = Fernet.generate_key()
            rd.set('cipher_key', cipher_key, 60 * 60)
        cipher = Fernet(cipher_key)
        encrypted_text = cipher.encrypt(bytes(username, encoding='utf-8'))
        encrypted_text = encrypted_text.decode('utf-8')
        return encrypted_text
    except Exception:
        return


def random_code():
    code = ''
    for i in range(4):
        code += random.choice(
            [chr(random.randint(97, 122)), chr(random.randint(65, 90)), str(random.randint(0, 9))])
    return code


@web.route('/_image-url')
def _get_image_url():
    img_id = request.args.get('img_id')
    img = UserDetail.query.get(img_id)
    if img is None:
        response = jsonify(status='not found')
        return response
    return jsonify(img_path=img.path, status='ok')


@web.route('/list', methods=['get'])
def get_list():
    page = request.args.get('page')
    if page:
        page = int(page)
    list = ProductID.query.filter_by(object_type='CpuProduct').paginate(page, 8, error_out=False)
    return render_template('web/list_result.html', list=list)


@web.route('/query_cpu', methods=['get'])
def query():
    page = request.args.get('page')
    query_condition = request.args.get('query')
    list = CpuProduct.query.filter(CpuProduct.name.like('%{}%'.format(query_condition))).paginate(page, 8,
                                                                                                  error_out=False)

    return render_template('web/query_list.html', list=list)


@web.route('/detail', methods=['get'])
def product_detail():
    num = request.args.get('item')
    if num:
        num = int(num)
        obj = ProductID.query.filter_by(id=num).first()
        return render_template('web/product_detail.html', obj=obj)
    return 'ok'


def ali():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = app.config['APP_ID']

    # 支付宝收到用户的支付,会向商户发两个请求,一个get请求,一个post请求
    # POST请求，用于最后的检测
    notify_url = app.config['NOTIFY_URL']
    # GET请求，用于页面的跳转展示
    return_url = app.config['RETURN_URL']
    # 用户私钥
    merchant_private_key_path = "keys/app_private_2048.txt"
    # 支付宝公钥
    alipay_public_key_path = "keys/alipay_public_2048.txt"
    # 生成一个AliPay的对象
    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


@web.route('/process_pay', methods=['post'])
def page2():
    # 支付宝如果收到用户的支付,支付宝会给我的地址发一个post请求,一个get请求
    alipay = ali()
    # 检测是否支付成功
    # 去请求体中获取所有返回的数据：状态/订单号
    post_data = request.form.to_dict()
    # print('支付宝给我的数据:::---------', post_data)
    # 做二次验证
    sign = post_data.pop('sign', None)
    # 通过调用alipay的verify方法去认证
    status = alipay.verify(post_data, sign)
    print('POST验证', status)
    if status:
        alipay_id = post_data.pop('out_trade_no', None)
        orders = Order.query.filter_by(alipay_id=int(alipay_id)).all()
        for order in orders:
            Order.query.filter_by(id=order.id).update({'status': 2})
            db.session.commit()
    return 'POST返回'


@web.route('/callback')
def call_back():
    alipay = ali()
    params = request.args
    print(type(params), params, type(params.to_dict()))
    params = params.to_dict()
    sign = params.pop('sign', None)
    status = alipay.verify(params, sign)
    print('GET验证', status)
    return redirect(url_for('usr.before_send'))
