# from flask_script import Manager

from proj import create_app
app=create_app()


# manage = Manager(app)
if __name__ == '__main__':
    app.run(host=app.config['HOST'],port=app.config['PORT'])
