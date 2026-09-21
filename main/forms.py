from django.forms import ModelForm, TextInput, Textarea, Select, URLInput, DateTimeInput
from main.models import Project, Experience
from django import forms

class ProjectForm(ModelForm):

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Input password here",
            }
        )
    )

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

class ExperienceForm(ModelForm):
    password = forms.CharField(
            label="Password",
            widget=forms.PasswordInput(
                attrs={
                    "placeholder": "Input password here",
                }
            )
        )

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "thumbnail", "started_at", "ended_at"]

        labels = {
            "title": "Experience Title",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
            "started_at": "Start Date",
            "ended_at": "End Date",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "e.g. UI/UX Staff",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your experience...",
                    "rows": 3,
                }
            ),
            "category": Select(
                attrs={
                    "class": "category-select",
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "started_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
            "ended_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }