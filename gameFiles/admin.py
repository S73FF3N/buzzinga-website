import json
from django.shortcuts import redirect
from django.urls import path
from django.contrib import admin, messages
from django.core.files.storage import default_storage
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.contrib.auth.models import User
from .models import (
    Tag, GameType, Category, Sound, Image, Question, Hints,
    WhoKnowsMore, WhoKnowsMoreElement
)

# Base JSON Upload Mixin
class JsonUploadMixin:
    """Mixin to handle JSON file uploads and database insertion."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-json/", self.admin_site.admin_view(self.upload_json), name=f"upload-json-{self.model._meta.model_name}"),
            path("confirm-insert/", self.admin_site.admin_view(self.confirm_insert), name=f"confirm-insert-{self.model._meta.model_name}"),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        """Handles JSON file upload and stores data in session."""
        if request.method == "POST" and request.FILES.get("json_file"):
            json_file = request.FILES["json_file"]
            file_name = json_file.name.rsplit(".", 1)[0]  # Extract file name without extension
            file_path = f"temp/{json_file.name}"

            path = default_storage.save(file_path, json_file)
            try:
                with default_storage.open(path, "r") as file:
                    data = json.load(file)
                request.session["json_data"] = data
                request.session["json_file_name"] = file_name
                messages.success(request, "File uploaded successfully. Review the data below.")
            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON file format.")
            
            return redirect("..")

        return redirect("..")

    def confirm_insert(self, request):
        """Processes and inserts uploaded JSON data into the database."""
        data = request.session.pop("json_data", [])
        file_name = request.session.pop("json_file_name", "uploaded_json")

        if not data:
            messages.error(request, "No data available to insert.")
            return redirect("..")

        User = get_user_model()
        default_user = User.objects.filter(pk=1).first()

        # Create a category for the uploaded dataset
        new_category, _ = Category.objects.get_or_create(
            name_de=file_name,
            game_type=GameType.objects.get(pk=3),
            defaults={"description_de": "Uploaded via JSON", "created_on": now(), "created_by": default_user}
        )

        self.process_data(data, new_category, default_user)
        messages.success(request, f"{self.model._meta.verbose_name_plural.capitalize()} data successfully inserted.")
        return redirect("..")

    def process_data(self, data, category, default_user):
        """Must be overridden in child classes to handle model-specific insertions."""
        raise NotImplementedError


# Registering simple models
for model in [Tag, GameType, Category, Sound, Image, Question]:
    @admin.register(model)
    class DefaultAdmin(admin.ModelAdmin):
        list_display = ['name_de'] if hasattr(model, 'name_de') else ['solution']


# HintAdmin with JSON upload
@admin.register(Hints)
class HintAdmin(admin.ModelAdmin, JsonUploadMixin):
    change_list_template = "admin/populate_db.html"
    list_display = ['solution']

    def process_data(self, data, category, default_user):
        """Inserts Hints data from JSON."""
        for entry in data:
            fields = entry["fields"]
            created_by = User.objects.filter(pk=fields.get("created_by", 1)).first() or default_user
            created_on = parse_datetime(fields["created_on"]) if "created_on" in fields else now()

            Hints.objects.create(
                category=category,
                private_new=fields.get("private_new", False),
                explicit=fields.get("explicit", False),
                solution=fields["solution"],
                difficulty=fields["difficulty"],
                created_on=created_on,
                created_by=created_by,
                **{f"hint{i}": fields.get(f"hint{i}", "") for i in range(1, 11)}
            )


# WhoKnowsMore Admin
class WhoKnowsMoreElementInline(admin.TabularInline):
    model = WhoKnowsMoreElement
    extra = 2


@admin.register(WhoKnowsMore)
class WhoKnowsMoreAdmin(admin.ModelAdmin, JsonUploadMixin):
    list_display = ['category', 'solution']
    inlines = [WhoKnowsMoreElementInline]
    change_list_template = "admin/whoknowsmore_changelist.html"

    def process_data(self, data, category, default_user):
        """Inserts WhoKnowsMore data from JSON."""
        for entry in data:
            wkm_instance = WhoKnowsMore.objects.create(
                category=category,
                difficulty=5,
                solution=entry["solution"],
                created_by=default_user
            )

            WhoKnowsMoreElement.objects.bulk_create([
                WhoKnowsMoreElement(category_element=wkm_instance, answer=ans["answer"], count_id=ans["count_id"])
                for ans in entry["answers"]
            ])
