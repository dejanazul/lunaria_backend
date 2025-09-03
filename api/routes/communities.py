from flask import Blueprint, request, g
from api.models.community import Community
from api.models.community_member import CommunityMember
from api.models.community_message import CommunityMessage
from api.utils.helpers import format_response, format_error
from api.utils.decorators import auth_required, validate_json
from api.utils.validators import CommunitySchema

communities_bp = Blueprint('communities', __name__)

@communities_bp.route('/', methods=['GET'])
@auth_required
def get_communities():
    """Get all communities user is member of"""
    try:
        communities = Community.get_user_communities(g.current_user_id)
        
        return format_response(
            [community.to_dict() for community in communities],
            "Communities retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to retrieve communities", 500)

@communities_bp.route('/discover', methods=['GET'])
@auth_required
def discover_communities():
    """Discover public communities"""
    try:
        search = request.args.get('search', '')
        limit = request.args.get('limit', 20, type=int)
        
        communities = Community.discover_communities(search, limit)
        
        return format_response(
            [community.to_dict() for community in communities],
            "Communities discovered successfully"
        )
    
    except Exception as e:
        return format_error("Failed to discover communities", 500)

@communities_bp.route('/', methods=['POST'])
@auth_required
@validate_json(CommunitySchema)
def create_community():
    """Create new community"""
    try:
        data = g.validated_data
        community = Community.create(
            name=data['name'],
            description=data.get('description'),
            created_by=g.current_user_id
        )
        
        # Auto-join creator as member
        CommunityMember.add_member(community.community_id, g.current_user_id)
        
        return format_response(
            community.to_dict(),
            "Community created successfully",
            201
        )
    
    except Exception as e:
        return format_error("Failed to create community", 500)

@communities_bp.route('/<community_id>/join', methods=['POST'])
@auth_required
def join_community(community_id):
    """Join a community"""
    try:
        community = Community.get_by_id(community_id)
        if not community:
            return format_error("Community not found", 404)
        
        # Check if already a member
        is_member = CommunityMember.is_member(community_id, g.current_user_id)
        if is_member:
            return format_error("Already a member of this community", 400)
        
        CommunityMember.add_member(community_id, g.current_user_id)
        
        return format_response(None, "Successfully joined community")
    
    except Exception as e:
        return format_error("Failed to join community", 500)

@communities_bp.route('/<community_id>/leave', methods=['POST'])
@auth_required
def leave_community(community_id):
    """Leave a community"""
    try:
        is_member = CommunityMember.is_member(community_id, g.current_user_id)
        if not is_member:
            return format_error("Not a member of this community", 400)
        
        CommunityMember.remove_member(community_id, g.current_user_id)
        
        return format_response(None, "Successfully left community")
    
    except Exception as e:
        return format_error("Failed to leave community", 500)

@communities_bp.route('/<community_id>/messages', methods=['GET'])
@auth_required
def get_messages(community_id):
    """Get community messages"""
    try:
        # Check if user is member
        is_member = CommunityMember.is_member(community_id, g.current_user_id)
        if not is_member:
            return format_error("Access denied. Join community first.", 403)
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        messages = CommunityMessage.get_community_messages(
            community_id, page, limit
        )
        
        return format_response(
            [msg.to_dict() for msg in messages],
            "Messages retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to retrieve messages", 500)

@communities_bp.route('/<community_id>/messages', methods=['POST'])
@auth_required
def post_message(community_id):
    """Post message to community"""
    try:
        # Check if user is member
        is_member = CommunityMember.is_member(community_id, g.current_user_id)
        if not is_member:
            return format_error("Access denied. Join community first.", 403)
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return format_error("Message cannot be empty", 400)
        
        message = CommunityMessage.create(
            community_id=community_id,
            user_id=g.current_user_id,
            message=message_text
        )
        
        return format_response(
            message.to_dict(),
            "Message posted successfully",
            201
        )
    
    except Exception as e:
        return format_error("Failed to post message", 500)
