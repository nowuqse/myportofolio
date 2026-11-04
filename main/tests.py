from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Kombistek Teaching Assistant",
            description="Assisted the teaching and learning process for Kombistek classes at Fasilkom UI.",
            category="part-time",
            started_at=timezone.now(),
        )

        self.project = Project.objects.create(
            title="Personal Portofolio",
            description="A personal portfolio website showcasing my skills and experiences.",

            category="web",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

        response = self.client.get(reverse("main:show_main"))

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Kombistek Teaching Assistant")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, reverse("api:experience-list"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        api_response = self.client.get(reverse("api:experience-list"))

        self.assertEqual(api_response.status_code, 200)

        data = api_response.json()

        self.assertEqual(data[0]["title"], self.experience.title)
        self.assertEqual(
            data[0]["description"],
            self.experience.description,
        )
        self.assertEqual(data[0]["category_display"], "Part-Time")
        self.assertTrue(data[0]["is_ongoing"])

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("api:experience-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        self.assertFalse(self.experience.is_ongoing)

        response = self.client.get(reverse("api:experience-list"))

        self.assertEqual(response.status_code, 200)

        experience_data = response.json()[0]

        self.assertFalse(experience_data["is_ongoing"])
        self.assertIsNotNone(experience_data["ended_at"])

    def test_project_url_is_accessible(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, reverse("api:project-list"))

    def test_project_page(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "Projects")
        self.assertContains(response, "Search based on project's name")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        api_response = self.client.get(reverse("api:project-list"))

        self.assertEqual(api_response.status_code, 200)

        data = api_response.json()

        self.assertEqual(data[0]["title"], self.project.title)
        self.assertEqual(data[0]["description"], self.project.description)
        self.assertEqual(data[0]["category"], "web")

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertContains(response, "No project added.")     

    def test_project_model(self):
        self.assertEqual(str(self.project), "Personal Portofolio")
        self.assertEqual(self.project.category, "web")

    def test_project_form_url(self):
        project_form_url = reverse("main:create_project")
        response = self.client.get(project_form_url)

        self.assertRedirects(
            response,
            f'{reverse("main:login")}?next={project_form_url}',
        )

        owner = User.objects.create_superuser(
            username="test-owner",
            password="test-password",
        )
        self.client.force_login(owner)
        response = self.client.get(project_form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Project")
        self.assertTemplateUsed(response, "project_form.html")
        self.assertTemplateNotUsed(response, "index.html")


