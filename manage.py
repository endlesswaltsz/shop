# from flask_script import Manager
# add by Yancy - branch 1
# add by hyz - branch dev
# 8:56

from proj import create_app
app = create_app()


# manage = Manager(app)
if __name__ == '__main__':
    app.run(host=app.config['HOST'],port=app.config['PORT'])
