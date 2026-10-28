"""
CreatorSpark — Form Definitions & Validation
Handles User Registration, Creator Profile Onboarding, Idea Generation,
Content Planning, and Reference Media Uploads with strict server-side validation.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from PIL import Image
import io

from .models import UserProfile, ContentIdea, PlannerEntry, ReferenceMedia


# -----------------------------------------------------------------------------
# 1. User Registration Form
# -----------------------------------------------------------------------------
class RegistrationForm(forms.ModelForm):
    """
    Secure registration form with username, email, password, and confirmation.
    Applies Django's built-in password validators and ensures unique email.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        help_text='Required for creator communications and account recovery.'
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a secure password'}),
        help_text='Must be at least 8 characters and not too common.'
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a unique username'}),
        }
        help_texts = {
            'username': 'Letters, digits and @/./+/-/_ only.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match. Please verify and try again.')

        if password:
            # Run Django's configured password validators
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error('password', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Ensure profile exists
            UserProfile.objects.get_or_create(user=user)
        return user


# -----------------------------------------------------------------------------
# 2. Creator Profile Onboarding & Settings Form
# -----------------------------------------------------------------------------
class UserProfileForm(forms.ModelForm):
    """
    Form for updating creator preferences, default niche, and Instagram handle.
    """
    class Meta:
        model = UserProfile
        fields = ['instagram_handle', 'primary_niche', 'target_audience', 'bio_notes']
        widgets = {
            'instagram_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@yourhandle'}),
            'primary_niche': forms.Select(attrs={'class': 'form-select'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'bio_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Aesthetic notes, content goals, or niche focus...'}),
        }

    def clean_instagram_handle(self):
        handle = self.cleaned_data.get('instagram_handle', '').strip()
        if handle and not handle.startswith('@'):
            handle = f'@{handle}'
        return handle


# -----------------------------------------------------------------------------
# 3. Idea Generator Input Form
# -----------------------------------------------------------------------------
class IdeaGeneratorForm(forms.Form):
    """
    Input controls for the rule-based idea generation engine.
    """
    niche = forms.ChoiceField(
        choices=UserProfile.NICHE_CHOICES,
        initial='lifestyle',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'genNiche'})
    )
    custom_niche = forms.CharField(
        required=False,
        label='Custom Niche (if selected above)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sustainable Home Decor'})
    )
    audience = forms.ChoiceField(
        choices=UserProfile.AUDIENCE_CHOICES,
        initial='beginners',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'genAudience'})
    )
    custom_audience = forms.CharField(
        required=False,
        label='Custom Audience (if selected above)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote Freelancers'})
    )
    content_format = forms.ChoiceField(
        choices=ContentIdea.FORMAT_CHOICES,
        initial='reels',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'genFormat'})
    )
    objective = forms.ChoiceField(
        choices=ContentIdea.GOAL_CHOICES,
        initial='engagement',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'genObjective'})
    )
    tone = forms.ChoiceField(
        choices=ContentIdea.TONE_CHOICES,
        initial='conversational',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'genTone'})
    )
    keywords = forms.CharField(
        required=False,
        label='Specific Topic or Keyword (Optional)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Morning Reset, Squat Depth, AirTag hacks'})
    )


