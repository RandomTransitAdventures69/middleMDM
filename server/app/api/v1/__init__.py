"""API v1 blueprint."""
from flask import Blueprint

api_bp = Blueprint("api_v1", __name__)

# Import routes to register them
from . import devices, enrollment, heartbeat, inventory, network, policies
