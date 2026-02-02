# from enum import Enum
# from typing import Optional, List
# from beanie import Document, Link, Indexed
# from pydantic import Field
# from datetime import datetime
# from app.models.article import ArticleModel
# from app.models.users import UserModel
# from app.models.firm import FirmModel


# class ModerationStatus(str, Enum):
#     PENDING = "PENDING"
#     APPROVED = "APPROVED"
#     REJECTED = "REJECTED"
#     ESCALATED = "ESCALATED"


# class ModerationTrigger(str, Enum):
#     PRE_PUBLISH = "pre_publish"
#     POST_PUBLISH = "post_publish"
#     USER_REPORT = "user_report"
#     SYSTEM_FLAG = "system_flag"


# class ModerationTaskModel(Document):
#     # 🔗 What is being moderated
#     article_id: Link[ArticleModel]
#     firm_id: Link[FirmModel]
#     publisher_id: Link[UserModel]

#     # 📌 Why moderation happened
#     trigger: ModerationTrigger
#     trust_score_snapshot: int

#     # 📋 Status
#     status: ModerationStatus = ModerationStatus.PENDING

#     # 🧑‍⚖️ Admin actions
#     assigned_admin_id: Optional[Link[UserModel]] = None
#     decision_reason: Optional[str] = None
#     admin_notes: Optional[str] = None

#     # ⚠️ Violations
#     violations_detected: List[str] = Field(default_factory=list)

#     # 🕒 Audit fields
#     created_at: datetime = Field(default_factory=datetime.now)
#     reviewed_at: Optional[datetime] = None

#     class Settings:
#         name = "moderation_tasks"
#         indexes = [
#             "status",
#             "trigger",
#             "created_at"
#         ]
