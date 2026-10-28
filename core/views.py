"""
CreatorSpark — Views & Application Logic
Handles public pages, user authentication, creator dashboard,
content idea generation, saved idea management, content planner,
caption/hashtag studio, and reference media library with strict user isolation.
"""

import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.db import connection
from django.db.models import Q

from .models import UserProfile, ContentIdea, PlannerEntry, ReferenceMedia
from .forms import (
    RegistrationForm, UserProfileForm, IdeaGeneratorForm,
    ContentIdeaForm, PlannerEntryForm, ReferenceMediaForm,
    CaptionStudioForm
)
from .generator import generate_content_ideas, generate_studio_caption, NICHE_TOPICS


# =============================================================================
# 1. Public Pages & Health Check
# =============================================================================

def landing(request):
    """Public landing page."""
    context = {
        'page_title': 'CreatorSpark — Content Idea Generation & Planning Studio',
        'niches': [
            {'id': 'skincare', 'name': 'Skincare & Beauty'},
            {'id': 'fitness', 'name': 'Fitness & Wellness'},
            {'id': 'technology', 'name': 'Tech & Gadgets'},
            {'id': 'fashion', 'name': 'Fashion & Style'},
            {'id': 'food', 'name': 'Food & Culinary'},
            {'id': 'travel', 'name': 'Travel & Adventure'},
            {'id': 'lifestyle', 'name': 'Lifestyle & Productivity'},
            {'id': 'finance', 'name': 'Personal Finance'},
            {'id': 'education', 'name': 'Education & Self-Improvement'},
        ],
        'formats': [
            {'id': 'reels', 'name': 'Instagram Reels', 'badge': 'High Reach'},
            {'id': 'carousel', 'name': 'Educational Carousel', 'badge': 'High Saves'},
            {'id': 'stories', 'name': 'Interactive Stories', 'badge': 'High Engagement'},
            {'id': 'static', 'name': 'Single Static Post', 'badge': 'Aesthetic/Quote'},
        ],
    }
    return render(request, 'core/landing.html', context)


def about(request):
    """About & platform architecture page."""
    return render(request, 'core/about.html', {
        'page_title': 'About CreatorSpark — Transparent Creator Tools',
    })


@require_GET
def health_check(request):
    """System health-check endpoint."""
    db_status = 'disconnected'
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1;')
            row = cursor.fetchone()
            if row and row[0] == 1:
                db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    health_data = {
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'app': 'CreatorSpark',
        'stage': '2 of 5 (Authentication, Generator & Studio Complete)',
        'version': '1.0.0',
        'database': db_status,
        'db_vendor': connection.vendor,
    }
    status_code = 200 if db_status == 'connected' else 503
    return JsonResponse(health_data, status=status_code)


@require_GET
def sample_idea_api(request):
    """Landing page interactive preview API."""
    niche = request.GET.get('niche', 'skincare').lower()
    content_format = request.GET.get('format', 'reels').lower()

    ideas = generate_content_ideas(niche=niche, content_format=content_format, count=1)
    if ideas:
        sample_idea = {
            'title': ideas[0]['title'],
            'hook': ideas[0]['hook'],
            'outline': ideas[0]['outline'],
            'caption': ideas[0]['caption_draft'],
            'hashtags': ideas[0]['hashtags'],
            'cta': ideas[0]['call_to_action'],
            'difficulty': ideas[0]['estimated_difficulty'],
        }
    else:
        sample_idea = {
            'title': '3 Quick Creator Tips to Boost Retention',
            'hook': '"Stop losing viewers in the first 2 seconds!"',
            'outline': ['0-3s Hook', '3-10s Problem', '10-20s Solution', '20-25s Outro'],
            'caption': 'Retention is everything on Instagram Reels. Save this reminder!',
            'hashtags': ['#CreatorTips', '#InstagramGrowth', '#ReelsAdvice'],
            'cta': 'Save this Reel for later!',
            'difficulty': 'Beginner friendly',
        }

    return JsonResponse({
        'niche': niche,
        'format': content_format,
        'idea': sample_idea,
    })


