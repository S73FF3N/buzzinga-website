from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.dispatch import receiver

import os

upload_storage = FileSystemStorage(location=settings.UPLOAD_ROOT, base_url='/uploads')

import random

DIFFICULTY = [(i+1,i+1) for i in range(10)]

LICENSE = (
    ('CC0', 'Creative Commons Zero Public Domain'),
    ('CC BY', 'Creative Commons Attribution'),
    ('CC BY-SA', 'Creative Commons Attribution-ShareAlike')
)


class Tag(models.Model):
    name_de = models.CharField(max_length=50)

    class Meta:
        ordering = ['name_de']

    def amount_elements_with_tag(self, category):
        if category.game_type.id == 1:
            elements = Sound.objects.filter(category=category, tags__in=[self])
        elif category.game_type.id == 2:
            elements = Image.objects.filter(category=category, tags__in=[self])
        elif category.game_type.id == 3:
            elements = Question.objects.filter(category=category, tags__in=[self])
        else:
            elements = Hints.objects.filter(category=category, tags__in=[self])
        return len(elements)

    def __str__(self):
        return self.name_de

class GameType(models.Model):
    name_de = models.CharField(max_length=50)
    logo = models.CharField(max_length=20, blank=True)
    available = models.BooleanField(default=True)

    def amount_categories(self):
        categories = Category.objects.filter(game_type=self, private=False)
        return len(categories)

    def __str__(self):
        return self.name_de

class Category(models.Model):
    name_de = models.CharField(max_length=50)
    game_type = models.ForeignKey(GameType, default=1, on_delete=models.CASCADE, )
    description_de = models.TextField()
    private = models.BooleanField(default=False)
    logo = models.CharField(max_length=20, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey('auth.User', default=1, on_delete=models.SET_DEFAULT)

    def amount_files(self):
        if self.game_type.id == 1:
            files = Sound.objects.filter(category=self, private_new=False)
        elif self.game_type.id == 2:
            files = Image.objects.filter(category=self, private_new=False)
        elif self.game_type.id == 3:
            files = Question.objects.filter(category=self, private_new=False)
        else:
            files = Hints.objects.filter(category=self, private_new=False)
        return len(files)

    def tags_used(self):
        if self.game_type.id == 1:
            elements = Sound.objects.filter(category=self, private_new=False)
        elif self.game_type.id == 2:
            elements = Image.objects.filter(category=self, private_new=False)
        elif self.game_type.id == 3:
            elements = Question.objects.filter(category=self, private_new=False)
        else:
            elements = Hints.objects.filter(category=self, private_new=False)
        used_tags = []
        for e in elements:
            for tag in e.tags.all():
                if tag not in used_tags:
                    used_tags.append(tag)
        return used_tags

    def examples(self):
        if self.game_type.id == 1:
            categoryElement_id_list = list(Sound.objects.filter(category=self, private_new=False).values_list('id', flat=True))
        elif self.game_type.id == 2:
            categoryElement_id_list = list(Image.objects.filter(category=self, private_new=False).values_list('id', flat=True))
        elif self.game_type.id == 3:
            categoryElement_id_list = list(Question.objects.filter(category=self, private_new=False).values_list('id', flat=True))
        else:
            categoryElement_id_list = list(
                Hints.objects.filter(category=self, private_new=False).values_list('id', flat=True))
        random_categoryElement_id_list = random.sample(categoryElement_id_list, min(len(categoryElement_id_list), 5))
        if self.game_type.id == 1:
            elements = Sound.objects.filter(id__in=random_categoryElement_id_list)
        elif self.game_type.id == 2:
            elements = Image.objects.filter(id__in=random_categoryElement_id_list)
        elif self.game_type.id == 3:
            elements = Question.objects.filter(id__in=random_categoryElement_id_list)
        else:
            elements = Hints.objects.filter(id__in=random_categoryElement_id_list)
        return elements

    def latest_elements(self):
        print(self)
        if self.game_type.id == 1:
            latest_create_date = Sound.objects.filter(category=self).order_by('-created_on')[0].created_on
            amount_elements = Sound.objects.filter(category=self, created_on=latest_create_date).count()
        elif self.game_type.id == 2:
            latest_create_date = Image.objects.filter(category=self).order_by('-created_on')[0].created_on
            amount_elements = Image.objects.filter(category=self, created_on=latest_create_date).count()
        elif self.game_type.id == 3:
            latest_create_date = Question.objects.filter(category=self).order_by('-created_on')[0].created_on
            amount_elements = Question.objects.filter(category=self, created_on=latest_create_date).count()
        else:
            latest_create_date = Hints.objects.filter(category=self).order_by('-created_on')[0].created_on
            amount_elements = Hints.objects.filter(category=self, created_on=latest_create_date).count()
        return {'category_name': self.name_de, 'amount_elements': amount_elements, 'latest_create_date': latest_create_date}

    def __str__(self):
        return self.name_de

class CategoryElement(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    private_new = models.BooleanField(default=False)
    explicit = models.BooleanField(default=False)
    solution = models.CharField(max_length=80)
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY)
    tags = models.ManyToManyField(Tag, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey('auth.User', default=1, on_delete=models.SET_DEFAULT)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['solution', 'category'], name='%(class)s_unique_solution_per_category')
        ]

    def __str__(self):
        return self.solution

def get_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    solution = instance.solution.replace(" ", "_")
    filename_solution = solution+"."+ext
    return '{0}/{1}/{2}'.format(instance.category.game_type.name_de, instance.category.name_de, filename_solution)

class Image(CategoryElement):
    image_file = models.ImageField(upload_to=get_upload_path, storage=upload_storage)
    author = models.CharField(max_length=50)
    license = models.CharField(choices=LICENSE, max_length=100)
    file_changed = models.BooleanField(default=False)


class Sound(CategoryElement):
    sound_file = models.FileField(upload_to=get_upload_path, storage=upload_storage)

class Question(CategoryElement):
    quiz_question = models.CharField(max_length=150)
    option1 = models.CharField(max_length=80)
    option2 = models.CharField(max_length=80)
    option3 = models.CharField(max_length=80)

class Hints(CategoryElement):
    hint1 = models.CharField(max_length=80)
    hint2 = models.CharField(max_length=80)
    hint3 = models.CharField(max_length=80)
    hint4 = models.CharField(max_length=80)
    hint5 = models.CharField(max_length=80)
    hint6 = models.CharField(max_length=80)
    hint7 = models.CharField(max_length=80)
    hint8 = models.CharField(max_length=80)
    hint9 = models.CharField(max_length=80)
    hint10 = models.CharField(max_length=80)

def _delete_file(path):
   """ Deletes file from filesystem. """
   if os.path.isfile(path):
       os.remove(path)

@receiver(models.signals.post_delete, sender=Image)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.image_file:
        _delete_file(instance.image_file.path)

