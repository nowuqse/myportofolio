import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    # Menyiapkan pengguna, Project, URL API, dan payload untuk setiap test Project.
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )

        self.visitor = User.objects.create_user(
            username="visitor",
            password="test-password",
        )

        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            category="web",
        )

        self.list_url = reverse(
            "api:project-list"
        )

        self.detail_url = reverse(
            "api:project-detail",
            args=[self.project.id],
        )

        self.star_url = reverse(
            "api:project-star",
            args=[self.project.id],
        )

        self.payload = {
            "title": "New project",
            "description": "A useful application",
            "category": "web",
        }


    # Memastikan pengunjung dapat membaca daftar dan detail Project yang aman.
    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[0]["id"],
            str(self.project.id),
        )

        self.assertEqual(
            response.data[0]["category"],
            "web",
        )

        self.assertFalse(
            response.data[0]["is_starred"]
        )

        self.assertNotIn(
            "fields",
            response.data[0],
        )

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


    # Memastikan pencarian Project tidak peka huruf besar dan menangani hasil kosong.
    def test_search_and_empty_results(self):
        response = self.client.get(
            self.list_url,
            {"title": "PORT"},
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        response = self.client.get(
            self.list_url,
            {"title": "not-found"},
        )

        self.assertEqual(
            response.data,
            [],
        )


    # Memastikan UUID Project yang tidak tersedia menghasilkan status 404.
    def test_missing_project(self):
        url = reverse(
            "api:project-detail",
            args=[uuid.uuid4()],
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    # Memastikan pengunjung dan pengguna biasa tidak dapat mengubah Project.
    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(
                user=user
            )

            response = self.client.post(
                self.list_url,
                self.payload,
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

            response = self.client.patch(
                self.detail_url,
                {"title": "Changed"},
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

            response = self.client.delete(
                self.detail_url
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(
            Project.objects.count(),
            1,
        )

        self.project.refresh_from_db()

        self.assertEqual(
            self.project.title,
            "Portfolio",
        )


    # Memastikan pemilik portofolio dapat membuat Project baru.
    def test_owner_can_create(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Project.objects.filter(
                pk=response.data["id"]
            ).exists()
        )


    # Memastikan serializer menolak field kosong, XSS, dan kategori tidak valid.
    def test_validation(self):
        self.client.force_authenticate(
            user=self.owner
        )

        invalid_inputs = [
            (
                {"title": "   "},
                "title",
            ),
            (
                {
                    "title": (
                        '<img src="x" '
                        'onerror="alert(1)">'
                    )
                },
                "title",
            ),
            (
                {"category": "invalid-category"},
                "category",
            ),
        ]

        for changes, error_field in invalid_inputs:
            response = self.client.post(
                self.list_url,
                {
                    **self.payload,
                    **changes,
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )

            self.assertIn(
                error_field,
                response.data,
            )

        self.assertEqual(
            Project.objects.count(),
            1,
        )


    # Memastikan PATCH, PUT, dan DELETE mengikuti perilaku serta status yang benar.
    def test_patch_put_and_delete(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.project.refresh_from_db()

        self.assertEqual(
            self.project.title,
            "Changed",
        )

        self.assertEqual(
            self.project.description,
            "My website",
        )

        self.assertEqual(
            self.project.category,
            "web",
        )

        response = self.client.put(
            self.detail_url,
            {"title": "Incomplete"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        response = self.client.put(
            self.detail_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.project.refresh_from_db()

        self.assertEqual(
            self.project.title,
            self.payload["title"],
        )

        self.assertEqual(
            self.project.category,
            self.payload["category"],
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertEqual(
            response.content,
            b"",
        )

        self.assertFalse(
            Project.objects.filter(
                pk=self.project.id
            ).exists()
        )


    # Memastikan star memerlukan login serta dapat diaktifkan dan dibatalkan.
    def test_star_requires_login_and_toggles(self):
        response = self.client.post(
            self.star_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(
            user=self.visitor
        )

        response = self.client.post(
            self.star_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["is_starred"]
        )

        self.assertEqual(
            response.data["star_count"],
            1,
        )

        response = self.client.post(
            self.star_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["is_starred"]
        )

        self.assertEqual(
            response.data["star_count"],
            0,
        )


    # Memastikan field hasil perhitungan tidak dapat dipalsukan oleh client.
    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
                "starred_by": [
                    self.visitor.id
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["star_count"],
            0,
        )

        self.assertFalse(
            response.data["is_starred"]
        )

        created_project = Project.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            created_project.starred_by.count(),
            0,
        )


    # Memastikan status staff atau Editor tidak memberi hak mengelola Project.
    def test_staff_and_editor_cannot_manage_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()

        editor_group = Group.objects.create(
            name="Editor"
        )

        self.visitor.groups.add(
            editor_group
        )

        self.client.force_authenticate(
            user=self.visitor
        )

        response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    # Memastikan method yang tidak didukung menghasilkan status 405.
    def test_wrong_method(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.delete(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )


    # Memastikan request session tanpa token CSRF ditolak oleh server.
    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(
            enforce_csrf_checks=True
        )

        logged_in = client.login(
            username="owner",
            password="test-password",
        )

        self.assertTrue(logged_in)

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Project.objects.count(),
            1,
        )


    # Memastikan request session dengan token CSRF yang benar dapat diproses.
    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(
            enforce_csrf_checks=True
        )

        logged_in = client.login(
            username="owner",
            password="test-password",
        )

        self.assertTrue(logged_in)

        page = client.get(
            self.list_url,
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(
            page.status_code,
            status.HTTP_200_OK,
        )

        token = client.cookies[
            "csrftoken"
        ].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class ExperienceAPITest(APITestCase):
    # Menyiapkan setiap peran, Experience, URL API, dan payload untuk setiap test.
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

    # Memastikan pengunjung dapat membaca, mencari, dan melihat detail Experience.
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

    # Memastikan pemilik dapat membuat, memperbarui, dan menghapus Experience.
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

    # Memastikan Editor hanya dapat update tanpa hak membuat atau menghapus data.
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

    # Memastikan pengunjung tanpa login tidak dapat mengubah database Experience.
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

    # Memastikan pengguna biasa tidak dapat membuat, update, atau menghapus data.
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

    # Memastikan pengguna login dapat memberi dan membatalkan star Experience.
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

    # Memastikan pengunjung tanpa login ditolak dan tidak tercatat sebagai pemberi star.
    def test_unauthenticated_user_cannot_star(self):
        response = self.client.post(
            self.star_url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.experience.starred_by.exists())

    # Memastikan request session tanpa token CSRF ditolak dan database tidak berubah.
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

    # Memastikan serializer Experience menolak nilai kosong, HTML, dan kategori salah.
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
