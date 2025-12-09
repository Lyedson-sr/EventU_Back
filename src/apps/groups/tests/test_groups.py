from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.groups.models import Group, GroupMember


class GroupTests(APITestCase):
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

        self.group = Group.objects.create(
            creator=self.creator,
            name="Grupo X",
            description="desc",
            color="#fff",
        )
        GroupMember.objects.create(group=self.group, user=self.member)

        self.client.force_authenticate(self.creator)

    def test_stranger_cannot_retrieve_group(self):
        self.client.force_authenticate(self.stranger)
        url = reverse("group-detail", kwargs={"pk": self.group.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_stranger_cannot_list_groups(self):
        self.client.force_authenticate(self.stranger)
        url = reverse("group-list")
        res = self.client.get(url)
        self.assertEqual(len(res.data), 0)

    def test_member_cannot_update_group(self):
        self.client.force_authenticate(self.member)
        url = reverse("group-detail", kwargs={"pk": self.group.id})
        res = self.client.patch(url, {"name": "Hack"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_cannot_delete_group(self):
        self.client.force_authenticate(self.member)
        url = reverse("group-detail", kwargs={"pk": self.group.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_groups(self):
        self.client.force_authenticate(None)
        url = reverse("group-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_create_group(self):
        self.client.force_authenticate(None)
        url = reverse("group-list")
        res = self.client.post(url, {"name": "abc", "description": "x", "color": "red"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_nonexistent_group_returns_404(self):
        url = reverse("group-detail", kwargs={"pk": 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_list_nonexistent_group_returns_404(self):
        url = reverse("group-members-list", kwargs={"group_pk": 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
