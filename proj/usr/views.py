#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import json
import os

from flask import render_template, flash, redirect, url_for, session, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from . import usr
from .forms import PwdForm, AvatarForm
from .. import db, rd
from ..models import Users, UserDetail, ProductID, Order, OrderDetail, AlipayOrder
from ..web.views import ali


@usr.before_request
def auth():
    user = session.get('user')
    # print(url_for('web.login'))
    if not user:
        if request.method == 'POST':
            return jsonify({'status': 'success', 'url': url_for('web.login') + '?return_url=%s' % request.referrer})
        flash('请先登录', category='err')
        return redirect(url_for('web.login') + '?return_url=%s' % request.path)


@usr.route('/')
def index():
    return render_template('usr/user_base.html')


@usr.route('/info/')
def userinfo():
    return render_template('usr/userinfo.html')


@usr.route('/info/modify_password/', methods=["GET", "POST"])
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = Users.query.filter_by(username=session["user"])
        if not user.first().check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('usr.pwd'))
        new_pwd = generate_password_hash(data["new_pwd"])
        user.update({'password': new_pwd})
        db.session.commit()
        return redirect(url_for('web.logout'))
    return render_template("usr/modify_password.html", form=form)


@usr.route('/info/avatar/', methods=["GET", "POST"])
def avatar():
    from ..web.views import app
    form = AvatarForm()
    if form.validate_on_submit():
        avatar_name = secure_filename(form.avatar.data.filename)
        detail = UserDetail.query.filter_by(user_id=session['user_id'])
        if detail.first().avatar:
            os.remove(app.config['STATIC_DIR'] + os.path.sep + detail.first().avatar)
        detail.update({'avatar': 'files/avatar/' + avatar_name})
        db.session.commit()
        form.avatar.data.save(app.config['STATIC_DIR'] + '/files/avatar/' + avatar_name)
        session['avatar'] = 'files/avatar/' + avatar_name
        flash('上传头像成功！', category='success')
        return redirect(url_for('usr.avatar'))
    return render_template("usr/edit_avatar.html", form=form)


@usr.route('/add_to_cart/', methods=['post'])
def add_to_cart():
    count = request.form.get('count')
    pid = request.form.get('pid')
    user_id = session.get('user_id')
    user_cart_list = rd.hget('user_cart', user_id)
    if not user_cart_list:
        rd.hset('user_cart', user_id, json.dumps([(pid, count), ]))
    else:
        user_cart_list = json.loads(user_cart_list)
        for i in user_cart_list:
            if i[0] == pid:
                i[1] = str(int(i[1]) + int(count))
                break
        else:
            user_cart_list.append((pid, count))
        rd.hset('user_cart', user_id, json.dumps(user_cart_list))
    session["cart_count"] = get_cart_count(user_id)
    return jsonify({'status': 'success', 'url': url_for('usr.cart')})


@usr.route('/cart/', methods=['get', 'post'])
def cart():
    user_cart_list = rd.hget('user_cart', session['user_id'])
    list = None
    if not user_cart_list:
        pass
    else:
        user_cart_list = json.loads(user_cart_list)
        list = [(ProductID.query.filter_by(id=int(li[0])).first(), int(li[1])) for li in user_cart_list]
    return render_template('usr/cart.html', list=list)


@usr.route('/cart_change/', methods=['post'])
def cart_change():
    func = request.form.get('func')
    pid = request.form.get('pid')
    user_id = session.get('user_id')
    user_cart_list = json.loads(rd.hget('user_cart', user_id))
    count = ''
    for i in user_cart_list:
        if i[0] == pid:
            if func == '+':
                count = i[1] = str(int(i[1]) + 1)
                print(count)
            else:
                count = i[1] = str(int(i[1]) - 1)
            break
    rd.hset('user_cart', user_id, json.dumps(user_cart_list))
    session["cart_count"] = get_cart_count(user_id)
    return jsonify({'status': 'success', 'count': count})


@usr.route('/delete_item')
def cart_delete_item():
    item = request.args.get('item')
    user_id = int(session.get('user_id'))
    user_cart_list = json.loads(rd.hget('user_cart', user_id))
    for order in user_cart_list:
        if order[0] == item:
            print(item, order[0])
            user_cart_list.remove(order)
            break
    rd.hset('user_cart', user_id, json.dumps(user_cart_list))
    session["cart_count"] = get_cart_count(user_id)
    return redirect(url_for('usr.cart'))


