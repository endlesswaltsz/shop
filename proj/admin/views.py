#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import session, redirect, render_template, flash, url_for, request
from werkzeug.utils import secure_filename

from . import admin
from .forms import AdminLoginForm, CpuForm
from .. import db
from ..models import Store, CpuProduct, CpuDetail, ProductID


@admin.before_request
def auth():
    admin = session.get('admin')
    if not admin:
        if request.path != url_for('admin.login'):
            return redirect(url_for('admin.login'))
@admin.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


@admin.route('/')
def index():
    return render_template('admin/admin_main.html')


@admin.route('/login/', methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        data = form.data
        store = Store.query.filter_by(admin_username=data["username"], admin_password=data['password']).first()
        if not store:
            flash('帐号或密码错误', 'err')
            return redirect(url_for('admin.login'))
        session["admin"] = store.name
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)


@admin.route('/add_cpu', methods=['get', 'post'])
def add_cpu():
    form = CpuForm()
    if form.validate_on_submit():
        data = form.data
        store = Store.query.filter_by(name=session['admin']).first()
        image_name = secure_filename(form.commodity_figure_path.data.filename)
        from ..web.views import app
        form.commodity_figure_path.data.save(app.config['STATIC_DIR'] + '/files/product_image/' + image_name)
        pid = ProductID(category='cpu')

        cpu = CpuProduct(name=data['name'], PID=pid.id, slogan=data['slogan'], sale_price=data['sale_price'],
                         commodity_figure_path='/files/product_image/' + image_name, store_id=store.id)
        pid.object = cpu
        detail = CpuDetail(cpu_id=cpu.id, brand=store.brand, interface=data['interface'],
                           match_mainboard=data['match_mainboard'],
                           series=data['series'], model=data['model'], core_count=data['core_count'], GHz=data['GHz'],
                           manufacturing_technique=data['manufacturing_technique'], power=data['power'])
        db.session.add_all([pid, cpu, detail])
        db.session.commit()
        ProductID.query.filter_by(id=pid.id).update({'object_id': cpu.id})
        CpuProduct.query.filter_by(id=cpu.id).update({'PID': pid.id})
        CpuDetail.query.filter_by(id=detail.id).update({'cpu_id': cpu.id})
        db.session.commit()

    return render_template('admin/add_cpu.html', form=form)
