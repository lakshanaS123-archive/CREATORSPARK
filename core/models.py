"""
Data models for CreatorSpark.
Provides robust schema for creator profiles, saved content ideas,
planner schedule entries, and reference media, ensuring strict user isolation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """
    Creator Profile and Settings.
    Extends Django's User model with social media creator preferences.
    """
    NICHE_CHOICES = [
        ('beauty', 'Beauty & Cosmetics'),
        ('skincare', 'Skincare & Dermatological Care'),
        ('fashion', 'Fashion & Styling'),
        ('fitness', 'Fitness & Wellness'),
        ('food', 'Food & Culinary'),
        ('travel', 'Travel & Adventure'),
        ('technology', 'Technology & Gadgets'),
        ('education', 'Education & Self-Improvement'),
        ('lifestyle', 'Lifestyle & Productivity'),
        ('finance', 'Personal Finance & Investing'),
        ('custom', 'Custom Niche'),
    ]

    AUDIENCE_CHOICES = [
        ('beginners', 'Beginners & Novices'),
        ('students', 'Students & Young Adults'),
        ('professionals', 'Working Professionals'),
        ('enthusiasts', 'Passionate Enthusiasts'),
        ('custom', 'Custom Audience'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='creator_profile',
        verbose_name=_('User')
    )
    instagram_handle = models.CharField(
        max_length=60,
        blank=True,
        help_text=_('Your Instagram creator handle (e.g. @creatorspark)')
    )
    primary_niche = models.CharField(
        max_length=50,
        choices=NICHE_CHOICES,
        default='lifestyle',
        verbose_name=_('Primary Niche')
    )
    target_audience = models.CharField(
        max_length=50,
        choices=AUDIENCE_CHOICES,
        default='beginners',
        verbose_name=_('Target Audience')
    )
    bio_notes = models.TextField(
        blank=True,
        max_length=500,
        help_text=_('Personal notes, aesthetic guidelines, or creator brand statement.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Creator Profile')
        verbose_name_plural = _('Creator Profiles')

    def __str__(self):
        handle = f" ({self.instagram_handle})" if self.instagram_handle else ""
        return f"{self.user.username}{handle}"


class ContentIdea(models.Model):
    """
    Represents a generated or custom-crafted content idea.
    Stores hooks, structured outlines, captions, hashtags, and format metadata.
    Strictly isolated per authenticated user.
    """
    FORMAT_CHOICES = [
        ('reels', 'Instagram Reel (Short-form video)'),
        ('carousel', 'Carousel (Multi-slide educational/visual)'),
        ('stories', 'Interactive Stories (Polls, Q&A, BTS)'),
        ('static', 'Static Single Post (Aesthetic, quote, photo)'),
        ('educational_series', 'Educational Series (Multi-part breakdown)'),
    ]

    GOAL_CHOICES = [
        ('engagement', 'Drive High Comments & Shares'),
        ('education', 'Provide Actionable Value & Saves'),
        ('community', 'Community Connection & Relatability'),
        ('awareness', 'Product / Service Awareness'),
        ('personal_brand', 'Personal Brand Authority'),
    ]

    TONE_CHOICES = [
        ('informative', 'Informative & Educational'),
        ('entertaining', 'Entertaining & Humorous'),
        ('conversational', 'Casual & Conversational'),
        ('inspirational', 'Inspirational & Motivating'),
        ('professional', 'Professional & Authoritative'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_ideas',
        verbose_name=_('Owner')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Idea Title')
    )
    niche = models.CharField(
        max_length=50,
        verbose_name=_('Niche')
    )
    audience = models.CharField(
        max_length=50,
        verbose_name=_('Target Audience')
    )
    content_format = models.CharField(
        max_length=50,
        choices=FORMAT_CHOICES,
        default='reels',
        verbose_name=_('Content Format')
    )
    objective = models.CharField(
        max_length=50,
        choices=GOAL_CHOICES,
        default='engagement',
        verbose_name=_('Objective')
    )
    tone = models.CharField(
        max_length=50,
        choices=TONE_CHOICES,
        default='conversational',
        verbose_name=_('Tone')
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Optional keywords or specific topic prompts')
    )
    hook = models.TextField(
        verbose_name=_('Opening Hook'),
        help_text=_('The first 3 seconds or cover line to capture viewer attention.')
    )
    outline = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Suggested Content Sequence / Outline'),
        help_text=_('List of steps, slides, or scene beats.')
    )
    caption_draft = models.TextField(
        verbose_name=_('Caption Draft'),
        help_text=_('Draft caption with storytelling body and formatting.')
    )
    hashtags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Hashtags List'),
        help_text=_('Curated list of hashtags categorized by reach tiers.')
    )
    call_to_action = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Suggested Call-To-Action (CTA)')
    )
    estimated_difficulty = models.CharField(
        max_length=50,
        blank=True,
        default='Beginner friendly',
        verbose_name=_('Estimated Production Difficulty')
    )
    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_('Favorited')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Content Idea')
        verbose_name_plural = _('Content Ideas')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_content_format_display()})"

    @property
    def outline_list(self):
        """Returns the outline sequence as a list of strings."""
        if isinstance(self.outline, list):
            return self.outline
        if isinstance(self.outline, str):
            return [line.strip() for line in self.outline.split('\n') if line.strip()]
        return []

    @property
    def hashtags_list(self):
        """Returns the hashtags as a list of cleaned tag strings."""
        if isinstance(self.hashtags, list):
            return self.hashtags
        if isinstance(self.hashtags, str):
            return [tag.strip() for tag in self.hashtags.split() if tag.strip()]
        return []

    @property
    def hashtags_string(self):
        """Returns the hashtags formatted as a single space-separated string."""
        tags = self.hashtags_list
        return ' '.join(tags)


class PlannerEntry(models.Model):
    """
    Represents an item on the creator's content schedule.
    Can link to a saved ContentIdea or be created as an independent schedule item.
    """
    STATUS_CHOICES = [
        ('idea', 'Idea Draft'),
        ('planned', 'Scheduled / Planned'),
        ('in_progress', 'Creating / Filming'),
        ('ready', 'Ready to Post'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='planner_entries',
        verbose_name=_('Owner')
    )
    idea = models.ForeignKey(
        ContentIdea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planner_entries',
        verbose_name=_('Linked Idea')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Post Title')
    )
    content_format = models.CharField(
        max_length=50,
        choices=ContentIdea.FORMAT_CHOICES,
        default='reels'
    )
    planned_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Scheduled Date')
    )
    planned_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Best Posting Time')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_('Publication Status')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Production / Filming Notes')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Planner Entry')
        verbose_name_plural = _('Planner Entries')
        ordering = ['planned_date', 'planned_time', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'planned_date']),
        ]

    def __str__(self):
        date_str = f" for {self.planned_date}" if self.planned_date else ""
        return f"{self.title} [{self.get_status_display()}]{date_str}"


class ReferenceMedia(models.Model):
    """
    Uploaded reference visuals, moodboards, or cover drafts for content planning.
    Strictly isolated per user with file size and type controls.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reference_media',
        verbose_name=_('Owner')
    )
    idea = models.ForeignKey(
        ContentIdea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reference_images',
        verbose_name=_('Associated Idea')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Image Title / Reference Label')
    )
    image = models.ImageField(
        upload_to='reference_media/%Y/%m/',
        verbose_name=_('Reference Image')
    )
    caption_notes = models.TextField(
        blank=True,
        verbose_name=_('Visual Notes & Inspiration')
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text=_('File size in bytes')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Reference Media')
        verbose_name_plural = _('Reference Media Items')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def formatted_size(self):
        """Returns human-readable representation of file size."""
        if not self.file_size:
            return "0 KB"
        kb = self.file_size / 1024
        if kb < 1024:
            return f"{kb:.1f} KB"
        mb = kb / 1024
        return f"{mb:.2f} MB"


# Signals to maintain profile synchronization
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
