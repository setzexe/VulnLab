from flask import Blueprint, render_template

from .auth import admin_required
from .db import get_db


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
@admin_required
def index():
    users = get_db().execute(
        """
        SELECT
            user.id,
            user.username,
            user.role,
            COUNT(note.id) AS note_count
        FROM user
        LEFT JOIN note ON note.owner_id = user.id
        GROUP BY user.id, user.username, user.role
        ORDER BY user.id
        """
    ).fetchall()

    return render_template("admin/index.html", users=users)