from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ExerciseForm, SignUpForm, WorkoutForm
from .models import Exercise, Workout


class WorkoutListView(LoginRequiredMixin, ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'
    context_object_name = 'workouts'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user).order_by('-date', '-id')


class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'workouts/workout_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.object.pk})


class WorkoutUpdateView(LoginRequiredMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'workouts/workout_form.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.object.pk})


class WorkoutDeleteView(LoginRequiredMixin, DeleteView):
    model = Workout
    template_name = 'workouts/workout_confirm_delete.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('workout_list')


class WorkoutToggleFinishedView(LoginRequiredMixin, View):
    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk, user=request.user)
        workout.finished = not workout.finished
        workout.save(update_fields=['finished'])
        return redirect('workout_detail', pk=pk)


class WorkoutDetailView(LoginRequiredMixin, DetailView):
    model = Workout
    template_name = 'workouts/workout_detail.html'
    context_object_name = 'workout'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)


class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workouts/exercise_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.workout = get_object_or_404(Workout, pk=kwargs['workout_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.workout = self.workout
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.workout.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workout'] = self.workout
        return context


class ExerciseToggleCompletedView(LoginRequiredMixin, View):
    def post(self, request, workout_pk, pk):
        workout = get_object_or_404(Workout, pk=workout_pk, user=request.user)
        exercise = get_object_or_404(Exercise, pk=pk, workout=workout)
        exercise.completed = not exercise.completed
        exercise.save(update_fields=['completed'])
        return redirect('workout_detail', pk=workout_pk)


class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workouts/exercise_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.workout = get_object_or_404(Workout, pk=kwargs['workout_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Exercise.objects.filter(workout=self.workout)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.workout.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workout'] = self.workout
        return context


class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = 'workouts/exercise_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.workout = get_object_or_404(Workout, pk=kwargs['workout_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Exercise.objects.filter(workout=self.workout)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.workout.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workout'] = self.workout
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse('workout_list')
