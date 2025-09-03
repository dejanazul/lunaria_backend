from utils.database import execute_query
from utils.helpers import generate_uuid


class CommunityMessage:
    def __init__(
        self,
        message_id=None,
        community_id=None,
        user_id=None,
        content=None,
        created_at=None,
    ):
        self.message_id = message_id
        self.community_id = community_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at

    def to_dict(self):
        """Convert community message object to dictionary"""
        return {
            "message_id": self.message_id,
            "community_id": self.community_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at,
        }

    @classmethod
    def create(cls, community_id, user_id, content):
        """Create a new message in the community"""
        message_data = {
            "message_id": generate_uuid(),
            "community_id": community_id,
            "user_id": user_id,
            "content": content,
        }

        result = execute_query("community_messages", "insert", json=message_data)
        return cls(**result) if result else None

    @classmethod
    def get_messages(cls, community_id, limit=50, before_id=None):
        """Get messages from a community with pagination"""
        if before_id:
            # Get messages before a specific message ID (for pagination)
            result = execute_query(
                "community_messages",
                "select",
                columns="*",
                eq=("community_id", community_id),
                lt=("created_at", before_id),
                order_by="created_at",
                desc=True,
                limit=limit,
            )
        else:
            # Get the most recent messages
            result = execute_query(
                "community_messages",
                "select",
                columns="*",
                eq=("community_id", community_id),
                order_by="created_at",
                desc=True,
                limit=limit,
            )

        return [cls(**m) for m in result] if result else []
