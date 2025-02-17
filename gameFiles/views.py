from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, FormView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile

from .models import GameType, Category, Image, Sound, Question, Tag, Hints, WhoKnowsMore, WhoKnowsMoreElement
from .forms import CategoryForm, ImageForm, ImageEditForm, SoundForm, QuestionForm, WhoKnowsMoreForm, \
    WhoKnowsMoreElementFormSet, WhoKnowsMoreElementFormSetUpdate, ImageDownloadForm, SoundDownloadForm, \
    QuestionDownloadForm, HintForm, HintDownloadForm, WhoKnowsMoreDownloadForm

from dal import autocomplete
from io import BytesIO
import zipfile
from random import sample
import datetime
import tempfile
import json
from PIL import ImageFont, ImageDraw
from PIL import Image as PILImage
from rest_framework import serializers as srlz
from rest_framework.renderers import JSONRenderer


def myFunc(e):
    return e['latest_create_date']


def home(request):
    categories = Category.objects.filter(private=False).order_by('-created_on')
    newest_categories = [c for c in categories if c.amount_files() > 0]
    newest_categories = newest_categories[0:4]
    latest_create_dates = []
    for c in categories:
        latest_create_dates.append(c.latest_elements())
    latest_create_dates.sort(key=lambda x: x['latest_create_date'], reverse=True)
    return render(request, 'home.html',
                  {'newest_categories': newest_categories, 'latest_create_dates': latest_create_dates[0:4]})


class GameTypeView(ListView):
    queryset = GameType.objects.all()
    template_name = "game_type_list.html"

    def get_queryset(self):
        self.qs = super(GameTypeView, self).get_queryset().all()
        return self.qs

    def get_context_data(self):
        context = super(GameTypeView, self).get_context_data()
        context['game_types'] = self.qs
        return context


class CategoryView(ListView):
    queryset = Category.objects.all()
    template_name = "category_list.html"

    def get_queryset(self):
        self.qs = super(CategoryView, self).get_queryset().filter(game_type=self.kwargs['game_type'], private=False)
        return self.qs

    def get_context_data(self):
        context = super(CategoryView, self).get_context_data()
        context['categories'] = self.qs
        context['game_type'] = get_object_or_404(GameType, pk=str(self.kwargs['game_type']))
        return context


def category_detail(request, game_type, id=id):
    category = get_object_or_404(Category, id=id)
    tags = []
    for t in category.tags_used():
        tags.append((t.name_de, t.amount_elements_with_tag(category=category)))
    sorted_tags = sorted(tags, key=lambda x: x[1])
    sorted_tags = sorted_tags[::-1]

    if game_type == 2:
        category_elements = Sound.objects.filter(category=category, private_new=False)
    elif game_type == 1:
        category_elements = Image.objects.filter(category=category, private_new=False)
    elif game_type == 4:
        category_elements = Question.objects.filter(category=category, private_new=False)
    elif game_type == 3:
        category_elements = Hints.objects.filter(category=category, private_new=False)
    else:
        category_elements = WhoKnowsMore.objects.filter(category=category, private_new=False)
    difficulty_count = {}
    for e in category_elements.all():
        if e.difficulty not in difficulty_count.keys():
            difficulty_count[e.difficulty] = 1
        else:
            difficulty_count[e.difficulty] += 1
    return render(request, 'category_detail.html',
                  {'game_type': game_type, 'category': category, 'tags': sorted_tags[:5],
                   'labels': list(difficulty_count.keys()), 'data': list(difficulty_count.values())})


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    def form_valid(self, form):
        form.instance.created_on = datetime.datetime.now()
        form.instance.created_by = self.request.user
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class CategoryEditView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class ImageEditView(LoginRequiredMixin, UpdateView):
    model = Image
    form_class = ImageEditForm
    template_name = 'image-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class SoundEditView(LoginRequiredMixin, UpdateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class QuestionEditView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class HintEditView(LoginRequiredMixin, UpdateView):
    model = Hints
    form_class = HintForm
    template_name = 'hint-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class WhoKnowsMoreEditView(LoginRequiredMixin, UpdateView):
    model = WhoKnowsMore
    form_class = WhoKnowsMoreForm
    template_name = 'who-knows-more-edit.html'
    object = None

    def get_object(self, queryset=None):
        self.object = super(WhoKnowsMoreEditView, self).get_object()
        return self.object

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = WhoKnowsMoreElementFormSetUpdate(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=WhoKnowsMoreForm(instance=self.object),
                                  formset=formset,
                                  )
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = WhoKnowsMoreForm(data=self.request.POST, instance=self.object)
        formset = WhoKnowsMoreElementFormSetUpdate(data=self.request.POST,
                                                   instance=self.object)
        print(formset.errors)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.category_element = self.object
            instance.count_id = len(WhoKnowsMoreElement.objects.filter(category_element=self.object)) + 1
            instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Image

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SoundDeleteView(LoginRequiredMixin, DeleteView):
    model = Sound

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class HintDeleteView(LoginRequiredMixin, DeleteView):
    model = Hints

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class WhoKnowsMoreDeleteView(LoginRequiredMixin, DeleteView):
    model = WhoKnowsMore

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ParentCreateView(CreateView):
    def form_valid(self, form):
        form.instance.created_on = datetime.datetime.now()
        form.instance.created_by = self.request.user
        tags = form.cleaned_data["tags"]
        self.object = form.save()
        self.object.tags.add(*tags)
        return super().form_valid(form)


