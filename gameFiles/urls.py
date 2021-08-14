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
    path('category-edit/<int:pk>', views.CategoryEditView.as_view(), name='category-edit'),
    path('image-edit/<int:pk>', views.ImageEditView.as_view(), name='image-edit'),
    path('sound-edit/<int:pk>', views.SoundEditView.as_view(), name='sound-edit'),
    path('question-edit/<int:pk>', views.QuestionEditView.as_view(), name='question-edit'),
    path('image-download/<int:category_id>', views.ImageDownloadView.as_view(), name='image-download'),
    path('sound-download/<int:category_id>', views.SoundDownloadView.as_view(), name='sound-download'),
    path('question-download/<int:category_id>', views.QuestionDownloadView.as_view(), name='question-download'),
    path('ajax/get_profile_table/<int:user_id>/<str:per_page>/', account_views.get_profile_table, name='get_profile_table'),
    path('ajax/set_profile_filter/<str:per_page>/', account_views.set_profile_filter, name='set_profile_filter'),
    path('tag-autocomplete', views.TagAutocomplete.as_view(create_field='name_de'), name='tag-autocomplete'),
    path('category-autocomplete', views.CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('user-autocomplete', views.UserAutocomplete.as_view(), name='user-autocomplete'),
]