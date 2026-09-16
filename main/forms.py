from django.forms import ModelForm, TextInput, Textarea, Select
from main.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "category"]

        labels = {
            "title": "Project Name",
            "description": "Project Description",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "e.g Personal Portfolio",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Tell me about your project...",
                    "rows": 3,
                }
            ),
            "category": Select(
                attrs={
                    "class": "category-select",
                }
            ),
        }