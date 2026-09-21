from django.urls import path

from main.views import show_main, show_experience, show_project, create_project, get_projects_json, delete_project, create_experience, get_experience_json, delete_experience, update_experience, update_project

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("project/", show_project, name="show_project"),
    path("project/add/", create_project, name="create_project"),
    path("experience/add/", create_experience, name="create_experience"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("project/<uuid:project_id>/delete/", delete_project,name="delete_project"),
    path("experience/<uuid:experience_id>/delete/", delete_experience,name="delete_experience"),
    path("experience/<uuid:experience_id>/update/", update_experience, name="update_experience"),
    path("project/<uuid:project_id>/update/", update_project, name="update_project"),
]