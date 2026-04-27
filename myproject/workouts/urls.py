from django.urls import path

from .views import (
    AnalyticsView,
    DashboardView,
    ExerciseCreateView,
    ExerciseDeleteView,
    ExerciseToggleCompletedView,
    ExerciseUpdateView,
    WorkoutCreateView,
    WorkoutDeleteView,
    WorkoutDetailView,
    WorkoutListView,
    WorkoutToggleFinishedView,
    WorkoutUpdateView,
)

urlpatterns = [
    path('', WorkoutListView.as_view(), name='workout_list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('workouts/new/', WorkoutCreateView.as_view(), name='workout_create'),
    path('workouts/<int:pk>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path('workouts/<int:pk>/edit/', WorkoutUpdateView.as_view(), name='workout_edit'),
    path('workouts/<int:pk>/delete/', WorkoutDeleteView.as_view(), name='workout_delete'),
    path(
        'workouts/<int:pk>/toggle-finished/',
        WorkoutToggleFinishedView.as_view(),
        name='workout_toggle_finished',
    ),
    path(
        'workouts/<int:workout_pk>/exercises/new/',
        ExerciseCreateView.as_view(),
        name='exercise_create',
    ),
    path(
        'workouts/<int:workout_pk>/exercises/<int:pk>/edit/',
        ExerciseUpdateView.as_view(),
        name='exercise_edit',
    ),
    path(
        'workouts/<int:workout_pk>/exercises/<int:pk>/delete/',
        ExerciseDeleteView.as_view(),
        name='exercise_delete',
    ),
    path(
        'workouts/<int:workout_pk>/exercises/<int:pk>/toggle-completed/',
        ExerciseToggleCompletedView.as_view(),
        name='exercise_toggle_completed',
    ),
]
