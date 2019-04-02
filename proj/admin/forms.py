from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms.fields import SubmitField, PasswordField, StringField, DecimalField
from wtforms.validators import DataRequired


class AdminLoginForm(FlaskForm):
    username = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号！",
        }
    )
    password = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！",
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )


class CpuForm(FlaskForm):
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

