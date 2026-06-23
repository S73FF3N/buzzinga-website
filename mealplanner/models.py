from django.db import models

class Recipe(models.Model):
    cookidoo_id    = models.CharField(max_length=100, unique=True)
    name           = models.CharField(max_length=200)
    prep_time_min  = models.IntegerField()
    is_meat        = models.BooleanField(default=False)
    last_suggested = models.DateField(null=True, blank=True)
    last_selected  = models.DateField(null=True, blank=True)
    times_selected = models.IntegerField(default=0)

    def __str__(self):
        tag = '🍖' if self.is_meat else '🌿'
        return f"{tag} {self.name} ({self.prep_time_min} min)"

class WeeklySelection(models.Model):
    DAYS = ['Mo', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    week_start    = models.DateField()
    recipes       = models.ManyToManyField(Recipe, through='DayAssignment')
    feedback_text = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

class DayAssignment(models.Model):
    DAY_CHOICES = [(d, d) for d in ['Mo', 'Mi', 'Do', 'Fr', 'Sa', 'So']]
    selection   = models.ForeignKey(WeeklySelection, on_delete=models.CASCADE)
    recipe      = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    day         = models.CharField(max_length=2, choices=DAY_CHOICES)