# =============================================================================
# 2. Authentication & Creator Profiles
# =============================================================================

def register_view(request):
    """User registration view with automatic login and profile setup onboarding."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome to CreatorSpark, @{user.username}! Let's customize your creator profile preferences."
            )
            return redirect('profile')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': 'Join CreatorSpark — Creator Registration',
    })


def login_view(request):
    """User login view with validation and redirect support."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Ensure profile exists
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back, @{user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
        'page_title': 'Sign In — CreatorSpark',
    })


def logout_view(request):
    """Safely logs out the user and redirects to the landing page."""
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "You have been safely signed out. See you next post!")
    return redirect('landing')


@login_required
def profile_view(request):
    """Creator profile settings and onboarding flow."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your creator profile preferences were saved successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please check the profile fields below.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'page_title': 'Creator Profile & Settings — CreatorSpark',
    })


# =============================================================================
# 3. Creator Dashboard
# =============================================================================

@login_required
def dashboard_view(request):
    """
    Creator studio dashboard showing real database stats, upcoming content,
    and recent saved ideas with strict user isolation.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Real database statistics
    total_ideas = ContentIdea.objects.filter(user=request.user).count()
    favorite_ideas = ContentIdea.objects.filter(user=request.user, is_favorite=True).count()
    planned_posts = PlannerEntry.objects.filter(user=request.user).exclude(status__in=['published', 'archived']).count()
    published_posts = PlannerEntry.objects.filter(user=request.user, status='published').count()
    media_count = ReferenceMedia.objects.filter(user=request.user).count()

    # Recent saved ideas
    recent_ideas = ContentIdea.objects.filter(user=request.user).order_by('-created_at')[:4]

    # Upcoming scheduled posts
    upcoming_posts = (
        PlannerEntry.objects.filter(user=request.user)
        .exclude(status__in=['published', 'archived'])
        .order_by('planned_date', 'planned_time')[:4]
    )

    context = {
        'page_title': 'Creator Dashboard — CreatorSpark',
        'profile': profile,
        'stats': {
            'total_ideas': total_ideas,
            'favorite_ideas': favorite_ideas,
            'planned_posts': planned_posts,
            'published_posts': published_posts,
            'media_count': media_count,
        },
        'recent_ideas': recent_ideas,
        'upcoming_posts': upcoming_posts,
    }
    return render(request, 'core/dashboard.html', context)


# =============================================================================
# 4. Content Idea Generator Engine
# =============================================================================

