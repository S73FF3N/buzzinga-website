from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.generic import FormView
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from django.contrib.auth.decorators import login_required

from django_tables2.config import RequestConfig
from io import BytesIO
import zipfile
import json
import tempfile

from gameFiles.tables import ProfileTable, CategoryTable
from gameFiles.filters import ImageFilter, SoundFilter, QuestionFilter, CategoryFilter, HintFilter
from gameFiles.models import Category, Image, Sound, Question, Hints
from .forms import DownloadForm

@login_required
def profile_view(request, per_page=4):
    context = {}
    context['profile_filter'] = QuestionFilter(prefix="profile")
    context['images_table'] = create_profile_table(request, "images_", per_page)
    context['sounds_table'] = create_profile_table(request, "sounds_", per_page)
    context['questions_table'] = create_profile_table(request, "questions_", per_page)
    context['hints_table'] = create_profile_table(request, "hints_", per_page)
    context['categories_table'] = create_profile_table(request, "categories_", per_page)
    return render(request, 'profile.html', context)

def get_profile_table(request, per_page):

    active_table = request.GET.get("active_table")
    if active_table in ["images_", "sounds_", "questions_", "categories_", "hints_"]:
        data = {
            "active_table":active_table,
            "html":render_to_string('profile_table_view.html', {'request':request, 'table':create_profile_table(request, active_table, per_page)})
        }
        return JsonResponse(data)
    return JsonResponse({"active_table":"error","msg":_("Invalid table name")})

def set_profile_filter(request, per_page, active_table):

    context = {}
    context['images_table'] = render_to_string('profile_table_view.html', {'request':request, 'table':create_profile_table(request, "images_", per_page)})
    context['sounds_table'] = render_to_string('profile_table_view.html', {'request':request, 'table':create_profile_table(request, "sounds_", per_page)})
    context['questions_table'] = render_to_string('profile_table_view.html', {'request':request, 'table':create_profile_table(request, "questions_", per_page)})
    context['hints_table'] = render_to_string('profile_table_view.html', {'request': request,
                                                                              'table': create_profile_table(request,
                                                                                                            "hints_",
                                                                                                            per_page)})
    context['categories_table'] = render_to_string('profile_table_view.html', {'request': request, 'table': create_profile_table(request, "categories_", per_page)})

    return JsonResponse(context)

def create_profile_table(request, table_name, per_page):
    user = request.user
    if table_name == "images_":
        filter_obj = ImageFilter(request.GET, Image.objects.filter(created_by=user), prefix="profile")
        table = ProfileTable(filter_obj.qs, prefix=table_name)
    elif table_name == "sounds_":
        filter_obj = SoundFilter(request.GET, Sound.objects.filter(created_by=user), prefix="profile")
        table = ProfileTable(filter_obj.qs, prefix=table_name)
    elif table_name == "questions_":
        filter_obj = QuestionFilter(request.GET, Question.objects.filter(created_by=user), prefix="profile")
        table = ProfileTable(filter_obj.qs, prefix=table_name)
    elif table_name == "hints_":
        filter_obj = HintFilter(request.GET, Hints.objects.filter(created_by=user), prefix="profile")
        table = ProfileTable(filter_obj.qs, prefix=table_name)
    elif table_name == "categories_":
        filter_obj = CategoryFilter(request.GET, Category.objects.filter(created_by=user), prefix="profile")
        table = CategoryTable(filter_obj.qs, prefix=table_name)

    table.user_id = user.id
    table.per_page = int(per_page)
    RequestConfig(request, paginate={"per_page":int(per_page)}).configure(table)
    return table

