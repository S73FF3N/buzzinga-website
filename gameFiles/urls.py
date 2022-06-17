from django.urls import path

from . import views
from account import views as account_views

urlpatterns = [
    path('', views.GameTypeView.as_view(), name='game_type_list'),
    path('categories/<int:game_type>/', views.CategoryView.as_view(), name='category_list'),
    path('<int:game_type>/<int:id>/', views.category_detail, name='category_detail'),
    path('category-create', views.CategoryCreateView.as_view(), name='category-create'),
    path('sound-create', views.SoundCreateView.as_view(), name='sound-create'),
    path('image-create', views.ImageCreateView.as_view(), name='image-create'),
    path('question-create', views.QuestionCreateView.as_view(), name='question-create'),
    path('hint-create', views.HintCreateView.as_view(), name='hint-create'),
    path('whoknowsmore-create', views.WhoKnowsMoreCreateView.as_view(), name='whoknowsmore-create'),
    path('solution/<int:game_type>/<int:category_element>/', views.solution, name='solution'),
    path('category-edit/<int:pk>', views.CategoryEditView.as_view(), name='category-edit'),
    path('image-edit/<int:pk>', views.ImageEditView.as_view(), name='image-edit'),
    path('sound-edit/<int:pk>', views.SoundEditView.as_view(), name='sound-edit'),
    path('question-edit/<int:pk>', views.QuestionEditView.as_view(), name='question-edit'),
    path('hint-edit/<int:pk>', views.HintEditView.as_view(), name='hint-edit'),
    path('whoknowsmore-edit/<int:pk>', views.WhoKnowsMoreEditView.as_view(), name='whoknowsmore-edit'),
    path('category-delete/<int:pk>', views.CategoryDeleteView.as_view(), name='category-delete'),
    path('image-delete/<int:pk>', views.ImageDeleteView.as_view(), name='image-delete'),
    path('sound-delete/<int:pk>', views.SoundDeleteView.as_view(), name='sound-delete'),
    path('question-delete/<int:pk>', views.QuestionDeleteView.as_view(), name='question-delete'),
    path('hint-delete/<int:pk>', views.HintDeleteView.as_view(), name='hint-delete'),
    path('whoknowsmore-delete/<int:pk>', views.WhoKnowsMoreDeleteView.as_view(), name='whoknowsmore-delete'),
    path('image-download/<int:category_id>', views.ImageDownloadView.as_view(), name='image-download'),
    path('sound-download/<int:category_id>', views.SoundDownloadView.as_view(), name='sound-download'),
    path('question-download/<int:category_id>', views.QuestionDownloadView.as_view(), name='question-download'),
    path('hint-download/<int:category_id>', views.HintDownloadView.as_view(), name='hint-download'),
    path('whoknowsmore-download/<int:category_id>', views.WhoKnowsMoreDownloadView.as_view(), name='whoknowsmore-download'),
    path('ajax/get_profile_table/<str:per_page>/', account_views.get_profile_table, name='get_profile_table'),
    path('ajax/set_profile_filter/<str:per_page>/', account_views.set_profile_filter, name='set_profile_filter'),
    path('tag-autocomplete', views.TagAutocomplete.as_view(create_field='name_de'), name='tag-autocomplete'),
    path('category-autocomplete', views.CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('user-autocomplete', views.UserAutocomplete.as_view(), name='user-autocomplete'),
]