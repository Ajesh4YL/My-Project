from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .models import Project, Task
from .forms import ProjectForm,TaskForm
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.postgres.search import SearchQuery, SearchRank
from .forms import SearchForm
from django.db.models import F,Q,Count
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('email_confirmation')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})

def email_confirmation(request):
    return render(request, 'registration/email_confirmation.html')

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
@permission_required('aj.can_view_project', raise_exception=True)
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not request.user.has_perm('aj.can_view_project', project):
        raise PermissionDenied
    return render(request, 'project_detail.html', {'project': project})

@login_required
@permission_required('aj.can_edit_project', raise_exception=True)
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not request.user.has_perm('aj.can_edit_project', project):
        raise PermissionDenied
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_form.html', {'form': form})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m() 
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tasks = project.tasks.all()
    return render(request, 'tasks/task_list.html', {'project': project, 'tasks': tasks})

@login_required
@permission_required('aj.can_view_task', raise_exception=True)
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not request.user.has_perm('aj.can_view_task', task):
        raise PermissionDenied
    return render(request, 'task_detail.html', {'task': task})

@login_required
@permission_required('aj.can_edit_task', raise_exception=True)
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not request.user.has_perm('aj.can_edit_task', task):
        raise PermissionDenied
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('task_list', project_id=project.pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'project': project})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'project': task.project})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list', project_id=task.project.pk)
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def dashboard(request):
    user = request.user
    
    tasks = Task.objects.filter(assigned_to=user).order_by('status')
    task_groups = {
        'TODO': tasks.filter(status='TODO'),
        'INPROGRESS': tasks.filter(status='INPROGRESS'),
        'DONE': tasks.filter(status='DONE')
    }
    
    projects = Project.objects.filter(team_members=user)
    
    upcoming_tasks = Task.objects.filter(
        assigned_to=user,
        due_date__gte=now().date()
    ).order_by('due_date')
    
    return render(request, 'dashboard.html', {
        'task_groups': task_groups,
        'projects': projects,
        'upcoming_tasks': upcoming_tasks
    })

@login_required
@require_POST
def update_task_status(request):
    task_id = request.POST.get('task_id')
    status = request.POST.get('status')

    task = Task.objects.get(pk=task_id)
    task.status = status
    task.save()

    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def update_task_assignment(request):
    task_id = request.POST.get('task_id')
    user_id = request.POST.get('user_id')

    task = Task.objects.get(pk=task_id)
    task.assigned_to_id = user_id
    task.save()

    return JsonResponse({'status': 'success'})

def search(request):
    form = SearchForm(request.GET or None)
    tasks = []
    projects = []

    if form.is_valid():
        query = form.cleaned_data['query']
        search_query = SearchQuery(query)

        tasks = Task.objects.annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(rank__gte=0.1).order_by('-rank')

        projects = Project.objects.annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(rank__gte=0.1).order_by('-rank')

    return render(request, 'search_results.html', {
        'form': form,
        'tasks': tasks,
        'projects': projects
    })

@login_required
@permission_required('aj.can_manage_team', raise_exception=True)
def manage_team(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        raise PermissionDenied
    return render(request, 'manage_team.html', {'project': project})

def filter_tasks(request):
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    assignee = request.GET.get('assignee')
    
    tasks = Task.objects.all()
    
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if assignee:
        tasks = tasks.filter(assigned_to_id=assignee)
    
    html = render_to_string('task_list.html', {'tasks': tasks})
    return JsonResponse({'html': html})

@login_required
def report(request):
    user = request.user

    tasks_by_project_status = Task.objects.values('project__name', 'status').annotate(count=Count('id')).order_by('project__name')
    overdue_tasks = Task.objects.filter(due_date__lt=now().date(), status__ne='DONE')
    tasks_assigned = Task.objects.filter(assigned_to=user)
    tasks_completed = tasks_assigned.filter(status='DONE')
    tasks_pending = tasks_assigned.filter(status__ne='DONE')
    projects = Project.objects.all()
    project_names = [p.name for p in projects]
    task_counts_by_project = [
        Task.objects.filter(project=p).count() for p in projects
    ]

    context = {
        'tasks_by_project_status': tasks_by_project_status,
        'overdue_tasks': overdue_tasks,
        'tasks_completed': tasks_completed.count(),
        'tasks_pending': tasks_pending.count(),
        'project_names': project_names,
        'task_counts_by_project': task_counts_by_project
    }
    
    return render(request, 'report.html', context)