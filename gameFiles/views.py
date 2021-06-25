from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, FormView, CreateView, UpdateView
from django.conf import settings
from django.urls import reverse

from .models import GameType, Category, CategoryElement, Image, Sound, Question, Tag
from .forms import CategoryForm, ImageForm, SoundForm, QuestionForm, ImageDownloadForm, SoundDownloadForm

from dal import autocomplete
from io import BytesIO
import zipfile
from random import sample
import datetime

def home(request):
    return render(request, 'home.html')

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
    sorted_tags = sorted(tags, key=lambda x:x[1])
    sorted_tags = sorted_tags[::-1]

    category_elements = CategoryElement.objects.filter(category=category, private_new=False)
    difficulty_count = {}
    for e in category_elements.all():
        if e.difficulty not in difficulty_count.keys():
            difficulty_count[e.difficulty] = 1
        else:
            difficulty_count[e.difficulty] += 1
    return render(request, 'category_detail.html', {'game_type': game_type, 'category': category, 'tags': sorted_tags[:5], 'labels': list(difficulty_count.keys()), 'data': list(difficulty_count.values())})

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    #def get_initial(self):
     #   return {
      #      'game_type': self.kwargs['game_type_id'],
       # }

    #def get_context_data(self, **kwargs):
     #   ctx = super(CategoryCreateView, self).get_context_data(**kwargs)
      #  ctx['game_type_id'] = self.kwargs['game_type_id']
       # return ctx

    #def form_invalid(self, form):
     #   return render(self.request, 'success.html', {'element': "Test"})

    def form_valid(self, form):
        form.instance.created_on = datetime.datetime.now()
        self.object = form.save()
        return super().form_valid(form)#render(self.request, 'success.html', {'element': self.object})

class CategoryEditView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    def get_success_url(self):
        return reverse('account:profile')

class ImageEditView(UpdateView):
    model = Image
    form_class = ImageForm
    template_name = 'image-edit.html'

    def get_success_url(self):
        return reverse('account:profile')

class SoundEditView(UpdateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'

    def get_success_url(self):
        return reverse('account:profile')

class QuestionEditView(UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'

    def get_success_url(self):
        return reverse('account:profile')

class ParentCreateView(CreateView):
    #def get_initial(self):
     #   return {
      #      'category': self.kwargs['category_id'],
       # }

    def form_valid(self, form):
        form.instance.created_on = datetime.datetime.now()
        tags = form.cleaned_data["tags"]
        self.object = form.save()
        self.object.tags.add(*tags)
        return super().form_valid(form)#render(self.request, 'success.html', {'element': self.object})

class ImageCreateView(ParentCreateView):
    model = Image
    form_class = ImageForm
    template_name = 'image-edit.html'#'image_create_form.html'

    def get_success_url(self):
        return reverse('account:profile')
    #def get_context_data(self, **kwargs):
     #   ctx = super(ImageCreateView, self).get_context_data(**kwargs)
      #  ctx['category_id'] = self.kwargs['category_id']
       # return ctx

class SoundCreateView(ParentCreateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'

    def get_success_url(self):
        return reverse('account:profile')
    #def get_context_data(self, **kwargs):
     #   ctx = super(SoundCreateView, self).get_context_data(**kwargs)
      #  ctx['category_id'] = self.kwargs['category_id']
       # return ctx

class QuestionCreateView(ParentCreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'

    def get_success_url(self):
        return reverse('account:profile')
    #def get_context_data(self, **kwargs):
     #   ctx = super(QuestionCreateView, self).get_context_data(**kwargs)
      #  ctx['category_id'] = self.kwargs['category_id']
       # return ctx

class ImageDownloadView(FormView):
    template_name = 'image-download.html'
    form_class = ImageDownloadForm

    def get_context_data(self, **kwargs):
        ctx = super(ImageDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        tags = form.cleaned_data["tags"]
        if not tags:
            tags = Tag.objects.all()
        difficulty_range = [int(form.cleaned_data["max_difficulty"])-i for i in range(int(form.cleaned_data["max_difficulty"])-int(form.cleaned_data["min_difficulty"])+1)]
        if form.cleaned_data["explicit"] == True:
            images = Image.objects.filter(category=form.cleaned_data["category"], tags__in=tags, difficulty__in=difficulty_range, explicit=False)
        else:
            images = Image.objects.filter(category=form.cleaned_data["category"], tags__in=tags, difficulty__in=difficulty_range)
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
                    zf.write(settings.MEDIA_ROOT+"/"+i.image_file.name, "Bilder/"+image_name_split[1]+"/"+image_name_split[2])
                else:
                    continue
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp

class SoundDownloadView(FormView):
    template_name = 'sound-download.html'
    form_class = SoundDownloadForm

    def get_context_data(self, **kwargs):
        ctx = super(SoundDownloadView, self).get_context_data(**kwargs)
        ctx['category_id'] = self.kwargs['category_id']
        return ctx

    def get_initial(self):
        return {
            'category': self.kwargs['category_id'],
        }

    def form_valid(self, form):
        tags = form.cleaned_data["tags"]
        if not tags:
            tags = Tag.objects.all()
        print(tags)
        difficulty_range = [int(form.cleaned_data["max_difficulty"])-i for i in range(int(form.cleaned_data["max_difficulty"])-int(form.cleaned_data["min_difficulty"])+1)]
        if form.cleaned_data["explicit"] == True:
            sounds = Sound.objects.filter(category=form.cleaned_data["category"], tags__in=tags, difficulty__in=difficulty_range, explicit=False)
        else:
            sounds = Sound.objects.filter(category=form.cleaned_data["category"], tags__in=tags, difficulty__in=difficulty_range)
        print(Sound.objects.filter(category=form.cleaned_data['category']))
        sounds_ids = set(list(sounds.values_list('id', flat=True)))
        if form.cleaned_data["amount"] < len(sounds_ids):
            random_ids = sample(sounds_ids, form.cleaned_data["amount"])
            sounds = sounds.filter(id__in=random_ids)
        category_name = Category.objects.get(pk=form.cleaned_data["category"].pk).name_de
        zip_filename = "%s.zip" % category_name
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
            for s in sounds:
                print(s)
                sound_name_split = s.sound_file.name.split("/")
                if len(sound_name_split[2]) > 4:
                    zf.write(settings.MEDIA_ROOT+"/"+s.sound_file.name, "Audio/"+sound_name_split[1]+"/"+sound_name_split[2])
                else:
                    continue
        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type="application/zip")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp

class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs

class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Category.objects.all()

        game_type = self.forwarded.get('game_type', None)

        if game_type:
            qs = qs.filter(game_type=game_type)

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs
