from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, FormView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db.models import Count, OuterRef, Subquery, Q, IntegerField
from django.db.models.expressions import Value
from django.db.models.functions import Coalesce

from .models import GameType, Category, Image, Sound, Question, Hints, WhoKnowsMore, WhoKnowsMoreElement, QuizGameResult
from .forms import CategoryForm, ImageForm, ImageEditForm, SoundForm, QuestionForm, WhoKnowsMoreForm, WhoKnowsMoreElementFormSet, WhoKnowsMoreElementFormSetUpdate, ImageDownloadForm, SoundDownloadForm, QuestionDownloadForm, HintForm, HintDownloadForm, WhoKnowsMoreDownloadForm, SolutionForm, QuizGameResultForm, RandomTeamAssignmentForm

from dal import autocomplete
from collections import defaultdict
from itertools import chain
from io import BytesIO
import zipfile
import tempfile
import json
from pathlib import Path
from PIL import ImageFont, ImageDraw
from PIL import Image as PILImage
from rest_framework import serializers as srlz
from rest_framework.renderers import JSONRenderer
import logging
logger = logging.getLogger(__name__)


def home(request):
    # Subqueries to count related objects for each child model
    image_count = Image.objects.filter(
        category=OuterRef('pk'), private_new=False
    ).values('category').annotate(count=Count('id')).values('count')

    sound_count = Sound.objects.filter(
        category=OuterRef('pk'), private_new=False
    ).values('category').annotate(count=Count('id')).values('count')

    question_count = Question.objects.filter(
        category=OuterRef('pk'), private_new=False
    ).values('category').annotate(count=Count('id')).values('count')

    hint_count = Hints.objects.filter(
        category=OuterRef('pk'), private_new=False
    ).values('category').annotate(count=Count('id')).values('count')

    whoknowsmore_count = WhoKnowsMore.objects.filter(
        category=OuterRef('pk'), private_new=False
    ).values('category').annotate(count=Count('id')).values('count')

    # Aggregate all subqueries
    newest_categories = Category.objects.filter(private=False).annotate(
        file_count=Coalesce(Subquery(image_count, output_field=IntegerField()), Value(0)) +
                   Coalesce(Subquery(sound_count, output_field=IntegerField()), Value(0)) +
                   Coalesce(Subquery(question_count, output_field=IntegerField()), Value(0)) +
                   Coalesce(Subquery(hint_count, output_field=IntegerField()), Value(0)) +
                   Coalesce(Subquery(whoknowsmore_count, output_field=IntegerField()), Value(0))
    ).filter(file_count__gt=0).order_by('-created_on')[:4]
    latest_create_dates = sorted(
        [c.latest_elements() for c in newest_categories],
        key=lambda x: x['latest_create_date'], reverse=True
    )[:4]
    
    return render(request, 'home.html', {
        'newest_categories': newest_categories,
        'latest_create_dates': latest_create_dates
    })


class GameTypeView(ListView):
    queryset = GameType.objects.all()
    template_name = "game_type_list.html"

    def get_queryset(self):
        self.qs = super().get_queryset().filter(available=True)
        return self.qs

    def get_context_data(self):
        context = super().get_context_data()
        context['game_types'] = self.qs
        return context


class CategoryView(ListView):
    queryset = Category.objects.all()
    template_name = "category_list.html"

    def get_queryset(self):
        return Category.objects.public_for_game_type(self.kwargs['game_type'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_queryset()
        context['game_type'] = get_object_or_404(GameType, pk=self.kwargs['game_type'])
        return context


def category_detail(request, game_type, id):
    category = get_object_or_404(Category, id=id)

    # Mapping game type IDs to download URLs
    download_urls = {
        1: "gamefiles:sound-download",
        2: "gamefiles:image-download",
        3: "gamefiles:hint-download",
        4: "gamefiles:question-download",
        5: "gamefiles:whoknowsmore-download",
    }
    
    # Get the correct download URL based on category type
    category_download_url = download_urls.get(category.game_type.id, "gamefiles:whoknowsmore-download")

    category_elements = category.get_related_objects()
    category_elements = category_elements.filter(private_new=False) if category_elements else []
    
    difficulty_count = {}
    for e in category_elements:
        difficulty_count[e.difficulty] = difficulty_count.get(e.difficulty, 0) + 1

    return render(request, 'category_detail.html', {
        'game_type': game_type,
        'category': category,
        'labels': list(difficulty_count.keys()),
        'data': list(difficulty_count.values()),
        "category_download_url": category_download_url,
    })


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'per_page': 10})
    

