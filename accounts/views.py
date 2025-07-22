from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views import View

from django_tables2.config import RequestConfig
from io import BytesIO
import zipfile
import json
import tempfile

from gameFiles.tables import SoundTable, ImageTable, QuestionTable, HintTable, CategoryTable, WhoKnowsMoreTable
from gameFiles.filters import ImageFilter, SoundFilter, QuestionFilter, CategoryFilter, HintFilter, \
    WhoKnowsMoreFilter
from gameFiles.models import Category, Image, Sound, Question, Hints, WhoKnowsMore
from gameFiles.views import WhoKnowsMoreSerializer

TABLE_MAPPING = {
    #"image": (Image, ImageFilter, ImageTable),
    #"sound": (Sound, SoundFilter, SoundTable),
    "question": (Question, QuestionFilter, QuestionTable),
    "hint": (Hints, HintFilter, HintTable),
    "whoknowsmore": (WhoKnowsMore, WhoKnowsMoreFilter, WhoKnowsMoreTable),
    "category": (Category, CategoryFilter, CategoryTable),
}

TABLE_NAMES = {
            "category": "Kategorien",
            #"image": "Bilder",
            #"sound": "Sounds",
            "question": "Fragen",
            "hint": "Hinweise",
            "whoknowsmore": "Wer weiß mehr?"
            }

@login_required
def profile_view(request, per_page=10):
    tables = {
        f"{table_name}_table": create_profile_table(request, table_name, per_page)
        for table_name in TABLE_NAMES
    }
    per_page_options = [10, 25, 50]
    context = {
        "profile_filter": ImageFilter(prefix="profile"),
        "tables": tables,
        "table_names": TABLE_NAMES,
        "per_page_options": per_page_options,
    }
    return render(request, "profile.html", context)

@login_required
def get_profile_table(request, per_page):
    if not request.user.is_authenticated:
        return JsonResponse({"active_table": "error", "msg": "Not authenticated"}, status=403)
    
    active_table = request.GET.get("active_table")

    if active_table not in TABLE_NAMES:
        return JsonResponse({"active_table": "error", "msg": "Invalid table name"})

    # Generate table based on active tab
    table_html = render_to_string(
        "profile_table_view.html",
        {
            "request": request,
            "table": create_profile_table(request, active_table, per_page)
        },
    )

    return JsonResponse({"active_table": f"{active_table}_table", "html": table_html})


def set_profile_filter(request, per_page):
    data = {
        f"{table_name}_table": render_to_string(
            "profile_table_view.html",
            {"request": request, "table": create_profile_table(request, table_name, per_page)},
        )
        for table_name in TABLE_NAMES
    }
    return JsonResponse(data)


def create_profile_table(request, table_name, per_page): # Ensure this maps correctly
    user = request.user
    ModelClass, FilterClass, TableClass = TABLE_MAPPING[table_name]

    qs_created_by_user = ModelClass.objects.filter(created_by=user)
    qs_public = ModelClass.objects.filter(category__private=False, private_new=False) if table_name != "category" else ModelClass.objects.filter(private=False)

    # Custom permission: 'accounts.can_view_public_elements'
    if user.has_perm("accounts.can_view_public_elements"):
        elements = qs_created_by_user | qs_public
    else:
        elements = qs_created_by_user

    filter_obj = FilterClass(request.GET, queryset=elements, prefix="profile")
    table = TableClass(filter_obj.qs, prefix=table_name)
    RequestConfig(request, paginate={"per_page": int(per_page)}).configure(table)

    return table

class DownloadView(View):
    def get(self, request, active_table, element_string=None):
        return self.download_elements(request, active_table, element_string)

    def download_elements(self, request, active_table, element_string):
        if active_table not in TABLE_NAMES:
            return HttpResponse("Invalid table name", status=400)

        zip_buffer = BytesIO()
        zip_filename = "BuzzingaDownloads.zip"
        user = request.user
        ModelClass = TABLE_MAPPING[active_table][0]

        download_all = element_string == "all"
        elements = ModelClass.objects.filter(created_by=user) | ModelClass.objects.filter(category__private=False, private_new=False) if download_all else ModelClass.objects.filter(id__in=element_string.split("+"))

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            if active_table in ["images_", "sounds_"]:
                base_path = "Bilder" if active_table == "images_" else "Audio"
                file_attr = "image_file" if active_table == "images_" else "sound_file"

                for elem in elements:
                    file_path = getattr(elem, file_attr).name
                    file_parts = file_path.split("/")
                    if len(file_parts) > 2 and len(file_parts[2]) > 4:
                        zf.write(settings.UPLOAD_ROOT + "/" + file_path, f"{base_path}/{file_parts[1]}/{file_parts[2]}")

            else:  # For questions, hints, whoknowsmore
                categories = elements.values_list("category", flat=True).distinct()
                for cat_id in categories:
                    category_name = get_object_or_404(Category, id=cat_id).name_de
                    category_elements = elements.filter(category=cat_id)

                    json_data = (
                        json.dumps(WhoKnowsMoreSerializer(category_elements, many=True).data, ensure_ascii=False)
                        if active_table == "whoknowsmore"
                        else json.dumps(json.loads(serializers.serialize("json", category_elements)), indent=6, ensure_ascii=False)
                    )

                    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                        tmp_file.write(json_data)
                        tmp_file.flush()
                        table_name = "who-knows-more" if active_table == "whoknowsmore" else active_table
                        zf.write(tmp_file.name, f"{table_name}/{category_name}.json")

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f"attachment; filename={zip_filename}"
        return response