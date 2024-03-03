# controllers/base_controller.py
from flask import Blueprint, request, Response
from services.code_reviewer_service import CodeReviewerService

base_bp = Blueprint('home', __name__)

class BaseController:
    @staticmethod
    @base_bp.route('/', methods=['POST'])
    def ping_pr():
        payload = request.json
        CodeReviewerService.review_code(payload)
        return "Code review initiated"