# -----------------------------------------------------------------------------
# 4. Content Idea Form (Create & Edit Saved Ideas)
# -----------------------------------------------------------------------------
class ContentIdeaForm(forms.ModelForm):
    """
    Form to manually create or refine an existing saved idea.
    Converts outlines and hashtags between text and JSON fields.
    """
    outline_text = forms.CharField(
        label='Content Sequence / Outline',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'One step or slide per line...'}),
        help_text='Enter each slide or video scene beat on a new line.'
    )
    hashtags_text = forms.CharField(
        label='Hashtags',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#CreatorLife #InstagramTips #ReelsDaily'}),
        help_text='Separate tags with spaces or commas.'
    )

    class Meta:
        model = ContentIdea
        fields = [
            'title', 'niche', 'audience', 'content_format', 'objective',
            'tone', 'hook', 'caption_draft', 'call_to_action',
            'estimated_difficulty', 'is_favorite'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'niche': forms.TextInput(attrs={'class': 'form-control'}),
            'audience': forms.TextInput(attrs={'class': 'form-control'}),
            'content_format': forms.Select(attrs={'class': 'form-select'}),
            'objective': forms.Select(attrs={'class': 'form-select'}),
            'tone': forms.Select(attrs={'class': 'form-select'}),
            'hook': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'caption_draft': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'call_to_action': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_difficulty': forms.TextInput(attrs={'class': 'form-control'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Prefill outline text from JSONField list
            if isinstance(self.instance.outline, list):
                self.fields['outline_text'].initial = '\n'.join(self.instance.outline)
            # Prefill hashtags text from JSONField list
            if isinstance(self.instance.hashtags, list):
                self.fields['hashtags_text'].initial = ' '.join(self.instance.hashtags)

    def clean_outline_text(self):
        text = self.cleaned_data.get('outline_text', '')
        return [line.strip() for line in text.split('\n') if line.strip()]

    def clean_hashtags_text(self):
        raw = self.cleaned_data.get('hashtags_text', '')
        tags = []
        for item in raw.replace(',', ' ').split():
            clean_tag = item.strip()
            if clean_tag:
                if not clean_tag.startswith('#'):
                    clean_tag = f'#{clean_tag}'
                tags.append(clean_tag)
        return tags

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.outline = self.cleaned_data['outline_text']
        instance.hashtags = self.cleaned_data['hashtags_text']
        if commit:
            instance.save()
        return instance


# -----------------------------------------------------------------------------
# 5. Content Planner Entry Form
# -----------------------------------------------------------------------------
class PlannerEntryForm(forms.ModelForm):
    """
    Form to schedule posts on the creator calendar with status tracking.
    """
    class Meta:
        model = PlannerEntry
        fields = ['title', 'content_format', 'planned_date', 'planned_time', 'status', 'idea', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Morning Skincare Reel'}),
            'content_format': forms.Select(attrs={'class': 'form-select'}),
            'planned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'idea': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Filming notes, outfit/gear requirements, or caption tweaks...'}),
        }
        help_texts = {
            'status': 'Track progress from concept to published post.',
            'idea': 'Optionally link this scheduled post to an idea from your library.',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Restrict linked ideas dropdown strictly to the authenticated user's own ideas
            self.fields['idea'].queryset = ContentIdea.objects.filter(user=user)
            self.fields['idea'].empty_label = '— None (Standalone post) —'


# -----------------------------------------------------------------------------
# 6. Reference Media Upload Form
# -----------------------------------------------------------------------------
class ReferenceMediaForm(forms.ModelForm):
    """
    Form to upload and manage reference images with strict type and size validation.
    """
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    class Meta:
        model = ReferenceMedia
        fields = ['title', 'image', 'caption_notes', 'idea']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lighting moodboard, cover reference'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp,image/gif'}),
            'caption_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Visual details, shot angles, or aesthetic inspiration notes...'}),
            'idea': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['idea'].queryset = ContentIdea.objects.filter(user=user)
            self.fields['idea'].empty_label = '— None (General Reference) —'

    def clean_image(self):
        uploaded_image = self.cleaned_data.get('image')
        if not uploaded_image:
            raise ValidationError('Please choose an image file to upload.')

        # 1. Size Validation
        if uploaded_image.size > self.MAX_FILE_SIZE:
            mb_size = uploaded_image.size / (1024 * 1024)
            raise ValidationError(f'File size ({mb_size:.1f} MB) exceeds the 5 MB maximum allowed limit.')

        # 2. Extension Validation
        ext = uploaded_image.name.split('.')[-1].lower() if '.' in uploaded_image.name else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f'Unsupported file format (.{ext}). Supported image formats: {", ".join(self.ALLOWED_EXTENSIONS).upper()}.'
            )

        # 3. Genuine Image Verification via Pillow
        try:
            image_data = uploaded_image.read()
            uploaded_image.seek(0)
            img = Image.open(io.BytesIO(image_data))
            img.verify()
        except Exception:
            raise ValidationError('Uploaded file is corrupted or not a valid image format.')

        return uploaded_image


# -----------------------------------------------------------------------------
# 7. Caption and Hashtag Studio Input Form
# -----------------------------------------------------------------------------
class CaptionStudioForm(forms.Form):
    """
    Form controls for drafting captions and generating tiered hashtags in the studio.
    """
    topic = forms.CharField(
        label='Post Topic or Core Message',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3 Nighttime Skincare Mistakes, How I organize my desk, Quick protein breakfast'})
    )
    niche = forms.ChoiceField(
        choices=UserProfile.NICHE_CHOICES,
        initial='lifestyle',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    audience = forms.ChoiceField(
        choices=UserProfile.AUDIENCE_CHOICES,
        initial='beginners',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tone = forms.ChoiceField(
        choices=ContentIdea.TONE_CHOICES,
        initial='conversational',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    style = forms.ChoiceField(
        choices=[
            ('story', 'Relatable Storytelling'),
            ('list', 'Quick Value / Listicle'),
            ('convo', 'Engaging Question & Debate'),
        ],
        initial='story',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
