from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.groups.models import Group, GroupMember


class GroupMemberTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            email="creator@test.com", password="1234", name="Creator"
        )
        self.member = User.objects.create_user(
            email="member@test.com", password="1234", name="Member"
        )
        self.stranger = User.objects.create_user(
            email="stranger@test.com", password="1234", name="Stranger"
        )
        self.other = User.objects.create_user(
            email="other@test.com", password="1234", name="Other"
        )

        self.group = Group.objects.create(
            creator=self.creator,
            name="Grupo Y",
            description="desc",
            color="#00f",
        )
        self.member_obj = GroupMember.objects.create(group=self.group, user=self.member)

        self.client.force_authenticate(self.creator)

    def test_stranger_cannot_list_members(self):
        self.client.force_authenticate(self.stranger)
        url = reverse("group-members-list", kwargs={"group_pk": self.group.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_member_with_empty_email_fails(self):
        url = reverse("group-members-list", kwargs={"group_pk": self.group.id})
        res = self.client.post(url, {"email": ""})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_member_user_not_found(self):
        url = reverse("group-members-list", kwargs={"group_pk": self.group.id})
        res = self.client.post(url, {"email": "nao-existe@test.com"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_member_duplicate_fails(self):
        url = reverse("group-members-list", kwargs={"group_pk": self.group.id})
        res = self.client.post(url, {"email": self.member.email})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_cannot_add_member(self):
        self.client.force_authenticate(self.member)
        url = reverse("group-members-list", kwargs={"group_pk": self.group.id})
        res = self.client.post(url, {"email": self.other.email})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_cannot_delete_member(self):
        self.client.force_authenticate(self.member)
        url = reverse(
            "group-member-detail",
            kwargs={"group_pk": self.group.id, "pk": self.member_obj.id},
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_cannot_delete_nonexistent_member(self):
        url = reverse(
            "group-member-detail", kwargs={"group_pk": self.group.id, "pk": 99999}
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_members_dont_see_unrelated_group_members(self):
        other_group = Group.objects.create(
            creator=self.stranger,
            name="Outro Grupo",
            description="???",
            color="#777",
        )
        GroupMember.objects.create(group=other_group, user=self.stranger)

        self.client.force_authenticate(self.member)
        url = reverse("group-members-list", kwargs={"group_pk": other_group.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_cannot_retrieve_other_group_member(self):
        other_group = Group.objects.create(
            creator=self.stranger,
            name="GG",
            description="desc",
            color="#000",
        )
        other_member = GroupMember.objects.create(group=other_group, user=self.other)

        self.client.force_authenticate(self.member)
        url = reverse(
            "group-member-detail",
            kwargs={"group_pk": other_group.id, "pk": other_member.id},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