@usr.route('/create_order/', methods=['post'])
def create_order():
    user_id = session.get('user_id')
    order_list = json.loads(request.form.get('list'))
    # user_cart_list = json.loads(rd.hget('user_cart', user_id))
    sum = 0
    orderlist = []
    user_cart_list = json.loads(rd.hget('user_cart', user_id))
    alipay_order = AlipayOrder()
    db.session.add(alipay_order)
    db.session.commit()
    for i in order_list:
        obj_id = int(i[0])
        for j in user_cart_list:
            if int(j[0]) == obj_id:
                user_cart_list.remove(j)
                continue
        count = int(i[1])
        obj = ProductID.query.filter_by(id=obj_id).first()
        price = float(obj.object.sale_price) * count
        sum += price
        order = Order(status='0', user_id=user_id, count=count, alipay_id=alipay_order.id)
        db.session.add(order)
        db.session.commit()
        detail = OrderDetail(order_id=order.id, object_type=obj.object_type, object_id=obj.object_id)
        db.session.add(detail)
        db.session.commit()
        orderlist.append(order.id)
    AlipayOrder.query.filter_by(id=alipay_order.id).update({'sum': sum})
    db.session.commit()
    send_order_expired_task(orderlist)  # 发送订单自动删除请求
    rd.hset('user_cart', user_id, json.dumps(user_cart_list))  # 从购物车中移除商品
    return jsonify({'status': 'success', 'url': url_for('usr.user_order_unpay')})


def send_order_expired_task(orderlist):
    '''
    30分钟如果未付款，自动关闭订单
    '''
    ctime = datetime.datetime.now()
    utc_ctime = datetime.datetime.utcfromtimestamp(ctime.timestamp())
    time_delay = datetime.timedelta(minutes=1)
    task_time = utc_ctime + time_delay  # 设定延迟执行时间
    from ..celery_task.order_expired import order_auto_expired
    order_auto_expired.apply_async(args=[orderlist], eta=task_time)


@usr.route('/user_order')
def user_order():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.ordered_time.desc())
    return render_template('usr/userorder_all.html', orders=orders)


@usr.route('/user_order_unpay')
def user_order_unpay():
    '''
    优惠券及秒杀打折业务逻辑暂未写，未返回前端当前用户有哪些可享用的折扣
    '''
    lists = []

    orders = Order.query.filter_by(user_id=session['user_id'], status='0').order_by(Order.ordered_time.desc()).all()
    if not orders:
        alipay_id = ''
    else:
        alipay_id = orders[0].alipay_id
    for order in orders:
        lists.append((ProductID.query.filter_by(id=order.detail.object.PID).first(), order.count, order.id))
    return render_template('usr/unpay.html', lists=lists, alipay_id=alipay_id)


@usr.route('/before_send', methods=['get'])
def before_send():
    '''

    order_dict={'alipay_id1':{'orders':[order1,order2,],'sum':sum},'alipay_id2':{...}}
    '''
    user_id = session.get('user_id')
    orders = Order.query.filter_by(user_id=user_id, status='2').order_by(Order.ordered_time.desc()).all()
    order_dict = {}
    for order in orders:
        if order.alipay_id not in order_dict:
            order_dict[order.alipay_id] = {}
            order_dict[order.alipay_id]['orders'] = [order, ]
            order_dict[order.alipay_id]['sum'] = order.alipay_order.sum
        else:
            order_dict[order.alipay_id]['orders'].append(order)
    return render_template('usr/has_payed.html', order_dict=order_dict)


@usr.route('/go_pay', methods=['post'])
def redirect_alipay():
    alipay_id = request.form.get('alipay_id')
    money = float(AlipayOrder.query.filter_by(id=int(alipay_id)).first().sum)
    # 生成一个对象
    alipay = ali()
    # 生成支付的url
    # 对象调用direct_pay
    # 该方法生成一个加密串
    query_params = alipay.direct_pay(
        subject="hy商城购物订单",  # 商品简单描述
        out_trade_no=str(alipay_id),  # 商户订单号
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
    return jsonify({'status': 'success', 'url': pay_url})


def get_cart_count(user_id):
    user_cart_list = rd.hget('user_cart', user_id)
    if not user_cart_list:
        return 0
    user_cart_list=json.loads(user_cart_list)
    sum = 0
    for items in user_cart_list:
        sum += int(items[1])
    return sum
