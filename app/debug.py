from flask import Blueprint, current_app

bp = Blueprint("debug", __name__, url_prefix="/debug")

@bp.get("/config")
def config():
    return {
        "application": "VulnLab",
        "database_path": current_app.config["DATABASE"],
        "debug_mode": current_app.debug,
        "secret_key": current_app.config["SECRET_KEY"],
        "testing_mode": current_app.testing,
    }