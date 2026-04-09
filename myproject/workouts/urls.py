from django.urls import path

from .views import ExerciseCreateView, WorkoutCreateView, WorkoutDetailView, WorkoutListView

urlpatterns = [
    path('', WorkoutListView.as_view(), name='workout_list'),
    path('workouts/new/', WorkoutCreateView.as_view(), name='workout_create'),
    path('workouts/<int:pk>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path(
        'workouts/<int:workout_pk>/exercises/new/',
        ExerciseCreateView.as_view(),
        name='exercise_create',
    ),
]
