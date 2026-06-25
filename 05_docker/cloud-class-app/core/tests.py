from django.test import TestCase
from django.urls import reverse


class CoreViewTests(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cloud Class")
        self.assertContains(response, "로컬에서 개발하고 AWS에 배포")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "service": "cloud-class-app"},
        )

    def test_info_endpoint(self):
        response = self.client.get(reverse("info"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "cloud-class-app")
        self.assertIn("environment", response.json())
        self.assertIn("version", response.json())
