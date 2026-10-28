from django.contrib import admin
from .models import UserProfile, ContentIdea, PlannerEntry, ReferenceMedia


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'instagram_handle', 'primary_niche', 'target_audience', 'created_at')
    search_fields = ('user__username', 'user__email', 'instagram_handle')
    list_filter = ('primary_niche', 'target_audience')


@admin.register(ContentIdea)
class ContentIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'niche', 'content_format', 'objective', 'is_favorite', 'created_at')
    list_filter = ('content_format', 'objective', 'is_favorite', 'niche')
    search_fields = ('title', 'hook', 'caption_draft', 'user__username')


@admin.register(PlannerEntry)
class PlannerEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'content_format', 'planned_date', 'status', 'created_at')
    list_filter = ('status', 'content_format', 'planned_date')
    search_fields = ('title', 'notes', 'user__username')


@admin.register(ReferenceMedia)
class ReferenceMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_size', 'created_at')
    search_fields = ('title', 'caption_notes', 'user__username')
