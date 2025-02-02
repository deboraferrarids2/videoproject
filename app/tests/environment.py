from app import create_app, db

def before_all(context):
    context.app = create_app(config_class="app.tests.test_config.TestConfig")

    with context.app.app_context():
        db.create_all()

def after_all(context):
    with context.app.app_context():
        db.session.remove()
        db.drop_all()
