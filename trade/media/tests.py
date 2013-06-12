import os
import unittest

from django.db import models
from django.core.files import File as DjangoFile
from django.conf import settings

from trade.media.models import Image, ImageRelation, File, FileRelation
from trade.media.models import RelatedImagesField, RelatedFilesField


class RegularSet(models.Model):
    title = models.CharField(max_length=20)
    images = RelatedImagesField()
    files = RelatedFilesField()

class ChildSet(RegularSet):
    notes = models.TextField()

class AbstractSet(models.Model):
    title = models.CharField(max_length=20)
    images = RelatedImagesField()
    files = RelatedFilesField()

    class Meta:
        abstract = True

class AbsChildSet(AbstractSet):
    description = models.TextField(blank=True)

class AltNameModel(models.Model):
    image_attachments = RelatedImagesField()


TEST_IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'test_images')
FILES = []
for filename in os.listdir(TEST_IMAGE_DIR):
    path = os.path.join(TEST_IMAGE_DIR, filename)
    f = DjangoFile(open(path, 'r'))
    FILES.append(f)

class ImageTest(unittest.TestCase):
    def test_image_creation(self):
        image = Image()
        image.filename.save('1.jpg', FILES[0])

        if not os.path.exists(image.filename.path):
            self.fail("Image file was saved properly.")

        self.assertEqual(image.title, '1')

        image.delete()

    def test_delete(self):
        image = Image()
        image.filename.save('1.jpg', FILES[0])
        filepath = image.filename.path
        image.delete()

        if os.path.exists(filepath):
            self.fail("Associated file was not deleted after instance deletion.")

    def tearDown(self):
        Image.objects.all().delete()

class FileTest(unittest.TestCase):
    def test_file_creation(self):
        file = File()
        file.filename.save('1.jpg', FILES[0])

        if not os.path.exists(file.filename.path):
            self.fail("File file was saved properly.")

        self.assertEqual(file.title, '1')

        file.delete()

    def test_delete(self):
        file = File()
        file.filename.save('1.jpg', FILES[0])
        filepath = file.filename.path
        file.delete()

        if os.path.exists(filepath):
            self.fail("Associated file was not deleted after instance deletion.")

    def tearDown(self):
        File.objects.all().delete()


class ImageRelationTest(unittest.TestCase):
    def setUp(self):
        self.files = FILES
        for i, f in enumerate(self.files):
            image = Image()
            name, ext = os.path.splitext(f.name)
            image.filename.save('image_%s.%s' % (i, ext), f)

    def _do_relation_test(self, set_class):
        set = set_class.objects.create(title='TESTING')

        # Assign single image
        image = Image.objects.all()[0]
        set.images.add(image)
        self.assertEqual(image.relations.count(), 1, "Add one image failed.")

        # Add one image
        image2 = Image.objects.all()[1]
        set.images.add(image2)
        self.assertEqual(set.images.count(), 2, "Add a second image failed.")

        # Assign random images
        set.images = Image.objects.all().order_by('?')
        self.assertEqual(set.images.count(), len(self.files), "Adding random images failed.")

        # Test sort order change
        first_image = set.images.all()[0]
        set.images.set_order(first_image.pk, set.images.count())
        self.assertEqual(first_image.pk, set.images.all().reverse()[0].pk, "Reordering failed.")

        # Test removing an image
        set.images.remove(image)
        self.failIf(image in set.images.all(), "Image was not removed properly.")

        # Tests that related object deletion also deletes the ImageRelation
        set.delete()
        self.assertEqual(image.relations.count(), 0)
        self.assertEqual(ImageRelation.objects.count(), 0)

        # Images should still be there after though
        self.assertEqual(Image.objects.count(), len(self.files), "Image count is incorrect.")

    def test_image_relations(self):
        self._do_relation_test(RegularSet)

    def test_abstract_subclasses(self):
        self._do_relation_test(AbsChildSet)

    def test_subclass(self):
        self._do_relation_test(ChildSet)

    def test_media_registry(self):
        for klass in (RegularSet, ChildSet, AbsChildSet):
            self.failUnless(ImageRelation.relates_to(klass),
                "%s.%s was not found in the list of related models." % (klass._meta.app_label, klass._meta.object_name))
        self.failIf(ImageRelation.relates_to(AbstractSet))

    def test_alt_field_name(self):
        a = AltNameModel.objects.create()
        a.image_attachments = Image.objects.all()
        self.assertEqual(a.image_attachments.count(), len(self.files), "Failed with alternate field name")

    def tearDown(self):
        Image.objects.all().delete()

class FileRelationTest(unittest.TestCase):
    def setUp(self):
        self.files = FILES
        for i, f in enumerate(self.files):
            file = File()
            name, ext = os.path.splitext(f.name)
            file.filename.save('file_%s.%s' % (i, ext), f)

    def _do_relation_test(self, set_class):
        set = set_class.objects.create(title='TESTING')

        # Assign single file
        file = File.objects.all()[0]
        set.files.add(file)
        self.assertEqual(file.relations.count(), 1, "Add one file failed.")

        # Add one file
        file2 = File.objects.all()[1]
        set.files.add(file2)
        self.assertEqual(set.files.count(), 2, "Add a second file failed.")

        # Assign random files
        set.files = File.objects.all().order_by('?')
        self.assertEqual(set.files.count(), len(self.files), "Add random files failed")

        # Test sort order change
        first_file = set.files.all()[0]
        set.files.set_order(first_file.pk, set.files.count())
        self.assertEqual(first_file.pk, set.files.all().reverse()[0].pk, "Reordering failed.")

        # Test removing a file
        set.files.remove(file)
        self.failIf(file in set.files.all(), "File was not removed properly.")

        # Tests that related object deletion also deletes the FileRelation
        set.delete()
        self.assertEqual(file.relations.count(), 0)
        self.assertEqual(FileRelation.objects.count(), 0)

        # Files should still be there after though
        self.assertEqual(File.objects.count(), len(self.files), "File count is incorrect.")

    def test_file_relations(self):
        self._do_relation_test(RegularSet)

    def test_abstract_subclasses(self):
        self._do_relation_test(AbsChildSet)

    def test_subclass(self):
        self._do_relation_test(ChildSet)

    def test_media_registry(self):
        for klass in (RegularSet, ChildSet, AbsChildSet):
            self.failUnless(FileRelation.relates_to(klass),
                "%s.%s was not found in the list of related models." % (klass._meta.app_label, klass._meta.object_name))
        self.failIf(FileRelation.relates_to(AbstractSet))

    def tearDown(self):
        File.objects.all().delete()