def download_elements(self, active_table, element_string):
    zip_filename = "BuzzingaDownloads.zip"
    zip_buffer = BytesIO()
    element_ids = element_string.split("+")
    if active_table == "images_":
        elements = Image.objects.filter(id__in=element_ids)
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for i in elements:
                image_name_split = i.image_file.name.split("/")
                if len(image_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + i.image_file.name,
                             "Bilder/" + image_name_split[1] + "/" + image_name_split[2])
                else:
                    continue
    elif active_table == "sounds_":
        elements = Sound.objects.filter(id__in=element_ids)
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for i in elements:
                sound_name_split = i.sound_file.name.split("/")
                if len(sound_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + i.sound_file.name,
                             "Audio/" + sound_name_split[1] + "/" + sound_name_split[2])
                else:
                    continue
    elif active_table == "questions_":
        elements = Question.objects.filter(id__in=element_ids)
        categories = elements.values_list('category', flat=True).distinct()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for c in categories:
                category_elements = elements.filter(category=c)
                json_str = serializers.serialize('json', category_elements, fields=('quiz_question','solution', 'option1', 'option2', 'option3'))
                tmp_file = tempfile.NamedTemporaryFile(mode="w+")
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                category_name = Category.objects.get(id=c).name_de
                tmp_file.seek(0)
                zf.write(tmp_file.name, "Questions/" + category_name + ".json")
    elif active_table == "hints_":
        elements = Hints.objects.filter(id__in=element_ids)
        categories = elements.values_list('category', flat=True).distinct()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for c in categories:
                category_elements = elements.filter(category=c)
                json_str = serializers.serialize('json', category_elements, fields=('solution', 'hint1', 'hint2', 'hint3', 'hint4', 'hint5', 'hint6', 'hint7', 'hint8', 'hint9', 'hint10'))
                tmp_file = tempfile.NamedTemporaryFile(mode="w+")
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                category_name = Category.objects.get(id=c).name_de
                tmp_file.seek(0)
                zf.write(tmp_file.name, "Hints/" + category_name + ".json")
    zip_buffer.seek(0)
    resp = HttpResponse(zip_buffer, content_type="application/zip")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def download_all_elements(self, active_table):
    zip_filename = "BuzzingaDownloads.zip"
    zip_buffer = BytesIO()
    if active_table == "images_":
        elements = Image.objects.all()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for i in elements:
                image_name_split = i.image_file.name.split("/")
                if len(image_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + i.image_file.name,
                             "Bilder/" + image_name_split[1] + "/" + image_name_split[2])
                else:
                    continue
    elif active_table == "sounds_":
        elements = Sound.objects.all()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for i in elements:
                sound_name_split = i.sound_file.name.split("/")
                if len(sound_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + i.sound_file.name,
                             "Audio/" + sound_name_split[1] + "/" + sound_name_split[2])
                else:
                    continue
    elif active_table == "questions_":
        elements = Question.objects.all()
        categories = elements.values_list('category', flat=True).distinct()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for c in categories:
                category_elements = elements.filter(category=c)
                json_str = serializers.serialize('json', category_elements, fields=('quiz_question','solution', 'option1', 'option2', 'option3'))
                tmp_file = tempfile.NamedTemporaryFile(mode="w+")
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                category_name = Category.objects.get(id=c).name_de
                tmp_file.seek(0)
                zf.write(tmp_file.name, "Questions/" + category_name + ".json")
    elif active_table == "hints_":
        elements = Hints.objects.all()
        categories = elements.values_list('category', flat=True).distinct()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for c in categories:
                category_elements = elements.filter(category=c)
                json_str = serializers.serialize('json', category_elements, fields=('solution', 'hint1', 'hint2', 'hint3', 'hint4', 'hint5', 'hint6', 'hint7', 'hint8', 'hint9', 'hint10'))
                tmp_file = tempfile.NamedTemporaryFile(mode="w+")
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                category_name = Category.objects.get(id=c).name_de
                tmp_file.seek(0)
                zf.write(tmp_file.name, "Hints/" + category_name + ".json")
    zip_buffer.seek(0)
    resp = HttpResponse(zip_buffer, content_type="application/zip")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