class CategoryCreateView(LoginRequiredMixin, SuccessUrlMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class CategoryEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-edit.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class ImageEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Image
    form_class = ImageEditForm
    template_name = 'image-edit.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class SoundEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class QuestionEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class HintEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Hints
    form_class = HintForm
    template_name = 'hint-edit.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class WhoknowsmoreEditView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = WhoKnowsMore
    form_class = WhoKnowsMoreForm
    template_name = 'who-knows-more-edit.html'
    object = None

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())

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
        if (form := self.get_form()).is_valid() and (formset := WhoKnowsMoreElementFormSetUpdate(self.request.POST, instance=self.object)).is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.category_element = self.object
            instance.count_id = WhoKnowsMoreElement.objects.filter(category_element=self.object).count() + 1
            instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        # Add non-form errors (e.g., from formset.clean()) to messages
        for error in formset.non_form_errors():
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))


class BaseDeleteView(LoginRequiredMixin, SuccessUrlMixin, DeleteView):
    #def get(self, request, *args, **kwargs):
    #    # Skip rendering a confirmation page and directly perform deletion
    #    return self.delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"{self.model.__name__} successfully deleted.")
        return super().delete(request, *args, **kwargs)
    
    #template_name = "confirm_delete.html"


class CategoryDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = Category


class ImageDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = Image


class SoundDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = Sound


class QuestionDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = Question


class HintDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = Hints


class WhoknowsmoreDeleteView(BaseDeleteView, LoginRequiredMixin):
    model = WhoKnowsMore


class ParentCreateView(SuccessUrlMixin, CreateView):
    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'per_page': 10})
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save()
        return super().form_valid(form)


class ImageCreateView(LoginRequiredMixin, ParentCreateView):
    model = Image
    form_class = ImageForm
    template_name = 'image-edit.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        img = PILImage.open(form.instance.image_file)
        file_name = form.instance.solution
        width, height = img.size

        font_size = max(int(min(width, height) / 50), 10)
        font_path = Path(settings.BASE_DIR) / "static/fonts/Montserrat-Regular.ttf"
        font = ImageFont.truetype(str(font_path), font_size)

        license_urls = {
            "CC0": "https://creativecommons.org/publicdomain/zero/1.0/deed.de",
            "CC BY": "https://creativecommons.org/licenses/by/4.0/deed.de",
            "CC BY-SA": "https://creativecommons.org/licenses/by-sa/3.0/de/",
        }
        text_license = license_urls.get(form.instance.license, "Unknown License")

        text = f"by {form.instance.author} "
        text += "(modified from original) " if form.instance.file_changed else ""
        text += f"licensed under {form.instance.license}"

        img_edit = ImageDraw.Draw(img)
        text_position = (width - font.getsize(text)[0] - 5, height - font.getsize(text)[1] - 20)
        license_position = (width - font.getsize(text_license)[0] - 5, height - font.getsize(text_license)[1] - 5)

        img_edit.text(text_position, text, (222, 222, 222), font=font)
        img_edit.text(license_position, text_license, (222, 222, 222), font=font)

        with BytesIO() as image_io:
            img.save(image_io, format=img.format)
            form.instance.image_file = ContentFile(image_io.getvalue(), f"{file_name}.{img.format.lower()}")

        return super().form_valid(form)


class SoundCreateView(LoginRequiredMixin, ParentCreateView):
    model = Sound
    form_class = SoundForm
    template_name = 'sound-edit.html'


