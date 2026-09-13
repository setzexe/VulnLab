from flask import ( abort, Blueprint, flash, g,
    redirect, render_template, request, url_for)

from .auth import login_required
from .db import get_db

bp = Blueprint("notes", __name__, url_prefix="/notes")

@bp.get("/")
@login_required
def index():
    notes = get_db().execute(
        """
        SELECT id, title, body, created_at
        FROM note
        WHERE owner_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (g.user["id"],),
    ).fetchall()

    return render_template("notes/index.html", notes=notes)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."

        if error is None:
            db = get_db()
            db.execute(
                """
                INSERT INTO note (owner_id, title, body)
                VALUES (?, ?, ?)
                """,
                (g.user["id"], title, body),
            )
            db.commit()

            return redirect(url_for("notes.index"))

        flash(error)

    return render_template("notes/create.html")

@bp.get("/search")
@login_required
def search():
    search_term = request.args.get("q", "")

    # SQL Injection Vulnerability:
    # User input is directly added into the SQL statement.
    # The attacker can start with ' to force the query to break, and add their own SQL code.
    query = f"""
        SELECT id, owner_id, title, body, created_at
        FROM note
        WHERE owner_id = {g.user["id"]} 
          AND title LIKE '%{search_term}%' 
        ORDER BY created_at DESC, id DESC
    """

    notes = get_db().execute(query).fetchall()

    return render_template(
        "notes/search.html",
        notes=notes,
        search_term=search_term,
    )

@bp.get("/<int:note_id>")
@login_required
def detail(note_id):
    note = get_db().execute(
        """
        SELECT id, owner_id, title, body, created_at
        FROM note
        WHERE id = ?
        """,
        (note_id,),
    ).fetchone()

    if note is None:
        abort(404)

    # The code below enforces that only the owner of a note can see their own note
    # By commenting it out, we showcase IDOR.
    # Authentication is required, but authorization is not.
    # Any loggin in user can see another user's note by changing the URL ID.
    # if note["owner_id"] != g.user["id"]: abort(403)

    return render_template("notes/detail.html", note=note)