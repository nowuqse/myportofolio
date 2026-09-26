from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from main.models import Experience, Project
from main.forms import ProjectForm, ExperienceForm
from django.contrib.auth.decorators import login_required 
from django.core.exceptions import PermissionDenied       
from django.conf import settings
import datetime

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Cindy Olivia Chai",
        "npm": "2506615753",
        "study_program": "S1 Information Systems",
        "bio": (
            "When I'm not coding or designing, you'll probably find me "
            "listening to music or doing something creative :D"
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

def show_experience(request):
    json_response = get_experience_json(request)
    is_editor = (request.user.is_authenticated and request.user.groups.filter(name="Editor").exists())

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    experiences = [
        experience.object for experience in experiences
    ]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Cindy Olivia Chai",
        "experience_list": experiences,
        "title_query": title_query,
        "is_editor": is_editor,
    }

    return render(request, "experience.html", context)

def show_project(request):
    json_response = get_projects_json(request)
    is_editor = (request.user.is_authenticated and request.user.groups.filter(name="Editor").exists())

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Cindy Olivia Chai",
        "project_list": projects,
        "title_query": title_query,
        "is_editor": is_editor,
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/") 
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        if password == settings.PASS:
            form.save()
            messages.success(request, "New experience added!")
            return redirect("main:show_experience")

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/") 
def create_project(request):   
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        if password == settings.PASS:
            form.save()
            messages.success(request, "New project added!")
            return redirect("main:show_project")
        else:
            messages.error(request, "Incorrect password!")
    
    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
    }
    return render(request, "project_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience = Experience.objects.all()

    if title_query:
        experience = experience.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experience)
    return HttpResponse(experience_json, content_type="application/json")

@login_required(login_url="/login/") 
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

@login_required(login_url="/login/") 
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted")
        return redirect("main:show_project")

    return redirect("main:show_project")

@login_required(login_url="/login/") 
def update_experience(request, experience_id):
    is_editor = request.user.groups.filter(name="Editor").exists()
    if not request.user.is_superuser or is_editor:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        if password == settings.PASS:
            form.save()
            messages.success(request, "Experience updated!")
            return redirect("main:show_experience")

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
        "experience": experience,
    }

    return render(request, "experience_update_form.html", context)

@login_required(login_url="/login/") 
def update_project(request, project_id):
    is_editor = request.user.groups.filter(name="Editor").exists()
    if not request.user.is_superuser or is_editor:
        raise PermissionDenied
    
    project = get_object_or_404(project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        if password == settings.PASS:
            form.save()
            messages.success(request, "Project updated!")
            return redirect("main:show_project")

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
        "project": project,
    }

    return render(request, "project_update_form.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_project")