@login_required
def generator_view(request):
    """
    Rule-based Idea Generator view.
    Generates 3 to 4 varied ideas and renders them for review, copy, listen, or saving.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    generated_ideas = None
    form_submitted = False

    if request.method == 'POST':
        form = IdeaGeneratorForm(request.POST)
        if form.is_valid():
            form_submitted = True
            niche = form.cleaned_data['custom_niche'] if form.cleaned_data['niche'] == 'custom' and form.cleaned_data['custom_niche'] else form.cleaned_data['niche']
            audience = form.cleaned_data['custom_audience'] if form.cleaned_data['audience'] == 'custom' and form.cleaned_data['custom_audience'] else form.cleaned_data['audience']
            content_format = form.cleaned_data['content_format']
            objective = form.cleaned_data['objective']
            tone = form.cleaned_data['tone']
            keywords = form.cleaned_data['keywords']

            generated_ideas = generate_content_ideas(
                niche=niche,
                audience=audience,
                content_format=content_format,
                objective=objective,
                tone=tone,
                keywords=keywords,
                count=4,
                user_handle=profile.instagram_handle or request.user.username,
            )
            messages.success(request, f"Generated {len(generated_ideas)} tailored content ideas!")
    else:
        # Pre-fill form with creator profile defaults
        form = IdeaGeneratorForm(initial={
            'niche': profile.primary_niche,
            'audience': profile.target_audience,
            'content_format': 'reels',
            'objective': 'engagement',
            'tone': 'conversational',
        })

    return render(request, 'ideas/generator.html', {
        'form': form,
        'generated_ideas': generated_ideas,
        'form_submitted': form_submitted,
        'page_title': 'Content Idea Generator — CreatorSpark',
    })


@login_required
@require_POST
def save_generated_idea(request):
    """
    Saves a generated idea directly to the user's persistent library.
    Supports both AJAX requests (JSON response) and traditional form submissions.
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    title = data.get('title', '').strip()
    if not title:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Idea title is required.'}, status=400)
        messages.error(request, "Unable to save: idea title is required.")
        return redirect('generator')

    # Parse outline and hashtags safely
    raw_outline = data.get('outline', [])
    if isinstance(raw_outline, str):
        try:
            outline_list = json.loads(raw_outline)
        except Exception:
            outline_list = [line.strip() for line in raw_outline.split('\n') if line.strip()]
    else:
        outline_list = list(raw_outline)

    raw_hashtags = data.get('hashtags', [])
    if isinstance(raw_hashtags, str):
        try:
            hashtags_list = json.loads(raw_hashtags)
        except Exception:
            hashtags_list = [tag.strip() for tag in raw_hashtags.replace(',', ' ').split() if tag.strip()]
    else:
        hashtags_list = list(raw_hashtags)

    idea = ContentIdea.objects.create(
        user=request.user,
        title=title,
        niche=data.get('niche', 'lifestyle'),
        audience=data.get('audience', 'beginners'),
        content_format=data.get('content_format', 'reels'),
        objective=data.get('objective', 'engagement'),
        tone=data.get('tone', 'conversational'),
        hook=data.get('hook', ''),
        outline=outline_list,
        caption_draft=data.get('caption_draft', ''),
        hashtags=hashtags_list,
        call_to_action=data.get('call_to_action', ''),
        estimated_difficulty=data.get('estimated_difficulty', 'Beginner friendly'),
    )

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': 'Idea saved to your library!',
            'idea_id': idea.id,
            'title': idea.title
        })

    messages.success(request, f"Saved '{idea.title}' to your ideas library!")
    return redirect('saved_ideas_list')


# =============================================================================
# 5. Saved Ideas Management
# =============================================================================

@login_required
def saved_ideas_list(request):
    """
    Lists saved content ideas with search and filtering capabilities.
    Strictly scoped to request.user.
    """
    ideas = ContentIdea.objects.filter(user=request.user)

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        ideas = ideas.filter(
            Q(title__icontains=q) |
            Q(caption_draft__icontains=q) |
            Q(hook__icontains=q) |
            Q(niche__icontains=q)
        )

    # Niche filter
    filter_niche = request.GET.get('niche', '').strip()
    if filter_niche:
        ideas = ideas.filter(niche__iexact=filter_niche)

    # Format filter
    filter_format = request.GET.get('format', '').strip()
    if filter_format:
        ideas = ideas.filter(content_format=filter_format)

    # Favorite filter
    filter_fav = request.GET.get('favorite', '').strip()
    if filter_fav == '1':
        ideas = ideas.filter(is_favorite=True)

    # Available niches and formats for filter dropdowns
    user_niches = ContentIdea.objects.filter(user=request.user).values_list('niche', flat=True).distinct()

    return render(request, 'ideas/saved_list.html', {
        'ideas': ideas,
        'search_query': q,
        'current_niche': filter_niche,
        'current_format': filter_format,
        'is_favorite_filter': filter_fav == '1',
        'user_niches': user_niches,
        'page_title': 'My Saved Ideas — CreatorSpark',
    })


@login_required
def idea_detail_view(request, pk):
    """Detailed view for a specific saved idea with associated planner and media."""
    idea = get_object_or_404(ContentIdea, pk=pk, user=request.user)
    linked_planner = idea.planner_entries.all()
    linked_media = idea.reference_images.all()

    return render(request, 'ideas/detail.html', {
        'idea': idea,
        'linked_planner': linked_planner,
        'linked_media': linked_media,
        'page_title': f"{idea.title} — CreatorSpark",
    })


