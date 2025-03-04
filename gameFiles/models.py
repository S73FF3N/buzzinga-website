from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.dispatch import receiver

import os
from datetime import date
import unicodedata
from pathlib import Path

upload_storage = FileSystemStorage(location=settings.UPLOAD_ROOT, base_url='/uploads')

import random

DIFFICULTY = [(i + 1, i + 1) for i in range(10)]

LICENSE = (
    ('CC0', 'Creative Commons Zero Public Domain'),
    ('CC BY', 'Creative Commons Attribution'),
    ('CC BY-SA', 'Creative Commons Attribution-ShareAlike')
)

GAME_TYPE_FOLDER_MAP = {
    2: "sounds",
    1: "images",
}

class Tag(models.Model):
    name_de = models.CharField(max_length=50)

    class Meta:
        ordering = ['name_de']

    def amount_elements_with_tag(self, category):
        related_objects = category.get_related_objects()
        return related_objects.filter(tags__in=[self]).count() if related_objects else 0

    def __str__(self):
        return self.name_de


class GameType(models.Model):
    name_de = models.CharField(max_length=50, verbose_name="Name")
    logo = models.CharField(max_length=20, blank=True)
    available = models.BooleanField(default=True)

    def amount_categories(self):
        categories = Category.objects.filter(game_type=self, private=False)
        return categories.count()

    def __str__(self):
        return self.name_de


class CategoryManager(models.Manager):
    def public_for_game_type(self, game_type):
        return self.filter(game_type=game_type, private=False)
    

class Category(models.Model):
    objects = CategoryManager()
    
    name_de = models.CharField(max_length=50, verbose_name="Name")
    game_type = models.ForeignKey(GameType, default=1, on_delete=models.CASCADE, verbose_name="Spielart", related_name="categories")
    description_de = models.TextField(verbose_name="Beschreibung")
    private = models.BooleanField(default=False, verbose_name="Privat")
    logo = models.CharField(max_length=20, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey('auth.User', default=1, on_delete=models.SET_DEFAULT)

    def get_related_objects(self):
        model_map = {
            2: self.sound_set,
            1: self.image_set,
            4: self.question_set,
            3: self.hints_set,
            5: self.whoknowsmore_set,
        }
        return model_map.get(self.game_type.id, self.category_set.none())

    @property
    def amount_files(self):
        related_objects = self.get_related_objects()
        return related_objects.filter(private_new=False).count() if related_objects else 0
    
    def tags_used(self):
        related_objects = self.get_related_objects()
        return Tag.objects.filter(categoryelement__in=related_objects, categoryelement__private_new=False).distinct()

    def examples(self):
        related_objects = self.get_related_objects().filter(private_new=False)
        category_element_id_list = list(related_objects.values_list('id', flat=True))
        random_category_element_id_list = random.sample(category_element_id_list, min(len(category_element_id_list), 5))
        return related_objects.filter(id__in=random_category_element_id_list)

    def latest_elements(self):
        related_objects = self.get_related_objects()
        if related_objects.exists():
            latest_create_date = related_objects.order_by('-created_on').first().created_on.date()
            amount_elements = related_objects.filter(created_on__date=latest_create_date).count()
        else:
            latest_create_date = date(1900, 1, 1)
            amount_elements = 0
        return {'category_name': self.name_de, 'amount_elements': amount_elements, 'latest_create_date': latest_create_date}

    def __str__(self):
        return self.name_de


class CategoryElement(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategorie")
    private_new = models.BooleanField(default=False, verbose_name="Privat")
    explicit = models.BooleanField(default=False, verbose_name="Explizit")
    solution = models.CharField(max_length=80, verbose_name="Lösung")
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY, verbose_name="Schwierigkeit")
    tags = models.ManyToManyField(Tag, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey('auth.User', default=1, on_delete=models.SET_DEFAULT)

    class Meta:
        abstract = True
        unique_together = ('solution', 'category')

    def __str__(self):
        return self.solution

    def clean_filename(name):
        return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8").replace(" ", "_")

    def get_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        filename_solution = f"{CategoryElement.clean_filename(instance.solution)}.{ext}"
        return f"{instance.category.game_type.name_de}/{instance.category.name_de}/{filename_solution}"


def get_upload_path(instance, filename): 
    """Generate the upload path dynamically based on the game type and category name."""
    
    # Ensure category exists
    if not instance.category:
        return os.path.join("uncategorized", filename)

    # Get game type folder, defaulting to 'other' if not mapped
    game_type = GAME_TYPE_FOLDER_MAP.get(instance.category.game_type.id, "other")

    # Format category name safely
    category_name = instance.category.name_de.replace(" ", "_")

    return os.path.join(game_type, category_name, filename)


class Image(CategoryElement):
    image_file = models.ImageField(upload_to=get_upload_path, storage=upload_storage, verbose_name="Bilddatei")
    author = models.CharField(max_length=50, verbose_name="Urheber")
    license = models.CharField(choices=LICENSE, max_length=100, verbose_name="Lizenz")
    file_changed = models.BooleanField(default=False, verbose_name="Datei bearbeitet?")


class Sound(CategoryElement):
    sound_file = models.FileField(upload_to=get_upload_path, storage=upload_storage, verbose_name="Sounddatei")


class Question(CategoryElement):
    quiz_question = models.CharField(max_length=150, verbose_name="Frage")
    option1 = models.CharField(max_length=80, verbose_name="Option 1")
    option2 = models.CharField(max_length=80, verbose_name="Option 2")
    option3 = models.CharField(max_length=80, verbose_name="Option 3")


class Hints(CategoryElement):
    hint1 = models.CharField(max_length=80, verbose_name="Hinweis 1")
    hint2 = models.CharField(max_length=80, verbose_name="Hinweis 2")
    hint3 = models.CharField(max_length=80, verbose_name="Hinweis 3")
    hint4 = models.CharField(max_length=80, verbose_name="Hinweis 4")
    hint5 = models.CharField(max_length=80, verbose_name="Hinweis 5")
    hint6 = models.CharField(max_length=80, verbose_name="Hinweis 6")
    hint7 = models.CharField(max_length=80, verbose_name="Hinweis 7")
    hint8 = models.CharField(max_length=80, verbose_name="Hinweis 8")
    hint9 = models.CharField(max_length=80, verbose_name="Hinweis 9")
    hint10 = models.CharField(max_length=80, verbose_name="Hinweis 10")


class WhoKnowsMore(CategoryElement):
    def show_solution(self):
        return self.answers.all().order_by('answer')


class WhoKnowsMoreElement(models.Model):
    category_element = models.ForeignKey(WhoKnowsMore, related_name="answers", on_delete=models.CASCADE)
    answer = models.CharField(max_length=80, verbose_name="Antwort")
    count_id = models.IntegerField(blank=True, null=True)



def _delete_file(path):
    Path(path).unlink(missing_ok=True)


@receiver(models.signals.post_delete, sender=Image)
@receiver(models.signals.post_delete, sender=Sound)
def delete_file(sender, instance, *args, **kwargs):
    file_path = getattr(instance, "image_file", None) or getattr(instance, "sound_file", None)
    if file_path and hasattr(file_path, "path"):
        _delete_file(file_path.path)
