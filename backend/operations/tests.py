from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User


class AuthFlowTests(APITestCase):
    """
    Simple smoke tests for token auth and the /api/users/me/ endpoint.

    Why this exists:
    - To quickly catch if authentication or basic API wiring breaks.
    - To give you a very fast "does it still work?" check after changes.
    """

    def setUp(self):
        """
        Create a test user we can use to log in and get a token.
        """
        self.username = "testuser"
        self.password = "testpassword123"

        # Use the custom User model's create_user helper.
        self.user = User.objects.create_user(
            username=self.username,
            email="testuser@example.com",
            password=self.password,
        )

    def test_obtain_token_and_get_current_user(self):
        """
        1. Get a token from /api/token-auth/.
        2. Call /api/users/me/ with that token.
        3. Check that we get 200 OK and the correct username.
        """
        # 1) Get token
        token_url = reverse("api_token_auth")
        response = self.client.post(
            token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # Response should be 200 and contain a "token" key
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        token = response.data["token"]

        # 2) Use the token to call /api/users/me/
        # REST framework TokenAuthentication expects header: "Authorization: Token <token>"
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me_url = "/api/users/me/"
        response = self.client.get(me_url)

        # 3) Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.username)
