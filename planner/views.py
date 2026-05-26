from django.shortcuts import render, redirect, get_object_or_404

from .gemini_ai import ask_gemini
from .models import StudyTask
from .forms import StudyTaskForm
from .ml_model import predict_study_hours
from .svm_model import predict_priority_svm
from django.db.models import Case, When, Value, IntegerField, Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'planner/signup.html', {'form': form})


def ml_study_hour_prediction(task):
    priority_weight = {'High': 3, 'Medium': 2, 'Low': 1}
    difficulty_weight = {'Hard': 3, 'Medium': 2, 'Easy': 1}

    p = priority_weight.get(task.priority, 2)
    d = difficulty_weight.get(task.difficulty, 2)

    predicted_hours = round((task.hours * 0.5) + (p * 0.7) + (d * 0.6), 1)
    return predicted_hours


def ml_priority_prediction(task):
    from datetime import date

    days_left = (task.deadline - date.today()).days
    score = 0

    # Deadline factor
    if days_left <= 1:
        score += 5
    elif days_left <= 3:
        score += 3
    else:
        score += 1

    # Difficulty factor
    if task.difficulty == 'Hard':
        score += 3
    elif task.difficulty == 'Medium':
        score += 2
    else:
        score += 1

    # Hours factor
    if task.hours >= 4:
        score += 3
    elif task.hours >= 2:
        score += 2
    else:
        score += 1

    if score >= 9:
        return 'High'
    elif score >= 6:
        return 'Medium'
    else:
        return 'Low'


def ml_best_time_prediction(task):
    if task.difficulty == 'Hard':
        return 'Morning'
    elif task.priority == 'High':
        return 'Evening'
    else:
        return task.preferred_time
    



import random




def generate_weekly_timetable(tasks):
    slots = [
        "8 AM - 10 AM",
        "11 AM - 1 PM",
        "2 PM - 4 PM",
        "5 PM - 6 PM",
        "8 PM - 9 PM",
    ]

    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    task_list = list(tasks)

    weekly_plan = []

    if not task_list:
        return weekly_plan

    for slot_index, slot in enumerate(slots):
        row = {
            "time": slot,
            "monday": "",
            "tuesday": "",
            "wednesday": "",
            "thursday": "",
            "friday": "",
            "status": "ML Generated",
        }

        for day_index, day in enumerate(days):
            task_index = (slot_index + day_index) % len(task_list)
            task = task_list[task_index]
            row[day] = task.subject

        weekly_plan.append(row)

    return weekly_plan



def generate_smart_timetable(tasks):
    timetable = []

    for task in tasks:
        score = 0

        if task.priority == 'High':
            score += 5
        elif task.priority == 'Medium':
            score += 3
        else:
            score += 1

        if task.difficulty == 'Hard':
            score += 3
        elif task.difficulty == 'Medium':
            score += 2
        else:
            score += 1

        days_left = (task.deadline - date.today()).days

        if days_left <= 1:
            score += 5
        elif days_left <= 3:
            score += 3
        else:
            score += 1

        timetable.append((score, task))

    timetable.sort(reverse=True, key=lambda x: x[0])

    slots = [
        "8 AM - 10 AM",
        "11 AM - 1 PM",
        "5 PM - 6 PM",
        "8 PM - 9 PM"
    ]

    final_plan = []

    for i, item in enumerate(timetable):
        if i < len(slots):
            final_plan.append({
                "time": slots[i],
                "subject": item[1].subject
            })

    return final_plan


def get_sorted_tasks():
    return StudyTask.objects.annotate(
        priority_order=Case(
            When(priority='High', then=Value(1)),
            When(priority='Medium', then=Value(2)),
            When(priority='Low', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', 'deadline')


def get_common_context():
    tasks = get_sorted_tasks()
    completed_count = StudyTask.objects.filter(completed=True).count()
    pending_count = StudyTask.objects.filter(completed=False).count()
    total_tasks = StudyTask.objects.count()
    total_hours = StudyTask.objects.aggregate(Sum('hours'))['hours__sum'] or 0

    suggestions = []
    today = date.today()

    for task in tasks:
        predicted_hours = predict_study_hours(task)
        predicted_priority = ml_priority_prediction(task)
        best_time = ml_best_time_prediction(task)

        suggestions.append(
            f"For {task.subject}: Study {predicted_hours} hour(s). "
            f"Predicted priority: {predicted_priority}. "
            f"Best study time: {best_time}."
        )
    smart_timetable = generate_weekly_timetable(tasks)

    subject_data = StudyTask.objects.values('subject').annotate(total_hours=Sum('hours'))

    return {
        'tasks': tasks,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_tasks': total_tasks,
        'total_hours': total_hours,
        'suggestions': suggestions,
        'subjects': [i['subject'] for i in subject_data],
        'hours': [i['total_hours'] for i in subject_data],
        'today': today,
        'smart_timetable': smart_timetable,
    }


@login_required
def home(request):
    coach_reply = None

    if request.method == 'POST':
        if 'coach_message' in request.POST:
            coach_message = request.POST.get('coach_message')
            coach_reply = ask_gemini(coach_message, get_sorted_tasks())
            form = StudyTaskForm()
        else:
            form = StudyTaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.difficulty = 'Medium'
                task.preferred_time = ml_best_time_prediction(task)
                task.priority = predict_priority_svm(task)
                task.save()
                return redirect('home')
    else:
        form = StudyTaskForm()

    context = get_common_context()
    context['form'] = form
    context['coach_reply'] = coach_reply

    return render(request, 'planner/home.html', context)


@login_required
def planner_page(request):
    if request.method == 'POST':
        form = StudyTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.priority = predict_priority_svm(task)
            task.save()
            return redirect('planner_page')
    else:
        form = StudyTaskForm()

    context = get_common_context()
    context['form'] = form
    return render(request, 'planner/planner.html', context)


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(StudyTask, id=task_id)
    task.completed = True
    task.save()
    return redirect('home')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(StudyTask, id=task_id)
    task.delete()
    return redirect('home')