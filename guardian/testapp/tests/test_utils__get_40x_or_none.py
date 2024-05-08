from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, Group
from django.conf import settings

# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseNotFound
from guardian.shortcuts import assign_perm
from guardian.utils import get_40x_or_None
from ..models import CustomUser as User


class Test(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.object = Group.objects.create(name="Test Group")

    def test_no_permissions_anonymous(self):
        request = self.factory.get("/group/{self.object.pk}/", obj=self.object)
        request.user = AnonymousUser()

        response = get_40x_or_None(request, ["auth.view_group"])
        self.assertEqual(response.status_code, 302)
        self.assertTrue(settings.LOGIN_URL in response.url)

    def test_no_permissions_authenticated_return_403(self):
        request = self.factory.get("/group/{self.object.pk}/", obj=self.object)
        request.user = self.user

        response = get_40x_or_None(request, ["auth.view_group"], return_403=True)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_no_permissions_authenticated_return_404(self):
        request = self.factory.get("/some-url")
        request.user = self.user
        response = get_40x_or_None(request, ["auth.view_group"], return_404=True)
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_with_any_permissions(self):
        request = self.factory.get("/group/{self.object.pk}/", obj=self.object)
        request.user = self.user
        assign_perm("auth.view_group", self.user, obj=self.object)

        response = get_40x_or_None(
            request,
            ["auth.view_group", "auth.change_group"],
            any_perm=True,
            obj=self.object,
        )
        self.assertIsNone(response)  # Expecting None as user has permission

    def test_global_perms(self):
        request = self.factory.get("/group/{self.object.pk}/", obj=self.object)
        request.user = self.user
        assign_perm("auth.view_group", self.user)

        response = get_40x_or_None(
            request,
            ["auth.view_group"],
            accept_global_perms=True,
            obj=self.object,
        )
        self.assertIsNone(response)  # User has global perms, expecting None

    def test_any_global_perms(self):
        request = self.factory.get("/group/{self.object.pk}/", obj=self.object)
        request.user = self.user
        assign_perm("auth.view_group", self.user)

        response = get_40x_or_None(
            request,
            ["auth.view_group", "auth.change_group"],
            accept_global_perms=True,
            any_perm=True,
            obj=self.object,
        )
        self.assertIsNone(response)  # User has global perms, expecting None
