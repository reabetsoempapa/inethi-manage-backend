from django.test import TestCase

from . import models


class TestMeshModel(TestCase):

    def test_settings_creation(self):
        mesh = models.Mesh.objects.create(name="testmesh")
        # Check that a MeshSettings instance has been crated
        self.assertIsInstance(mesh.settings, models.Mesh)
        old_id = mesh.settings.id
        # No new settings created
        mesh.save()
        self.assertEqual(old_id, mesh.settings.id)