class QuestionCreateView(LoginRequiredMixin, ParentCreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'question-edit.html'


class HintCreateView(LoginRequiredMixin, ParentCreateView):
    model = Hints
    form_class = HintForm
    template_name = 'hint-edit.html'


class WhoknowsmoreCreateView(LoginRequiredMixin, ParentCreateView):
    model = WhoKnowsMore
    form_class = WhoKnowsMoreForm
    template_name = 'who-knows-more-edit.html'
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object  # Ensure `object` is always in context
        return context
    
    def get(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        formset = WhoKnowsMoreElementFormSet()
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        formset = WhoKnowsMoreElementFormSet(self.request.POST)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        form.instance.created_by = self.request.user
        self.object = form.save()
        instances = formset.save(commit=False)

        for instance in instances:
            instance.category_element = self.object
            instance.count_id = WhoKnowsMoreElement.objects.filter(category_element=self.object).count() + 1
            instance.save()

        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

class WhoKnowsMoreElementSerializer(srlz.ModelSerializer):
    class Meta:
        model = WhoKnowsMoreElement
        fields = ('count_id', 'answer')


class WhoKnowsMoreSerializer(srlz.ModelSerializer):
    answers = WhoKnowsMoreElementSerializer(many=True)

    class Meta:
        model = WhoKnowsMore
        fields = ('id', 'solution', 'answers')


class BaseDownloadView(LoginRequiredMixin, FormView):
    """Base class for all download views to reduce redundancy."""
    
    template_name = 'sound-download.html'

    def get_success_url(self):
        category = Category.objects.get(pk=self.kwargs['category_id'])
        return reverse('gamefiles:category_detail', kwargs={'id': category.id, 'game_type': category.game_type.id})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs['category_id'])
        ctx.update({
            'category_id': self.kwargs['category_id'],
            'game_type_id': category.game_type.id
        })
        return ctx

    def get_initial(self):
        return {'category': self.kwargs['category_id']}

    def filter_queryset(self, model, form):
        """Filters objects based on form criteria."""
        user = self.request.user
        created_by = form.cleaned_data["created_by"] or User.objects.all()
        difficulty_range = range(
            int(form.cleaned_data["min_difficulty"]),
            int(form.cleaned_data["max_difficulty"]) + 1
        )

        filters = {
            "category": form.cleaned_data["category"],
            "created_by__in": created_by,
            "private_new": False,
            "difficulty__in": difficulty_range,
        }
        
        queryset = model.objects.filter(**filters).distinct()

        if form.cleaned_data["explicit"]:
            queryset = queryset.filter(explicit=False)
        
        if form.cleaned_data["min_upload_date"]:
            queryset = queryset.filter(created_on__gte=form.cleaned_data["min_upload_date"])
        
        if form.cleaned_data["max_upload_date"]:
            queryset = queryset.filter(created_on__lte=form.cleaned_data["max_upload_date"])
        
        if not form.cleaned_data["private_new"]:
            private_queryset = model.objects.filter(created_by=user, private_new=True)
            queryset = list(chain(queryset, private_queryset))
        
        return queryset

    def generate_zip_response(self, files, category_name, folder_name):
        """Creates and returns a zip file response."""
        zip_buffer = BytesIO()
        zip_filename = f"{category_name}.zip"
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_name, file_path in files:
                zf.write(file_path, f"{folder_name}/{file_name}")

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response


class ImageDownloadView(BaseDownloadView):
    form_class = ImageDownloadForm

    def form_valid(self, form):
        images = self.filter_queryset(Image, form)
        category_name = form.cleaned_data["category"].name_de

        files = [
            (img.image_file.name.split("/")[-1], f"{settings.MEDIA_ROOT}/{img.image_file.name}")
            for img in images
            if len(img.image_file.name.split("/")) > 2
        ]

        return self.generate_zip_response(files, category_name, "Bilder")


class SoundDownloadView(BaseDownloadView):
    form_class = SoundDownloadForm

    def form_valid(self, form):
        sounds = self.filter_queryset(Sound, form)
        category_name = form.cleaned_data["category"].name_de

        files = [
            (snd.sound_file.name.split("/")[-1], f"{settings.MEDIA_ROOT}/{snd.sound_file.name}")
            for snd in sounds
            if len(snd.sound_file.name.split("/")) > 2
        ]

        return self.generate_zip_response(files, category_name, "Audio")


class QuestionDownloadView(BaseDownloadView):
    form_class = QuestionDownloadForm

    def form_valid(self, form):
        questions = self.filter_queryset(Question, form)
        category_name = form.cleaned_data["category"].name_de

        json_str = serialize('json', questions)
        zip_buffer = BytesIO()
        zip_filename = f"{category_name}.zip"
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                tmp_file.flush
                tmp_file.seek(0)
                zf.write(tmp_file.name, f"{category_name}.json")
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response


class HintDownloadView(BaseDownloadView):
    form_class = HintDownloadForm

    def form_valid(self, form):
        hints = self.filter_queryset(Hints, form)
        category_name = form.cleaned_data["category"].name_de

        json_str = serialize('json', hints)
        zip_buffer = BytesIO()
        zip_filename = f"{category_name}.zip"
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                tmp_file.flush
                tmp_file.seek(0)
                zf.write(tmp_file.name, f"{category_name}.json")
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response


class WhoknowsmoreDownloadView(BaseDownloadView):
    form_class = WhoKnowsMoreDownloadForm

    def form_valid(self, form):
        whoknowsmore = self.filter_queryset(WhoKnowsMore, form)
        category_name = form.cleaned_data["category"].name_de

        serialized_data = WhoKnowsMoreSerializer(whoknowsmore, many=True).data
        json_str = JSONRenderer().render(serialized_data)
        zip_buffer = BytesIO()
        zip_filename = f"{category_name}.zip"
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                json.dump(json.loads(json_str), tmp_file, indent=6, ensure_ascii=False)
                tmp_file.flush
                tmp_file.seek(0)
                zf.write(tmp_file.name, f"{category_name}.json")
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response

def solution_form_view(request):
    """Handles solution selection through form submission."""
    if request.method == 'POST':
        form = SolutionForm(request.POST)
        if form.is_valid():
            game_type = form.cleaned_data['game_type'].id
            category_element = form.cleaned_data['category_element'].id
            return redirect('gamefiles:solution', game_type=game_type, category_element=category_element)
    else:
        form = SolutionForm()

    return render(request, 'solution_form.html', {'form': form})

def solution(request, game_type, category_element):
    """Fetches and returns the solution based on game type."""
    game_types = {
        "10 Hinweise": (Hints, "Hints"),
        "Wer weiß mehr?": (WhoKnowsMore, "WhoKnowsMore"),
    }

    game = GameType.objects.get(id=game_type)
    model, solution_type = game_types.get(game.name_de, (None, None))

    if not model:
        return render(request, 'solution.html', {'solution': None})

    solution = model.objects.get(id=category_element)
    if solution_type == "WhoKnowsMore":
        solution = solution.show_solution()

    return render(request, 'solution.html', {'solution': {"type": solution_type, "qs": solution}})


def leaderboard_view(request):
    team_assignment_result = None
    if request.method == "POST":
        if 'assign_teams' in request.POST:
            team_form = RandomTeamAssignmentForm(request.POST)
            form = QuizGameResultForm()  # keep the other form empty
            if team_form.is_valid():
                team_assignment_result = team_form.assign_teams()
        else:
            form = QuizGameResultForm(request.POST)
            team_form = RandomTeamAssignmentForm()
            if form.is_valid():
                form.save()
                return redirect("gamefiles:leaderboard")
    else:
        form = QuizGameResultForm()
        team_form = RandomTeamAssignmentForm()

    # user → {'points': float, 'games': int, 'wins': int}
    user_stats = defaultdict(lambda: {'points': 0.0, 'games': 0, 'wins': 0})

    results = QuizGameResult.objects.prefetch_related(
        'team1_users', 'team2_users', 'team3_users', 'team4_users'
    )

    for result in results:
        scores = {
            'team1': result.team1_points,
            'team2': result.team2_points,
            'team3': result.team3_points,
            'team4': result.team4_points,
        }

        # --- Track wins (raw score, unnormalized) ---
        max_score = max(scores.values())
        winning_teams = [team for team, score in scores.items() if score == max_score]

        for team_key in winning_teams:
            users = getattr(result, f"{team_key}_users").all()
            for user in users:
                user_stats[user]['wins'] += 1

        # --- Normalize scores ---
        min_score = min(scores.values())
        shifted_scores = {
            team: score - min_score for team, score in scores.items()
        }

        total_shifted = sum(shifted_scores.values())
        if total_shifted == 0:
            continue  # Avoid division by zero (e.g., all scores equal)

        normalized_scores = {
            team: (shifted / total_shifted) * 10
            for team, shifted in shifted_scores.items()
        }

        for team_key, team_score in normalized_scores.items():
            team_users = getattr(result, f"{team_key}_users").all()
            for user in team_users:
                user_stats[user]['points'] += team_score
                user_stats[user]['games'] += 1

    # Build leaderboard
    leaderboard = []
    for user, stats in user_stats.items():
        if stats['games'] > 0:
            leaderboard.append({
                'user': user,
                'avg_points': stats['points'] / stats['games'],
                'games': stats['games'],
                'wins': stats['wins'],
            })

    # Calculate win percentages and find the max
    for entry in leaderboard:
        entry['win_percentage'] = (entry['wins'] / entry['games'] * 100) if entry['games'] > 0 else 0.0

    # Find users with the most wins, and among them, those with the fewest games
    if leaderboard:
        max_wins_value = max(entry['wins'] for entry in leaderboard)
        min_games_for_max_wins = min(
            entry['games'] for entry in leaderboard if entry['wins'] == max_wins_value
        )
        # Mark crown for users with max_wins and min_games_for_max_wins
        for entry in leaderboard:
            entry['award_crown'] = (
                entry['wins'] == max_wins_value and entry['games'] == min_games_for_max_wins
            )
        max_wins = max_wins_value
        max_win_percentage = max(entry['win_percentage'] for entry in leaderboard)
    else:
        max_wins = 0
        max_win_percentage = 0.0
        for entry in leaderboard:
            entry['award_crown'] = False

    leaderboard.sort(key=lambda x: (-x['avg_points'], -x['wins']))

    return render(request, 'leaderboard.html', {
        'leaderboard': leaderboard,
        'form': form,
        'team_form': team_form,
        'team_assignment_result': team_assignment_result,
        'max_wins': max_wins,
        'max_win_percentage': max_win_percentage,
    })

class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        user_categories = Category.objects.filter(created_by=self.request.user)
        public_categories = Category.objects.filter(private=False)
        qs = user_categories | public_categories

        if game_type := self.forwarded.get('game_type'):
            qs = qs.filter(game_type=game_type)

        if self.q:
            qs = qs.filter(name_de__icontains=self.q)

        return qs
    

class CategoryElementAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete for filtering category elements by selected Category."""
    def get_queryset(self):
        category_id = self.forwarded.get('category', None)
        game_type_id = self.forwarded.get('game_type', None)
        qs = []
        # Determine the correct model for category elements
        game_types = {
            "10 Hinweise": Hints,
            "Wer weiß mehr?": WhoKnowsMore,
        }

        game_type = get_object_or_404(GameType, id=game_type_id)
        model = game_types.get(game_type.name_de)

        if model:
            if category_id:
                qs = model.objects.filter(category_id=category_id)
            else:
                qs = model.objects.all()
        
        if self.q:
            qs = qs.filter(pk=self.q)

        return qs


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(username__icontains=self.q)
        return qs