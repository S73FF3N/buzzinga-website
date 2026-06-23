from django.contrib import admin
from .models import Recipe, WeeklySelection, DayAssignment

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'prep_time_min', 'is_meat',
                     'last_selected', 'times_selected']
    list_filter   = ['is_meat']
    list_editable = ['is_meat', 'prep_time_min']
    ordering      = ['name']

admin.site.register(WeeklySelection)
admin.site.register(DayAssignment)
