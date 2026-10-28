"""
CreatorSpark — URL Routing
Routes for public pages, authentication, creator dashboard,
idea generator, saved ideas library, content planner, caption studio, and media library.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public & Health Check
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('health/', views.health_check, name='health_check'),
    path('api/sample-idea/', views.sample_idea_api, name='sample_idea_api'),

    # Authentication & Onboarding
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Creator Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Content Idea Generator & Saving
    path('generator/', views.generator_view, name='generator'),
    path('ideas/save/', views.save_generated_idea, name='save_generated_idea'),

    # Saved Ideas Library
    path('ideas/', views.saved_ideas_list, name='saved_ideas_list'),
    path('ideas/<int:pk>/', views.idea_detail_view, name='idea_detail'),
    path('ideas/<int:pk>/edit/', views.idea_edit_view, name='idea_edit'),
    path('ideas/<int:pk>/favorite/', views.idea_toggle_favorite, name='idea_toggle_favorite'),
    path('ideas/<int:pk>/delete/', views.idea_delete_view, name='idea_delete'),

    # Content Planner
    path('planner/', views.planner_list_view, name='planner_list'),
    path('planner/new/', views.planner_create_view, name='planner_create'),
    path('planner/<int:pk>/edit/', views.planner_edit_view, name='planner_edit'),
    path('planner/<int:pk>/delete/', views.planner_delete_view, name='planner_delete'),

    # Caption & Hashtag Studio
    path('studio/', views.caption_studio_view, name='caption_studio'),

    # Reference Media Library
    path('media-library/', views.media_library_view, name='media_library'),
    path('media-library/<int:pk>/delete/', views.media_delete_view, name='media_delete'),
]
