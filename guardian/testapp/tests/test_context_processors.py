from django.test import RequestFactory, TestCase
from guardian.management import create_anonymous_user
from guardian.context_processors import auth


class Test(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        create_anonymous_user(object(), using="default")

    def test_no_additional_queries_on_perms_check(self):
        """
        Verify that permission checks for the anonymous user do not result in
        additional database queries beyond the first check, thus addressing the
        "N+1 query" issue identified when using {% perms... %} in
        templates. See #6
        """
        context = auth(self.factory.get("/"))
        perms = context["perms"]

        with self.assertNumQueries(2):
            self.assertFalse(perms["auth"]["add_user"])

        with self.assertNumQueries(0):
            self.assertFalse(perms["auth"]["delete_user"])
