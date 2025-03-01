from django.shortcuts import render
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
from gameFiles.filters import ProfileFilter, ImageFilter, SoundFilter, QuestionFilter, CategoryFilter, HintFilter, \
    WhoKnowsMoreFilter
from gameFiles.models import Category, Image, Sound, Question, Hints, WhoKnowsMore
from gameFiles.views import WhoKnowsMoreSerializer


@login_required
def profile_view(request, per_page=10):
    context = {'profile_filter': ImageFilter(prefix="profile"),
               'images_table': create_profile_table(request, "images_", per_page),
               'sounds_table': create_profile_table(request, "sounds_", per_page),
               'questions_table': create_profile_table(request, "questions_", per_page),
               'hints_table': create_profile_table(request, "hints_", per_page),
               'whoknowsmore_table': create_profile_table(request, "whoknowsmore_", per_page),
               'categories_table': create_profile_table(request, "categories_", per_page)}
    return render(request, 'profile.html', context)


def get_profile_table(request, per_page):
    active_table = request.GET.get("active_table")
    if active_table in ["images_", "sounds_", "questions_", "categories_", "hints_", "whoknowsmore_"]:
        data = {
            "active_table": active_table,
            "html": render_to_string('profile_table_view.html', {'request': request,
                                                                 'table': create_profile_table(request, active_table,
                                                                                               per_page)})
        }
        return JsonResponse(data)
    return JsonResponse({"active_table": "error", "msg": "Invalid table name"})


def set_profile_filter(request, per_page):
    context = {'images_table': render_to_string('profile_table_view.html', {'request': request,
                                                                            'table': create_profile_table(request,
                                                                                                          "images_",
                                                                                                          per_page)}),
               'sounds_table': render_to_string('profile_table_view.html', {'request': request,
                                                                            'table': create_profile_table(request,
                                                                                                          "sounds_",
                                                                                                          per_page)}),
               'questions_table': render_to_string('profile_table_view.html', {'request': request,
                                                                               'table': create_profile_table(request,
                                                                                                             "questions_",
                                                                                                             per_page)}),
               'hints_table': render_to_string('profile_table_view.html', {'request': request,
                                                                           'table': create_profile_table(request,
                                                                                                         "hints_",
                                                                                                         per_page)}),
               'whoknowsmore_table': render_to_string('profile_table_view.html', {'request': request,
                                                                                  'table': create_profile_table(request,
                                                                                                                "whoknowsmore_",
                                                                                                                per_page)}),
               'categories_table': render_to_string('profile_table_view.html', {'request': request,
                                                                                'table': create_profile_table(request,
                                                                                                              "categories_",
                                                                                                              per_page)})}
    return JsonResponse(context)


def create_profile_table(request, table_name, per_page):
    user = request.user
    if table_name == "images_":
        qs_created_by_current_user = Image.objects.filter(created_by=user)
        qs_private = Image.objects.filter(category__private=False, private_new=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = ImageFilter(request.GET, elements, prefix="profile")
        table = ImageTable(filter_obj.qs, prefix="images_")
    elif table_name == "sounds_":
        qs_created_by_current_user = Sound.objects.filter(created_by=user)
        qs_private = Sound.objects.filter(category__private=False, private_new=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = SoundFilter(request.GET, elements, prefix="profile")
        table = SoundTable(filter_obj.qs, prefix="sounds_")
    elif table_name == "questions_":
        qs_created_by_current_user = Question.objects.filter(created_by=user)
        qs_private = Question.objects.filter(category__private=False, private_new=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = QuestionFilter(request.GET, elements, prefix="profile")
        table = QuestionTable(filter_obj.qs, prefix="questions_")
    elif table_name == "hints_":
        qs_created_by_current_user = Hints.objects.filter(created_by=user)
        qs_private = Hints.objects.filter(category__private=False, private_new=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = HintFilter(request.GET, elements, prefix="profile")
        table = HintTable(filter_obj.qs, prefix="hints_")
    elif table_name == "whoknowsmore_":
        qs_created_by_current_user = WhoKnowsMore.objects.filter(created_by=user)
        qs_private = WhoKnowsMore.objects.filter(category__private=False, private_new=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = WhoKnowsMoreFilter(request.GET, elements, prefix="profile")
        table = WhoKnowsMoreTable(filter_obj.qs, prefix="whoknowsmore_")
    elif table_name == "categories_":
        qs_created_by_current_user = Category.objects.filter(created_by=user)
        qs_private = Category.objects.filter(private=False)
        elements = qs_created_by_current_user | qs_private
        filter_obj = CategoryFilter(request.GET, elements, prefix="profile")
        table = CategoryTable(filter_obj.qs, prefix="category_")

    table.per_page = int(per_page)
    RequestConfig(request, paginate={"per_page": int(per_page)}).configure(table)
    return table

class DownloadView(View):
    def get(self, request, active_table, element_string=None):
        download_all = element_string == "all"
        return self.download_elements(request, active_table, element_string if not download_all else None, download_all)

    def download_elements(self, request, active_table, element_string=None, download_all=False):
        print(element_string)
        print(active_table)
        zip_filename = "BuzzingaDownloads.zip"
        zip_buffer = BytesIO()
        user = request.user  # Get the current user from the request

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            if active_table in ["images_", "sounds_"]:
                ModelClass = Image if active_table == "images_" else Sound
                base_path = "Bilder" if active_table == "images_" else "Audio"

                if download_all:
                    qs_created_by_user = ModelClass.objects.filter(created_by=user)
                    qs_public = ModelClass.objects.filter(category__private=False, private_new=False)
                    elements = qs_created_by_user | qs_public
                else:
                    element_ids = element_string.split("+")
                    elements = ModelClass.objects.filter(id__in=element_ids)

                for i in elements:
                    file_name_split = i.image_file.name.split("/") if active_table == "images_" else i.sound_file.name.split("/")
                    if len(file_name_split) > 2 and len(file_name_split[2]) > 4:
                        zf.write(settings.UPLOAD_ROOT + "/" + i.image_file.name if active_table == "images_" else settings.UPLOAD_ROOT + "/" + i.sound_file.name,
                                 f"{base_path}/{file_name_split[1]}/{file_name_split[2]}")

            elif active_table in ["questions_", "hints_", "whoknowsmore_"]:
                ModelClass = {"questions_": Question, "hints_": Hints, "whoknowsmore_": WhoKnowsMore}[active_table]

                if download_all:
                    qs_created_by_user = ModelClass.objects.filter(created_by=user)
                    qs_public = ModelClass.objects.filter(category__private=False, private_new=False)
                    elements = qs_created_by_user | qs_public
                else:
                    element_ids = element_string.split("+") if element_string else []
                    if not element_ids:
                        print("No elements selected")
                        return HttpResponse("No elements selected", status=400)
                    elements = ModelClass.objects.filter(id__in=element_ids)

                categories = elements.values_list('category', flat=True).distinct()
                for c in categories:
                    category_elements = elements.filter(category=c)
                    category_name = Category.objects.get(id=c).name_de
                    
                    json_str = (
                        serializers.serialize('json', category_elements) 
                        if active_table != "whoknowsmore_" 
                        else json.dumps(WhoKnowsMoreSerializer(category_elements, many=True).data, ensure_ascii=False)
                    )
                    
                    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                        json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                        tmp_file.flush()
                        tmp_file.seek(0)
                        active_table = "who-knows-more" if active_table == "whoknowsmore_"
                        zf.write(tmp_file.name, f"{active_table}/{category_name}.json")

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response