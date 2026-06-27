from flask import Blueprint, jsonify
from services.bootstrap_service import bootstrap_system

bp = Blueprint("bootstrap", __name__)
 

@bp.get("/mcp/bootstrap-system")
def bootstrap():
    return jsonify(bootstrap_system())
