"""Policies API."""
from flask import request, jsonify
from . import api_bp
from .heartbeat import authenticate_device
from ...extensions import db
from ...models.policy import Policy, PolicyAssignment, PolicyResult


@api_bp.route("/policies", methods=["GET"])
def get_policies():
    """Get policies for a device."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    # Get policies assigned to device directly or via groups
    assignments = PolicyAssignment.query.all()
    policy_ids = set()
    
    for assignment in assignments:
        if assignment.device_id == device.id:
            policy_ids.add(assignment.policy_id)
        else:
            # Check if device is in assigned group
            for membership in device.memberships:
                if membership.group_id == assignment.group_id:
                    policy_ids.add(assignment.policy_id)
                    break
    
    policies = Policy.query.filter(Policy.id.in_(policy_ids), Policy.enabled == True).all()
    
    result = []
    for policy in policies:
        result.append({
            "id": policy.id,
            "name": policy.name,
            "policy_type": policy.policy_type,
            "category": policy.category,
            "configuration": policy.get_config(),
        })
    
    return jsonify({"policies": result}), 200


@api_bp.route("/policies/report", methods=["POST"])
def report_policy_result():
    """Report policy execution result."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    data = request.get_json(silent=True) or {}
    
    policy_id = data.get("policy_id")
    policy_type = data.get("policy_type")
    status = data.get("status")  # compliant, non_compliant, error
    detail = data.get("detail")
    
    if not all([policy_id, policy_type, status]):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = PolicyResult(
        device_id=device.id,
        policy_id=policy_id,
        policy_type=policy_type,
        status=status,
        detail=detail,
    )
    db.session.add(result)
    db.session.commit()
    
    return jsonify({"message": "Policy result reported"}), 200
