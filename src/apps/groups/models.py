from django.db.models import (
    Model,
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    PROTECT,
    CASCADE,
)
from apps.users.models import User


class Group(Model):
    creator = ForeignKey(User, on_delete=PROTECT, related_name="created_groups")
    name = CharField(max_length=120, null=False, blank=False)
    description = TextField()
    color = CharField(null=False, blank=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "groups"

    def __str__(self):
        return f"Group(id={self.id}, name={self.name}, creator={self.creator.email})"


class GroupMember(Model):
    group = ForeignKey(Group, on_delete=CASCADE, related_name="group_members")
    user = ForeignKey(User, on_delete=CASCADE, related_name="group_memberships")
    joined_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "group_members"

    def __str__(self):
        return f"GroupMember(id={self.id}, group_id={self.group.id}, group_name={self.group.name}, user_email={self.user.email})"