@login_required
def idea_edit_view(request, pk):
    """Edit a saved idea."""
    idea = get_object_or_404(ContentIdea, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ContentIdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated idea '{idea.title}' successfully!")
            return redirect('idea_detail', pk=idea.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ContentIdeaForm(instance=idea)

    return render(request, 'ideas/edit.html', {
        'form': form,
        'idea': idea,
        'page_title': f"Edit: {idea.title} — CreatorSpark",
    })


@login_required
@require_POST
def idea_toggle_favorite(request, pk):
    """Toggles favorite status on a saved idea."""
    idea = get_object_or_404(ContentIdea, pk=pk, user=request.user)
    idea.is_favorite = not idea.is_favorite
    idea.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': idea.is_favorite,
            'message': 'Favorited' if idea.is_favorite else 'Unfavorited',
        })

    msg = f"Added '{idea.title}' to favorites." if idea.is_favorite else f"Removed '{idea.title}' from favorites."
    messages.info(request, msg)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'saved_ideas_list'
    return redirect(next_url)


@login_required
@require_http_methods(['GET', 'POST'])
def idea_delete_view(request, pk):
    """Deletes a saved idea with explicit user confirmation."""
    idea = get_object_or_404(ContentIdea, pk=pk, user=request.user)

    if request.method == 'POST':
        title = idea.title
        idea.delete()
        messages.success(request, f"Idea '{title}' was permanently deleted.")
        return redirect('saved_ideas_list')

    return render(request, 'ideas/confirm_delete.html', {
        'idea': idea,
        'page_title': f"Delete Idea: {idea.title}",
    })


# =============================================================================
# 6. Content Planner & Calendar
# =============================================================================

@login_required
def planner_list_view(request):
    """
    Content schedule planner grouped by status and timeline.
    Strictly isolated per user.
    """
    entries = PlannerEntry.objects.filter(user=request.user)

    # Filter by status
    status_filter = request.GET.get('status', 'all').strip()
    if status_filter != 'all' and status_filter in dict(PlannerEntry.STATUS_CHOICES):
        entries = entries.filter(status=status_filter)

    # Group into Overdue, Today, Upcoming, and Unscheduled
    today = date.today()
    overdue_entries = []
    today_entries = []
    upcoming_entries = []
    unscheduled_entries = []

    for entry in entries:
        if not entry.planned_date:
            unscheduled_entries.append(entry)
        elif entry.planned_date < today and entry.status not in ['published', 'archived']:
            overdue_entries.append(entry)
        elif entry.planned_date == today:
            today_entries.append(entry)
        else:
            upcoming_entries.append(entry)

    return render(request, 'planner/list.html', {
        'entries': entries,
        'current_status': status_filter,
        'status_choices': PlannerEntry.STATUS_CHOICES,
        'overdue_entries': overdue_entries,
        'today_entries': today_entries,
        'upcoming_entries': upcoming_entries,
        'unscheduled_entries': unscheduled_entries,
        'page_title': 'Content Planner & Schedule — CreatorSpark',
    })


@login_required
def planner_create_view(request):
    """Schedule a new post, with optional prefilling from an existing ContentIdea."""
    initial_data = {}
    idea_id = request.GET.get('idea_id')
    if idea_id:
        try:
            idea = ContentIdea.objects.get(pk=idea_id, user=request.user)
            initial_data['title'] = idea.title
            initial_data['content_format'] = idea.content_format
            initial_data['idea'] = idea
            initial_data['notes'] = f"Hook: {idea.hook}\nCTA: {idea.call_to_action}"
        except ContentIdea.DoesNotExist:
            pass

    if request.method == 'POST':
        form = PlannerEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, f"Scheduled post '{entry.title}' in your content planner!")
            return redirect('planner_list')
        else:
            messages.error(request, "Please check the schedule fields below.")
    else:
        form = PlannerEntryForm(initial=initial_data, user=request.user)

    return render(request, 'planner/form.html', {
        'form': form,
        'is_edit': False,
        'page_title': 'Schedule New Post — Content Planner',
    })


