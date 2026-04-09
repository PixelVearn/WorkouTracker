from django import forms

from .models import Exercise, Workout


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'reps', 'weight']
