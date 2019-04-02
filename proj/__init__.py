from flask import Flask
from flask_admin.base import Admin
from flask_admin.contrib.sqla import ModelView
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
rd = FlaskRedis()

# class MyView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('index.html')



f_admin = Admin(name='后台管理',template_mode='bootstrap3',endpoint='admin_back')
from .models import Users, OrderDetail, Order,UserDetail,Store
from .admin_model import OrderView,AvatarView,OrderDetailView,StoreView,CpuAddView




f_admin.add_view(CpuAddView(name='cpu_add'))
f_admin.add_view(OrderView(db.session))
f_admin.add_view(OrderDetailView(db.session))
f_admin.add_view(AvatarView(UserDetail,db.session))
f_admin.add_view(StoreView(Store,db.session))


def create_app():
    app = Flask(__name__)
    app.config.from_object('proj.settings.LocalTestingConfig')
    from .usr import usr as usr_blueprint
    from .web import web as web_blueprint
    from .admin import admin as admin_blueprint
    app.register_blueprint(usr_blueprint, url_prefix='/user')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(web_blueprint)

    db.init_app(app)
    rd.init_app(app)
    f_admin.init_app(app)
    return app
