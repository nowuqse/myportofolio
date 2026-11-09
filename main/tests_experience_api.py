from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="experience-owner",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="experience-editor",
            password="test-password",
        )
        self.visitor = User.objects.create_user(
            username="experience-visitor",
            password="test-password",
        )

        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

        self.experience = Experience.objects.create(
            title="Teaching Assistant",
            description="Assisted students.",
            category="part-time",
            started_at=timezone.now(),
        )

        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.id],
        )
        self.star_url = reverse(
            "api:experience-star",
            args=[self.experience.id],
        )
        self.payload = {
            "title": "Research Assistant",
            "description": "Conducted research.",
            "category": "research",
            "thumbnail": "",
            "started_at": timezone.now().isoformat(),
            "ended_at": None,
        }

    def test_public_can_read_list_detail_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertEqual(response.data[0]["category_display"], "Part-Time")

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.list_url,
            {"title": "not-found", "category": "research"},
        )
        self.assertEqual(response.data, [])

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.patch(
            self.detail_url,
            {"title": "Updated by owner"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Updated by editor"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated by editor")

        initial_count = Experience.objects.count()
        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), initial_count)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Experience.objects.filter(pk=self.experience.id).exists()
        )

    def test_unauthenticated_user_cannot_write(self):
        initial_count = Experience.objects.count()
        original_title = self.experience.title

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), initial_count)

        response = self.client.patch(
            self.detail_url,
            {"title": "Forbidden update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, original_title)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Experience.objects.filter(pk=self.experience.id).exists()
        )

    def test_regular_user_cannot_write(self):
        self.client.force_authenticate(user=self.visitor)

        initial_count = Experience.objects.count()
        original_title = self.experience.title

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), initial_count)

        response = self.client.patch(
            self.detail_url,
            {"title": "Forbidden update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, original_title)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Experience.objects.filter(pk=self.experience.id).exists()
        )

    def test_authenticated_user_can_star_and_unstar(self):
        self.client.force_authenticate(user=self.visitor)

        response = self.client.post(
            self.star_url,
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.experience.starred_by.filter(pk=self.visitor.pk).exists()
        )
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(
            self.star_url,
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            self.experience.starred_by.filter(pk=self.visitor.pk).exists()
        )
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_unauthenticated_user_cannot_star(self):
        response = self.client.post(
            self.star_url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.experience.starred_by.exists())

    def test_session_request_without_csrf_token_is_rejected(self):
        csrf_client = APIClient(enforce_csrf_checks=True)
        logged_in = csrf_client.login(
            username="experience-owner",
            password="test-password",
        )
        self.assertTrue(logged_in)

        initial_count = Experience.objects.count()
        response = csrf_client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), initial_count)

    def test_serializer_rejects_invalid_input(self):
        self.client.force_authenticate(user=self.owner)

        for changes, error_field in (
            ({"title": "   "}, "title"),
            ({"description": "<b></b>"}, "description"),
            ({"category": "invalid-category"}, "category"),
        ):
            response = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            self.assertIn(error_field, response.data)
