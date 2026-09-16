import os
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("VULNLAB_SECRET_KEY", "dev-key"),
        DATABASE=os.path.join(app.instance_path, "vulnlab.sqlite"),
        RATELIMIT_STORAGE_URI="memory://"
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db # PREVENTS INFINITE IMPORT LOOP
    from .extension import limiter
    limiter.init_app(app)
    db.init_app(app)
    
    from . import auth, admin, notes
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(notes.bp)

    @app.get("/")
    def index():
        return render_template("index.html")
    
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
