import json

from django.shortcuts import redirect
from django.urls import path
from django.contrib import admin
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .models import Tag, GameType, Category, Sound, Image, Question, Hints, WhoKnowsMore, WhoKnowsMoreElement

class TagAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(Tag, TagAdmin)

class GameTypeAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(GameType, GameTypeAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_de']
admin.site.register(Category, CategoryAdmin)

class SoundAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Sound, SoundAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Image, ImageAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['solution']
admin.site.register(Question, QuestionAdmin)

class HintAdmin(admin.ModelAdmin):
    change_list_template = "admin/populate_db.html"
    list_display = ['solution']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-json/", self.admin_site.admin_view(self.upload_json), name="upload-json"),
            path("confirm-insert/", self.admin_site.admin_view(self.confirm_insert), name="confirm-insert"),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        """Handle JSON file upload and show a preview."""
        if request.method == "POST" and request.FILES.get("json_file"):
            json_file = request.FILES["json_file"]
            file_name = json_file.name.rsplit(".", 1)[0]  # Extract file name without extension
            file_path = f"temp/{json_file.name}"

            # Save file temporarily
            path = default_storage.save(file_path, json_file)

            # Read the JSON file
            with default_storage.open(path, "r") as file:
                try:
                    data = json.load(file)
                    request.session["json_data"] = data  # Store data in session
                    request.session["json_file_name"] = file_name  # Store file name
                    messages.success(request, "File uploaded successfully. Review the data below.")
                except json.JSONDecodeError:
                    messages.error(request, "Invalid JSON file format.")
                    return redirect("..")

            return redirect("..")

        return redirect("..")


    def confirm_insert(self, request):
        """Confirm data insertion into the database."""
        data = request.session.get("json_data", [])
        file_name = request.session.get("json_file_name", "uploaded_json")  # Default name if missing

        if not data:
            messages.error(request, "No data available to insert.")
            return redirect("..")

        User = get_user_model()

        # Ensure created_by (default to ID=1)
        default_user = User.objects.filter(pk=1).first()

        # Create a new category (ignoring category from JSON)
        new_category = Category.objects.create(
            name_de=file_name,
            game_type=GameType.objects.get(pk=3),
            description_de="Uploaded via JSON",
            created_on=now(),
            created_by=default_user
        )

        for entry in data:
            fields = entry["fields"]

            # Ensure created_by is valid, else use default (ID=1)
            created_by = User.objects.filter(pk=fields.get("created_by", 1)).first() or default_user

            # Convert DateTime field
            created_on = parse_datetime(fields["created_on"]) if "created_on" in fields else now()

            # Create Hints object (ignoring Many-to-Many field 'tags' and JSON 'category')
            Hints.objects.create(
                category=new_category,  # Use newly created category
                private_new=fields.get("private_new", False),
                explicit=fields.get("explicit", False),
                solution=fields["solution"],
                difficulty=fields["difficulty"],
                created_on=created_on,
                created_by=created_by,
                hint1=fields["hint1"],
                hint2=fields["hint2"],
                hint3=fields["hint3"],
                hint4=fields["hint4"],
                hint5=fields["hint5"],
                hint6=fields["hint6"],
                hint7=fields["hint7"],
                hint8=fields["hint8"],
                hint9=fields["hint9"],
                hint10=fields["hint10"],
            )

        # Clear session after inserting
        del request.session["json_data"]
        del request.session["json_file_name"]
        messages.success(request, "Data successfully inserted into the database.")
        return redirect("..")

admin.site.register(Hints, HintAdmin)


def confirm_insert_whoknowsmore(self, request):
    """Confirm data insertion for WhoKnowsMore and related answers."""
    data = request.session.get("json_data", [])
    file_name = request.session.get("json_file_name", "uploaded_json")  # Default name if missing

    if not data:
        messages.error(request, "No data available to insert.")
        return redirect("..")

    User = get_user_model()
    default_user = User.objects.filter(pk=1).first()

    # Create a new category for this upload
    new_category = Category.objects.create(
        name_de=file_name,
        game_type=GameType.objects.get(pk=3),
        description_de="Uploaded via JSON",
        created_on=now(),
        created_by=default_user
    )

    for entry in data:
        solution = entry["solution"]

        # Create WhoKnowsMore object
        wkm_instance = WhoKnowsMore.objects.create(
            category=new_category,
            solution=solution,
            created_by=default_user
        )

        # Create WhoKnowsMoreElement objects (answers)
        for answer_data in entry["answers"]:
            WhoKnowsMoreElement.objects.create(
                category_element=wkm_instance,
                answer=answer_data["answer"],
                count_id=answer_data["count_id"]
            )

    # Clear session after inserting
    del request.session["json_data"]
    del request.session["json_file_name"]
    messages.success(request, "WhoKnowsMore data successfully inserted into the database.")
    return redirect("..")

class WhoKnowsMoreElementInline(admin.TabularInline):
    model = WhoKnowsMoreElement

class WhoKnowsMoreAdmin(admin.ModelAdmin):
    list_display = ['solution']
    inlines = [
        WhoKnowsMoreElementInline,
    ]
    change_list_template = "admin/whoknowsmore_changelist.html"  # Custom admin page

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload_json/", self.upload_json, name="upload_json_whoknowsmore"),
            path("confirm_insert/", self.confirm_insert_whoknowsmore, name="confirm_insert_whoknowsmore"),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        """Handle JSON file upload and show a preview."""
        if request.method == "POST" and request.FILES.get("json_file"):
            json_file = request.FILES["json_file"]
            file_name = json_file.name.rsplit(".", 1)[0]  # Extract file name without extension
            file_data = json_file.read().decode("utf-8")

            try:
                data = json.loads(file_data)
                request.session["json_data"] = data  # Store data in session
                request.session["json_file_name"] = file_name  # Store file name
                messages.success(request, "File uploaded successfully. Review the data below.")
            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON file format.")
                return redirect("..")

            return redirect("..")

        return redirect("..")

admin.site.register(WhoKnowsMore, WhoKnowsMoreAdmin)

class WhoKnowsMoreElementAdmin(admin.ModelAdmin):
    list_display = ['answer']
admin.site.register(WhoKnowsMoreElement, WhoKnowsMoreElementAdmin)