class ImageCreateView(LoginRequiredMixin, ParentCreateView):
    model = Image
    form_class = ImageForm
    template_name = 'image-edit.html'

    def form_valid(self, form):
        form.instance.created_on = datetime.datetime.now()
        form.instance.created_by = self.request.user
        tags = form.cleaned_data["tags"]
        img = form.instance.image_file
        file_name = form.instance.solution
        img = PILImage.open(img)
        width, height = img.size
        font_size = int(min(width, height) / 50)
        font = ImageFont.truetype("Montserrat-Regular.ttf", font_size)
        if form.instance.file_changed:
            text = "by " + form.instance.author + " (modified from original) licensed under " + form.instance.license
        else:
            text = "by " + form.instance.author + " licensed under " + form.instance.license
        if form.instance.license == "CC0":
            text_license = "https://creativecommons.org/publicdomain/zero/1.0/deed.de"
        elif form.instance.license == "CC BY":
            text_license = "https://creativecommons.org/licenses/by/4.0/deed.de"
        else:
            text_license = "https://creativecommons.org/licenses/by-sa/3.0/de/"
        text_width = font.getsize(text)[0]
        text_height = font.getsize(text)[1]
        text_license_width = font.getsize(text_license)[0]
        text_license_height = font.getsize(text_license)[1]
        img_edit = ImageDraw.Draw(img)
        img_edit.text((width - text_width - 5, height - text_height - text_license_height - 10), text, (222, 222, 222),
                      font=font)
        img_edit.text((width - text_license_width - 5, height - text_license_height - 5), text_license, (222, 222, 222),
                      font=font)
        image_io = BytesIO()
        img.save(image_io, format=img.format)
        image_name = '{}.{}'.format(file_name, img.format)
        img = ContentFile(image_io.getvalue(), image_name)
        form.instance.image_file = img
        self.object = form.save()
        self.object.tags.add(*tags)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class SoundCreateView(LoginRequiredMixin, ParentCreateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class QuestionCreateView(LoginRequiredMixin, ParentCreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class HintCreateView(LoginRequiredMixin, ParentCreateView):
    model = Hints
    form_class = HintForm
    template_name = 'hint-edit.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class WhoKnowsMoreCreateView(LoginRequiredMixin, ParentCreateView):
    model = WhoKnowsMore
    form_class = WhoKnowsMoreForm
    template_name = 'who-knows-more-edit.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = WhoKnowsMoreElementFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  formset=formset,
                                  )
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = WhoKnowsMoreElementFormSet(self.request.POST)
        print(formset.errors)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        formset = formset
        if formset.is_valid and form.is_valid():
            self.object = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.category_element = self.object
                instance.count_id = len(WhoKnowsMoreElement.objects.filter(category_element=self.object)) + 1
                instance.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_success_url(self):
        return reverse('account:profile', kwargs={'per_page': 10})


class ImageDownloadView(LoginRequiredMixin, FormView):
    template_name = 'sound-download.html'
    form_class = ImageDownloadForm

    def get_success_url(self, **kwargs):
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type = category.game_type.id
        return reverse('gamefiles:category_detail', kwargs={'id': category.id, 'game_type': game_type})

    def get_context_data(self, **kwargs):
        ctx = super(ImageDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type_id = category.game_type.id
        ctx['game_type_id'] = game_type_id
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        current_user = self.request.user
        tags = form.cleaned_data["tags"]
        created_by = form.cleaned_data["created_by"]
        if not created_by:
            created_by = User.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"]) - i for i in range(
            int(form.cleaned_data["max_difficulty"]) - int(form.cleaned_data["min_difficulty"]) + 1)]
        if not tags:
            images = Image.objects.filter(category=form.cleaned_data["category"], created_by__in=created_by,
                                          private_new=False, difficulty__in=difficulty_range).distinct()
        else:
            images = Image.objects.filter(category=form.cleaned_data["category"], tags__in=tags,
                                          created_by__in=created_by,
                                          private_new=False, difficulty__in=difficulty_range).distinct()
        if form.cleaned_data["explicit"]:
            images.filter(explicit=False)
        if form.cleaned_data["min_upload_date"]:
            images.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        if form.cleaned_data["max_upload_date"]:
            images.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        if not form.cleaned_data["private_new"]:
            private_images = Image.objects.filter(created_by=current_user, private_new=True).distinct()
            images = images | private_images
        images_ids = set(list(images.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(images_ids):
            random_ids = sample(images_ids, form.cleaned_data["amount"])
            images = images.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for i in images:
                image_name_split = i.image_file.name.split("/")
                if len(image_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + i.image_file.name,
                             "Bilder/" + image_name_split[1] + "/" + image_name_split[2])
                else:
                    continue
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class SoundDownloadView(LoginRequiredMixin, FormView):
    template_name = 'sound-download.html'
    form_class = SoundDownloadForm

    def get_success_url(self, **kwargs):
        return reverse('gamefiles:category_detail',
                       kwargs={'id': self.kwargs['category_id'], 'game_type': self.kwargs['game_type']})

    def get_context_data(self, **kwargs):
        ctx = super(SoundDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        current_user = self.request.user
        tags = form.cleaned_data["tags"]
        created_by = form.cleaned_data["created_by"]
        if not created_by:
            created_by = User.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"]) - i for i in range(
            int(form.cleaned_data["max_difficulty"]) - int(form.cleaned_data["min_difficulty"]) + 1)]
        if not tags:
            sounds = Sound.objects.filter(category=form.cleaned_data["category"], created_by__in=created_by,
                                          private_new=False, difficulty__in=difficulty_range).distinct()
        else:
            sounds = Sound.objects.filter(category=form.cleaned_data["category"], tags__in=tags,
                                          created_by__in=created_by, private_new=False,
                                          difficulty__in=difficulty_range).distinct()
        if form.cleaned_data["explicit"]:
            sounds.filter(explicit=False)
        if form.cleaned_data["min_upload_date"]:
            sounds.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        if form.cleaned_data["max_upload_date"]:
            sounds.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        if not form.cleaned_data["private_new"]:
            private_sounds = Sound.objects.filter(created_by=current_user, private_new=True).distinct()
            sounds = sounds | private_sounds
        sounds_ids = set(list(sounds.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(sounds_ids):
            random_ids = sample(sounds_ids, form.cleaned_data["amount"])
            sounds = sounds.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for s in sounds:
                sound_name_split = s.sound_file.name.split("/")
                if len(sound_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT + "/" + s.sound_file.name,
                             "Audio/" + sound_name_split[1] + "/" + sound_name_split[2])
                else:
                    continue
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class QuestionDownloadView(LoginRequiredMixin, FormView):
    template_name = 'sound-download.html'
    form_class = QuestionDownloadForm

    def get_success_url(self, **kwargs):
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type = category.game_type.id
        return reverse('gamefiles:category_detail', kwargs={'id': category.id, 'game_type': game_type})

    def get_context_data(self, **kwargs):
        ctx = super(QuestionDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type_id = category.game_type.id
        ctx['game_type_id'] = game_type_id
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        current_user = self.request.user
        tags = form.cleaned_data["tags"]
        created_by = form.cleaned_data["created_by"]
        if not created_by:
            created_by = User.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"]) - i for i in range(
            int(form.cleaned_data["max_difficulty"]) - int(form.cleaned_data["min_difficulty"]) + 1)]
        if not tags:
            questions = Question.objects.filter(category=form.cleaned_data["category"], created_by__in=created_by,
                                                private_new=False, difficulty__in=difficulty_range).distinct()
        else:
            questions = Question.objects.filter(category=form.cleaned_data["category"], tags__in=tags,
                                                created_by__in=created_by,
                                                private_new=False, difficulty__in=difficulty_range, ).distinct()
        if form.cleaned_data["explicit"]:
            questions.filter(explicit=False)
        if form.cleaned_data["min_upload_date"]:
            questions.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        if form.cleaned_data["max_upload_date"]:
            questions.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        if not form.cleaned_data["private_new"]:
            private_questions = Question.objects.filter(created_by=current_user, private_new=True).distinct()
            questions = questions | private_questions
        questions_ids = set(list(questions.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(questions_ids):
            random_ids = sample(questions_ids, form.cleaned_data["amount"])
            questions = questions.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        json_str = serializers.serialize('json',
                                         questions)  # , fields=('quiz_question', 'solution', 'option1', 'option2', 'option3'))
        tmp_file = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
        tmp_file.seek(0)
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            zf.write(tmp_file.name, "Questions/" + category_name + ".json")
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class HintDownloadView(LoginRequiredMixin, FormView):
    template_name = 'sound-download.html'
    form_class = HintDownloadForm

    def get_success_url(self, **kwargs):
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type = category.game_type.id
        return reverse('gamefiles:category_detail', kwargs={'id': category.id, 'game_type': game_type})

    def get_context_data(self, **kwargs):
        ctx = super(HintDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type_id = category.game_type.id
        ctx['game_type_id'] = game_type_id
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        current_user = self.request.user
        tags = form.cleaned_data["tags"]
        created_by = form.cleaned_data["created_by"]
        if not created_by:
            created_by = User.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"]) - i for i in range(
            int(form.cleaned_data["max_difficulty"]) - int(form.cleaned_data["min_difficulty"]) + 1)]
        if not tags:
            hints = Hints.objects.filter(category=form.cleaned_data["category"], created_by__in=created_by,
                                         private_new=False, difficulty__in=difficulty_range).distinct()
        else:
            hints = Hints.objects.filter(category=form.cleaned_data["category"], tags__in=tags,
                                         created_by__in=created_by,
                                         private_new=False, difficulty__in=difficulty_range, ).distinct()
        if form.cleaned_data["explicit"]:
            hints.filter(explicit=False)
        if form.cleaned_data["min_upload_date"]:
            hints.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        if form.cleaned_data["max_upload_date"]:
            hints.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        if not form.cleaned_data["private_new"]:
            private_hints = Hints.objects.filter(created_by=current_user, private_new=True).distinct()
            hints = hints | private_hints
        hints_ids = set(list(hints.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(hints_ids):
            random_ids = sample(hints_ids, form.cleaned_data["amount"])
            hints = hints.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        json_str = serializers.serialize('json', hints)
        tmp_file = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
        tmp_file.seek(0)
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            zf.write(tmp_file.name, "Hints/" + category_name + ".json")
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class WhoKnowsMoreElementSerializer(srlz.ModelSerializer):
    class Meta:
        model = WhoKnowsMoreElement
        fields = ('count_id', 'answer')


class WhoKnowsMoreSerializer(srlz.ModelSerializer):
    answers = WhoKnowsMoreElementSerializer(many=True)

    class Meta:
        model = WhoKnowsMore
        fields = ('id', 'solution', 'answers')


class WhoKnowsMoreDownloadView(LoginRequiredMixin, FormView):
    template_name = 'sound-download.html'
    form_class = WhoKnowsMoreDownloadForm

    def get_success_url(self, **kwargs):
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type = category.game_type.id
        return reverse('gamefiles:category_detail', kwargs={'id': category.id, 'game_type': game_type})

    def get_context_data(self, **kwargs):
        ctx = super(WhoKnowsMoreDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        category = Category.objects.get(pk=self.kwargs['category_id'])
        game_type_id = category.game_type.id
        ctx['game_type_id'] = game_type_id
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        current_user = self.request.user
        tags = form.cleaned_data["tags"]
        created_by = form.cleaned_data["created_by"]
        if not created_by:
            created_by = User.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"]) - i for i in range(
            int(form.cleaned_data["max_difficulty"]) - int(form.cleaned_data["min_difficulty"]) + 1)]
        if not tags:
            whoknowsmore = WhoKnowsMore.objects.filter(category=form.cleaned_data["category"], created_by__in=created_by,
                                         private_new=False, difficulty__in=difficulty_range).distinct()
        else:
            whoknowsmore = WhoKnowsMore.objects.filter(category=form.cleaned_data["category"], tags__in=tags,
                                         created_by__in=created_by,
                                         private_new=False, difficulty__in=difficulty_range, ).distinct()
        if form.cleaned_data["explicit"]:
            whoknowsmore.filter(explicit=False)
        if form.cleaned_data["min_upload_date"]:
            whoknowsmore.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        if form.cleaned_data["max_upload_date"]:
            whoknowsmore.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        if not form.cleaned_data["private_new"]:
            private_whoknowsmore = WhoKnowsMore.objects.filter(created_by=current_user, private_new=True).distinct()
            whoknowsmore = whoknowsmore | private_whoknowsmore
        whoknowsmore_ids = set(list(whoknowsmore.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(whoknowsmore_ids):
            random_ids = sample(whoknowsmore_ids, form.cleaned_data["amount"])
            whoknowsmore = whoknowsmore.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        serialized_whoknowsmore = WhoKnowsMoreSerializer(whoknowsmore, many=True).data
        json_str = JSONRenderer().render(serialized_whoknowsmore)
        tmp_file = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
        tmp_file.seek(0)
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            zf.write(tmp_file.name, "Wer weiß mehr?/" + category_name + ".json")
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


def solution(request, game_type, category_element):
    game_type = GameType.objects.get(id=game_type)
    if game_type.name_de == "Audio":
        solution = {"type": "Sound", "qs": Sound.objects.get(id=category_element)}
    elif game_type.name_de == "Bilder":
        solution = {"type": "Image", "qs": Image.objects.get(id=category_element)}
    elif game_type.name_de == "Multiple Choice":
        solution = {"type": "Multiple Choice", "qs": Question.objects.get(id=category_element)}
    elif game_type.name_de == "10 Hinweise":
        solution = {"type": "Hints", "qs": Hints.objects.get(id=category_element)}
    elif game_type.name_de == "Wer weiß mehr?":
        solution = {"type": "WhoKnowsMore", "qs": WhoKnowsMore.objects.get(id=category_element).show_solution()}
    return render(request, 'solution.html', {'solution': solution})


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs_created_by_current_user = Category.objects.filter(created_by=self.request.user)
        qs_private = Category.objects.filter(private=False)

        qs = qs_created_by_current_user | qs_private

        game_type = self.forwarded.get('game_type', None)

        if game_type:
            qs = qs.filter(game_type=game_type)

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs
