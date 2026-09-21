from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Experience, Project
from main.forms import ProjectForm, ExperienceForm
from django.conf import settings

def show_main(request):
    context = {
        "name": "Cindy Olivia Chai",
        "npm": "2506615753",
        "study_program": "S1 Information Systems",
        "bio": (
            "When I'm not coding or designing, you'll probably find me "
            "listening to music or doing something creative :D"
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    json_response = get_experience_json(request)

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
    }

    return render(request, "experience.html", context)

def show_project(request):
    json_response = get_projects_json(request)

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
    }
    return render(request, "project.html", context)

def create_experience(request):
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

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        if password == settings.PASS:
            form.save()
            messages.success(request, "New project added!")
            return redirect("main:show_project")

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

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience = Experience.objects.all()

    if title_query:
        experience = experience.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experience)
    return HttpResponse(experience_json, content_type="application/json")


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted")
        return redirect("main:show_project")

    return redirect("main:show_project")

def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience updated!")
        return redirect("main:show_experience")

    context = {
        "name": "Cindy Olivia Chai",
        "form": form,
        "experience": experience,
    }

    return render(request, "experience_update_form.html", context)