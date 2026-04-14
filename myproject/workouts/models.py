from django.conf import settings
from django.db import models


class Workout(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    finished = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workouts',
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    completed = models.BooleanField(default=False)
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='exercises',
    )

    def __str__(self) -> str:
        return self.name
