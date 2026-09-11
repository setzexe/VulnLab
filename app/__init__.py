import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "vulnlab.sqlite"),
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from app import db # PREVENTS INFINITE IMPORT LOOP

    db.init_app(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
