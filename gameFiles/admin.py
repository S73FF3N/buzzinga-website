from django.contrib import admin

from .models import Tag, GameType, Category, Sound, Image, Question, Hints

class TagAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(Tag, TagAdmin)

class GameTypeAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(GameType, GameTypeAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(Category, CategoryAdmin)

class SoundAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Sound, SoundAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Image, ImageAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Question, QuestionAdmin)

class HintAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Hints, HintAdmin)

