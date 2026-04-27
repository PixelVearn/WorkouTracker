from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

import datetime
import json

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from .forms import ExerciseForm, SignUpForm, WorkoutForm
from .models import Exercise, Workout


class WorkoutListView(LoginRequiredMixin, ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'
    context_object_name = 'workouts'

    def get_queryset(self):
        qs = Workout.objects.filter(user=self.request.user)

        q = self.request.GET.get('q', '').strip()
        finished = (self.request.GET.get('finished') or '').strip()
        date_from_raw = (self.request.GET.get('date_from') or '').strip()
        date_to_raw = (self.request.GET.get('date_to') or '').strip()

        if q:
            qs = qs.filter(name__icontains=q)

        if finished == '1':
            qs = qs.filter(finished=True)
        elif finished == '0':
            qs = qs.filter(finished=False)

        try:
            if date_from_raw:
                date_from = datetime.date.fromisoformat(date_from_raw)
                qs = qs.filter(date__gte=date_from)
        except ValueError:
            pass

        try:
            if date_to_raw:
                date_to = datetime.date.fromisoformat(date_to_raw)
                qs = qs.filter(date__lte=date_to)
        except ValueError:
            pass

        return qs.order_by('-date', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['finished'] = (self.request.GET.get('finished') or '').strip()
        context['date_from'] = (self.request.GET.get('date_from') or '').strip()
        context['date_to'] = (self.request.GET.get('date_to') or '').strip()
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'workouts/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        workouts_qs = Workout.objects.filter(user=user)
        exercises_qs = Exercise.objects.filter(workout__user=user)

        volume_expr = ExpressionWrapper(
            F('reps') * F('weight'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )

        today = timezone.localdate()
        this_week_start = today - datetime.timedelta(days=today.weekday())

        labels = []
        volume_total = []
        volume_completed = []
        workouts_count = []
        exercises_completed_count = []

        weeks = 8
        for i in range(weeks - 1, -1, -1):
            week_start = this_week_start - datetime.timedelta(days=7 * i)
            week_end = week_start + datetime.timedelta(days=7)

            labels.append(week_start.strftime('%b %d'))
            workouts_count.append(workouts_qs.filter(date__gte=week_start, date__lt=week_end).count())
            exercises_completed_count.append(
                exercises_qs.filter(workout__date__gte=week_start, workout__date__lt=week_end, completed=True).count()
            )

            v_total = exercises_qs.filter(workout__date__gte=week_start, workout__date__lt=week_end).aggregate(
                total=Sum(volume_expr)
            )['total'] or 0
            v_completed = exercises_qs.filter(
                workout__date__gte=week_start,
                workout__date__lt=week_end,
                completed=True,
            ).aggregate(total=Sum(volume_expr))['total'] or 0

            volume_total.append(float(v_total))
            volume_completed.append(float(v_completed))

        context['labels_json'] = json.dumps(labels)
        context['volume_total_json'] = json.dumps(volume_total)
        context['volume_completed_json'] = json.dumps(volume_completed)
        context['workouts_count_json'] = json.dumps(workouts_count)
        context['exercises_completed_count_json'] = json.dumps(exercises_completed_count)

        context['weeks'] = weeks
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'workouts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        workouts_qs = Workout.objects.filter(user=user)
        exercises_qs = Exercise.objects.filter(workout__user=user)

        today = timezone.localdate()
        start_week = today - datetime.timedelta(days=today.weekday())
        start_month = today.replace(day=1)

        context['workouts_total'] = workouts_qs.count()
        context['workouts_finished'] = workouts_qs.filter(finished=True).count()
        context['workouts_week'] = workouts_qs.filter(date__gte=start_week).count()
        context['workouts_month'] = workouts_qs.filter(date__gte=start_month).count()

        context['exercises_total'] = exercises_qs.count()
        context['exercises_completed'] = exercises_qs.filter(completed=True).count()

        volume_expr = ExpressionWrapper(
            F('reps') * F('weight'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        context['total_volume'] = exercises_qs.aggregate(total=Sum(volume_expr))['total'] or 0
        context['total_volume_completed'] = exercises_qs.filter(completed=True).aggregate(
            total=Sum(volume_expr)
        )['total'] or 0

        return context


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
