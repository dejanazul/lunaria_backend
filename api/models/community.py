from api.utils.database import execute_query
from api.utils.helpers import generate_uuid


class Community:
    def __init__(
        self,
        community_id=None,
        name=None,
        description=None,
        created_by=None,
        is_public=True,
        created_at=None,
    ):
        self.community_id = community_id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.is_public = is_public
        self.created_at = created_at

    def to_dict(self):
        """Convert community object to dictionary"""
        return {
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "is_public": self.is_public,
            "created_at": self.created_at,
        }

    @classmethod
    def create(cls, name, created_by, description=None, is_public=True):
        """Create a new community"""
        community_data = {
            "community_id": generate_uuid(),
            "name": name,
            "description": description,
            "created_by": created_by,
            "is_public": is_public,
        }

        result = execute_query("communities", "insert", json=community_data)
        return cls(**result) if result else None

    @classmethod
    def get_by_id(cls, community_id):
        """Get community by ID"""
        result = execute_query(
            "communities", "select", columns="*", eq=("community_id", community_id)
        )
        return cls(**result) if result else None

    @classmethod
    def get_user_communities(cls, user_id):
        """Get all communities a user is a member of"""
        # This would typically join communities and community_members tables
        # For now we'll simulate with a mock implementation
        result = execute_query(
            "community_members",
            "select",
            columns="community_id",
            eq=("user_id", user_id),
        )

        communities = []
        for member in result:
            community = cls.get_by_id(member["community_id"])
            if community:
                communities.append(community)

        return communities

    @classmethod
    def discover_communities(cls, search_term="", limit=20):
        """Discover public communities"""
        # In a real implementation, you'd use a more sophisticated query
        # with search capabilities
        if search_term:
            result = execute_query(
                "communities",
                "select",
                columns="*",
                eq=("is_public", True),
                like=("name", f"%{search_term}%"),
                limit=limit,
            )
        else:
            result = execute_query(
                "communities",
                "select",
                columns="*",
                eq=("is_public", True),
                limit=limit,
            )

        return [cls(**c) for c in result] if result else []
