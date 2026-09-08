from django.shortcuts import render

from main.models import Experience


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
    context = {
        "name": "Cindy Olivia Chai",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)