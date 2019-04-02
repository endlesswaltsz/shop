from proj.web.views import app, db  # 不能直接从Manage.py中导入app，db

if __name__ == '__main__':  # 建表
    with app.app_context():
        db.create_all()
