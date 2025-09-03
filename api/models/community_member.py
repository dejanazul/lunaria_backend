from api.utils.database import execute_query
from api.utils.helpers import generate_uuid


class CommunityMember:
    def __init__(
        self, id=None, community_id=None, user_id=None, role="member", joined_at=None
    ):
        self.id = id
        self.community_id = community_id
        self.user_id = user_id
        self.role = role
        self.joined_at = joined_at

    def to_dict(self):
        """Convert community member object to dictionary"""
        return {
            "id": self.id,
            "community_id": self.community_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_at": self.joined_at,
        }

    @classmethod
    def create(cls, community_id, user_id, role="member"):
        """Add user to community"""
        member_data = {
            "id": generate_uuid(),
            "community_id": community_id,
            "user_id": user_id,
            "role": role,
        }

        result = execute_query("community_members", "insert", json=member_data)
        return cls(**result) if result else None

    @classmethod
    def get_by_user_and_community(cls, user_id, community_id):
        """Get membership by user and community"""
        result = execute_query(
            "community_members",
            "select",
            columns="*",
            eq=[("user_id", user_id), ("community_id", community_id)],
        )
        return cls(**result[0]) if result else None

    @classmethod
    def get_members(cls, community_id, limit=100):
        """Get all members of a community"""
        result = execute_query(
            "community_members",
            "select",
            columns="*",
            eq=("community_id", community_id),
            limit=limit,
        )
        return [cls(**m) for m in result] if result else []
