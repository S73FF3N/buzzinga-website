from django.urls import path
from . import views
from account import views as account_views

urlpatterns = [
    # General Views
    path('', views.GameTypeView.as_view(), name='game_type_list'),
    path('categories/<int:game_type>/', views.CategoryView.as_view(), name='category_list'),
    path('<int:game_type>/<int:id>/', views.category_detail, name='category_detail'),
    path('solution-form/', views.solution_form_view, name='solution_form'),
    path('get_category_elements/', views.get_category_elements, name='get_category_elements'),
    path('solution/<int:game_type>/<int:category_element>/', views.solution, name='solution'),

    # Category Views
    path('category-create', views.CategoryCreateView.as_view(), name='category-create'),
    path('category-edit/<int:pk>', views.CategoryEditView.as_view(), name='category-edit'),
    path('category-delete/<int:pk>', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Autocomplete Views
    path('category-autocomplete', views.CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('category-element-autocomplete/', views.CategoryElementAutocomplete.as_view(), name='category-element-autocomplete'),
    path('user-autocomplete', views.UserAutocomplete.as_view(), name='user-autocomplete'),

    # AJAX Calls
    path('ajax/get_profile_table/<str:per_page>/', account_views.get_profile_table, name='get_profile_table'),
    path('ajax/set_profile_filter/<str:per_page>/', account_views.set_profile_filter, name='set_profile_filter'),
]

# Dynamic CRUD operations for multiple models
models = ["sound", "image", "question", "hint", "whoknowsmore"]

for model in models:
    urlpatterns.extend([
        path(f'{model}-create', getattr(views, f"{model.capitalize()}CreateView").as_view(), name=f'{model}-create'),
        path(f'{model}-edit/<int:pk>', getattr(views, f"{model.capitalize()}EditView").as_view(), name=f'{model}-edit'),
        path(f'{model}-delete/<int:pk>', getattr(views, f"{model.capitalize()}DeleteView").as_view(), name=f'{model}-delete'),
        path(f'{model}-download/<int:category_id>', getattr(views, f"{model.capitalize()}DownloadView").as_view(), name=f'{model}-download'),
    ])
