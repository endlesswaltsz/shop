from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, PasswordField,StringField,SelectField,DecimalField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed,FileRequired,FileField



class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！"),
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }
    )
    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success",
        }
    )


class AvatarForm(FlaskForm):
    avatar = FileField(
        label="头像",
        validators=[
            FileRequired(),
        ],
        render_kw={
            "class": "form-control",
            'accept':'image/jpeg,image/png,image/jpg'
        }
    )
    submit = SubmitField(
        render_kw={
            'value':'上传',
            "class": "btn btn-success",
        }
    )
