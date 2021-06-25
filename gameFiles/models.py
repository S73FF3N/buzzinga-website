from django.db import models

import random

DIFFICULTY = [(i+1,i+1) for i in range(10)]

class Tag(models.Model):
    name_de = models.CharField(max_length=50)

    class Meta:
        ordering = ['name_de']

    def amount_elements_with_tag(self, category):
        elements = CategoryElement.objects.filter(category=category, tags__in=[self])
        return len(elements)

    def __str__(self):
        return self.name_de

class GameType(models.Model):
    name_de = models.CharField(max_length=50)
    logo = models.CharField(max_length=20, blank=True)
    available = models.BooleanField(default=True)

    def amount_categories(self):
        categories = Category.objects.filter(game_type=self)
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
        files = CategoryElement.objects.filter(category=self, private_new=False)
        return len(files)

    def tags_used(self):
        elements = CategoryElement.objects.filter(category=self, private_new=False)
        used_tags = []
        for e in elements:
            for tag in e.tags.all():
                if tag not in used_tags:
                    used_tags.append(tag)
        return used_tags

    def examples(self):
        categoryElement_id_list = list(CategoryElement.objects.filter(category=self, private_new=False).values_list('id', flat=True))
        random_categoryElement_id_list = random.sample(categoryElement_id_list, min(len(categoryElement_id_list), 5))
        elements = CategoryElement.objects.filter(id__in=random_categoryElement_id_list)
        return elements

    def __str__(self):
        return self.name_de

class CategoryElement(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, )
    private_new = models.BooleanField(default=False)
    explicit = models.BooleanField(default=False)
    solution = models.CharField(max_length=80)
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY)
    tags = models.ManyToManyField(Tag, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey('auth.User', default=1, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return self.solution

def get_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    solution = instance.solution.replace(" ", "_")
    filename_solution = solution+"."+ext
    return '{0}/{1}/{2}'.format(instance.category.game_type.name_de, instance.category.name_de, filename_solution)

class Image(CategoryElement):
    image_file = models.ImageField(upload_to=get_upload_path)
    #user_holds_rights = models.BooleanField(default=False)
    #source = models.CharField(max_length=100)

class Sound(CategoryElement):
    sound_file = models.FileField(upload_to=get_upload_path)
    #user_holds_rights = models.BooleanField(default=False)
    #source = models.CharField(max_length=100)

class Question(CategoryElement):
    quiz_question = models.CharField(max_length=80)
    option1 = models.CharField(max_length=80)
    option2 = models.CharField(max_length=80)
    option3 = models.CharField(max_length=80)