@login_required
def planner_edit_view(request, pk):
    """Edit an existing scheduled planner entry."""
    entry = get_object_or_404(PlannerEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = PlannerEntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated scheduled post '{entry.title}'!")
            return redirect('planner_list')
        else:
            messages.error(request, "Please check the schedule fields below.")
    else:
        form = PlannerEntryForm(instance=entry, user=request.user)

    return render(request, 'planner/form.html', {
        'form': form,
        'entry': entry,
        'is_edit': True,
        'page_title': f"Edit Schedule: {entry.title}",
    })


@login_required
@require_http_methods(['GET', 'POST'])
def planner_delete_view(request, pk):
    """Delete a planner entry with confirmation."""
    entry = get_object_or_404(PlannerEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        title = entry.title
        entry.delete()
        messages.success(request, f"Removed '{title}' from your content planner.")
        return redirect('planner_list')

    return render(request, 'planner/confirm_delete.html', {
        'entry': entry,
        'page_title': f"Delete Scheduled Post: {entry.title}",
    })


# =============================================================================
# 7. Caption and Hashtag Studio
# =============================================================================

@login_required
def caption_studio_view(request):
    """
    Interactive studio to draft, refine, and generate captions & tiered hashtags.
    Allows editing, one-click copying, and saving directly to the idea library.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    studio_results = None

    if request.method == 'POST':
        form = CaptionStudioForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            niche = form.cleaned_data['niche']
            audience = form.cleaned_data['audience']
            tone = form.cleaned_data['tone']
            style = form.cleaned_data['style']

            studio_results = generate_studio_caption(
                topic=topic,
                niche=niche,
                audience=audience,
                tone=tone,
                style=style
            )
            messages.success(request, "Generated tailored caption drafts and tiered hashtags!")
    else:
        form = CaptionStudioForm(initial={
            'niche': profile.primary_niche,
            'audience': profile.target_audience,
            'tone': 'conversational',
            'style': 'story',
            'topic': '3 Tips for Daily Consistency',
        })

    return render(request, 'studio/studio.html', {
        'form': form,
        'studio_results': studio_results,
        'page_title': 'Caption & Hashtag Studio — CreatorSpark',
    })


# =============================================================================
# 8. Reference Media Library
# =============================================================================

@login_required
def media_library_view(request):
    """
    Private reference media library.
    Allows uploading moodboards and reference images with strict validation.
    """
    media_items = ReferenceMedia.objects.filter(user=request.user)

    if request.method == 'POST':
        form = ReferenceMediaForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            media = form.save(commit=False)
            media.user = request.user
            if 'image' in request.FILES:
                media.file_size = request.FILES['image'].size
            media.save()
            messages.success(request, f"Uploaded '{media.title}' to your reference media library!")
            return redirect('media_library')
        else:
            messages.error(request, "Upload failed. Please check the file requirements below.")
    else:
        form = ReferenceMediaForm(user=request.user)

    return render(request, 'media/list.html', {
        'media_items': media_items,
        'form': form,
        'page_title': 'Reference Media Library — CreatorSpark',
    })


@login_required
@require_http_methods(['GET', 'POST'])
def media_delete_view(request, pk):
    """Deletes a reference media item and removes the file from disk safely."""
    media = get_object_or_404(ReferenceMedia, pk=pk, user=request.user)

    if request.method == 'POST':
        title = media.title
        # Delete image file from media storage safely
        if media.image:
            try:
                media.image.delete(save=False)
            except Exception:
                pass
        media.delete()
        messages.success(request, f"Reference image '{title}' deleted.")
        return redirect('media_library')

    return render(request, 'media/confirm_delete.html', {
        'media': media,
        'page_title': f"Delete Reference Image: {media.title}",
    })
