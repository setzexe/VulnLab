from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
