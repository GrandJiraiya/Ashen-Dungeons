from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
def admin_index():
    return {
        "section": "admin",
        "message": "Admin blueprint placeholder",
    }
    