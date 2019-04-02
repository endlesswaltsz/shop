import os

from flask import Markup, url_for
from flask_admin import BaseView, expose
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms.fields import SubmitField, StringField, DecimalField, FileField, SelectField, MultipleFileField
from wtforms.validators import DataRequired

from .models import Order, OrderDetail, Store

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, 'static')


class OrderView(ModelView):
    can_create = True

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(OrderView, self).__init__(Order, session, **kwargs)

    form_overrides = dict(status=SelectField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        status=dict(
            choices=[('0', '待付款'), ('1', '交易关闭'), ('2', '已支付'), ('3', '交易成功')]
        ))


class OrderDetailView(ModelView):
    can_create = True

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(OrderDetailView, self).__init__(OrderDetail, session, **kwargs)

    form_overrides = dict(object_type=SelectField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        object_type=dict(
            choices=[('CpuProduct', 'cpu'), ('GpuProduct', '显卡')]
        ))


class AvatarView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup(
            '<img src="%s">' % url_for('static',
                                       filename=form.thumbgen_filename(model.path))
        )

    column_formatters = {
        'path': _list_thumbnail
    }

    form_extra_fields = {
        'avatar': form.ImageUploadField(
            'avatar', base_path=file_path, relative_path='files/avatar/', thumbnail_size=(100, 100, True))
    }


class StoreView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup(
            '<img src="%s">' % url_for('static',
                                       filename=form.thumbgen_filename(model.path))
        )

    column_list = ('name', 'nav_bar_image')
    column_formatters = {
        'path': _list_thumbnail
    }

    form_extra_fields = {
        'nav_bar_image': form.ImageUploadField(
            'nav_bar_image', base_path=file_path, relative_path='files/store_image/', thumbnail_size=(300, 100, True))
    }


class CpuAddView(BaseView):

    @expose('/',methods=['GET','POST'])
    def index(self):
        class CpuForm(FlaskForm):
            stores = Store.query.all()
            name = StringField(
                label=u"商品名",
                validators=[
                    DataRequired()
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            slogan = StringField(
                label=u"商品描述",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            sale_price = DecimalField(
                label=u'售卖价格',
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            commodity_figure_path = FileField(
                label=u'商品图片',
                validators=[
                    FileRequired(),
                ],
                render_kw={
                    "class": "form-control",
                    'accept': 'image/jpeg,image/png,image/jpg'
                }
            )
            store = SelectField(
                label=u'旗舰店',
                validators=[
                    DataRequired(),
                ],
                choices=[(str(store.id), store.name) for store in stores],
                render_kw={
                    "class": "form-control",
                }
            )
            brand = SelectField(
                label=u'品牌',
                validators=[
                    DataRequired(),
                ],
                choices=[('英特尔', '英特尔'), ('AMD', 'AMD')],
                render_kw={
                    "class": "form-control",
                }
            )
            interface = StringField(
                label=u"接口类型",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            match_mainboard = StringField(
                label=u"搭配主板",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            series = StringField(
                label=u"系列",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            model = StringField(
                label=u"型号",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            core_count = StringField(
                label=u"核心数量",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            GHz = StringField(
                label=u"主频",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            manufacturing_technique = StringField(
                label=u"制造工艺",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            power = StringField(
                label=u"功率",
                validators=[
                    DataRequired(),
                ],
                render_kw={
                    "class": "form-control",
                }
            )
            # multi_img = MultipleFileField(
            #     label='多图片',
            #     render_kw={
            #         "class": "form-control",
            #     }
            # )
            submit = SubmitField(
                '提交',
                render_kw={
                    "class": "btn btn-success",
                }
            )
        from flask import request
        forms = CpuForm()
        if forms.validate_on_submit():
            print(forms.data)

        return self.render('index.html', form=forms)
