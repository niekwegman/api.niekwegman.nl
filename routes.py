from flask import Blueprint, request, jsonify
from models import db, User, Script, Log
from flask_jwt_extended import jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__)

@api_bp.route('/scripts', methods=['GET'])
@jwt_required()
def get_scripts():
    current_user = get_jwt_identity()
    if current_user['is_admin']:
        scripts = Script.query.all()
    else:
        return jsonify({"msg": "Admins only"}), 403
    return jsonify([{'id': s.id, 'name': s.name, 'log_location': s.log_location} for s in scripts]), 200

@api_bp.route('/scripts', methods=['POST'])
@jwt_required()
def create_script():
    if not get_jwt_identity()['is_admin']:
        return jsonify({"msg": "Admins only"}), 403
    data = request.get_json()
    new_script = Script(name=data['name'], log_location=data['log_location'])
    db.session.add(new_script)
    db.session.commit()
    return jsonify({"msg": "Script created"}), 201

@api_bp.route('/scripts/<int:script_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modify_script(script_id):
    if not get_jwt_identity()['is_admin']:
        return jsonify({"msg": "Admins only"}), 403
    script = Script.query.get_or_404(script_id)
    if request.method == 'PUT':
        data = request.get_json()
        script.name = data.get('name', script.name)
        script.log_location = data.get('log_location', script.log_location)
        db.session.commit()
        return jsonify({"msg": "Script updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(script)
        db.session.commit()
        return jsonify({"msg": "Script deleted"}), 200

@api_bp.route('/webhook/<int:script_id>', methods=['POST'])
@jwt_required()
def log_script_event(script_id):
    data = request.get_json()
    log = Log(script_id=script_id, message=data['message'])
    db.session.add(log)
    db.session.commit()
    return jsonify({"msg": "Log entry created"}), 201
