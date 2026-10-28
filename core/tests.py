import io
from datetime import date
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import UserProfile, ContentIdea, PlannerEntry, ReferenceMedia
from core.generator import generate_content_ideas, generate_studio_caption


# =============================================================================
# 1. Public Views & Health Check Test Suite
# =============================================================================
class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_landing_page_status_and_content(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CreatorSpark')
        self.assertTemplateUsed(response, 'core/landing.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_about_page_status(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About CreatorSpark')
        self.assertTemplateUsed(response, 'core/about.html')

    def test_health_check_endpoint(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('app'), 'CreatorSpark')
        self.assertEqual(data.get('database'), 'connected')

    def test_sample_idea_api_endpoint(self):
        response = self.client.get(reverse('sample_idea_api'), {'niche': 'skincare', 'format': 'reels'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('idea', data)
        self.assertIn('title', data['idea'])
        self.assertIn('hook', data['idea'])
        self.assertIn('outline', data['idea'])


# =============================================================================
# 2. Authentication & Onboarding Test Suite
# =============================================================================
class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'test_creator',
            'email': 'creator@example.com',
            'password': 'SecurePassword2026!',
            'password_confirm': 'SecurePassword2026!',
        })
        # Successful registration redirects to profile onboarding
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(User.objects.filter(username='test_creator').exists())
        user = User.objects.get(username='test_creator')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'SecurePassword2026!',
            'password_confirm': 'DifferentPassword2026!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password_confirm', 'Passwords do not match. Please verify and try again.')
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())

    def test_user_login_and_logout(self):
        User.objects.create_user(username='login_user', email='login@example.com', password='ValidPassword123!')

        # Login
        response = self.client.post(reverse('login'), {
            'username': 'login_user',
            'password': 'ValidPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Logout
        logout_response = self.client.post(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertRedirects(logout_response, reverse('landing'))

    def test_private_routes_require_authentication(self):
        protected_urls = [
            reverse('dashboard'),
            reverse('generator'),
            reverse('saved_ideas_list'),
            reverse('planner_list'),
            reverse('caption_studio'),
            reverse('media_library'),
            reverse('profile'),
        ]
        for url in protected_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302, f"URL {url} did not redirect unauthenticated user")
            self.assertIn('/login/', res.url)


# =============================================================================
# 3. Creator Profile Test Suite
# =============================================================================
class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profile_user', password='Password123!')
        self.client.login(username='profile_user', password='Password123!')

    def test_profile_update(self):
        response = self.client.post(reverse('profile'), {
            'instagram_handle': 'mycreatorhandle',
            'primary_niche': 'fitness',
            'target_audience': 'enthusiasts',
            'bio_notes': 'Fitness & nutrition creator',
        })
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.instagram_handle, '@mycreatorhandle')
        self.assertEqual(profile.primary_niche, 'fitness')
        self.assertEqual(profile.target_audience, 'enthusiasts')


# =============================================================================
# 4. Content Idea Generator & Saved Ideas CRUD
# =============================================================================
class IdeaGeneratorAndSavedIdeasTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='idea_creator', password='Password123!')
        self.client.login(username='idea_creator', password='Password123!')

    def test_rule_based_generator_engine_output(self):
        ideas = generate_content_ideas(
            niche='skincare',
            audience='beginners',
            content_format='reels',
            objective='education',
            tone='conversational',
            count=3
        )
        self.assertEqual(len(ideas), 3)
        for item in ideas:
            self.assertIn('title', item)
            self.assertIn('hook', item)
            self.assertIn('outline', item)
            self.assertIn('caption_draft', item)
            self.assertIn('hashtags', item)
            self.assertIn('call_to_action', item)

    def test_save_generated_idea_and_detail(self):
        response = self.client.post(reverse('save_generated_idea'), {
            'title': '3 Skin Barrier Tips',
            'niche': 'skincare',
            'audience': 'beginners',
            'content_format': 'reels',
            'objective': 'education',
            'tone': 'conversational',
            'hook': 'Stop washing your face with hot water!',
            'caption_draft': 'Hot water strips your natural moisture barrier. Try lukewarm water.',
            'call_to_action': 'Save for your night routine!',
            'estimated_difficulty': 'Beginner friendly',
            'outline': '["0-3s hook", "3-15s demonstration"]',
            'hashtags': '["#Skincare", "#BarrierRepair"]',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContentIdea.objects.filter(user=self.user, title='3 Skin Barrier Tips').exists())
        idea = ContentIdea.objects.get(user=self.user, title='3 Skin Barrier Tips')

        # Detail view
        detail_res = self.client.get(reverse('idea_detail', args=[idea.id]))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, '3 Skin Barrier Tips')
        self.assertContains(detail_res, 'Stop washing your face with hot water!')

    def test_edit_and_favorite_and_delete_idea(self):
        idea = ContentIdea.objects.create(
            user=self.user,
            title='Initial Title',
            niche='fashion',
            audience='students',
            content_format='carousel',
            hook='Outfit test',
            caption_draft='Draft caption'
        )

        # Toggle favorite
        self.client.post(reverse('idea_toggle_favorite', args=[idea.id]))
        idea.refresh_from_db()
        self.assertTrue(idea.is_favorite)

        # Edit idea
        edit_res = self.client.post(reverse('idea_edit', args=[idea.id]), {
            'title': 'Updated Title',
            'niche': 'fashion',
            'audience': 'students',
            'content_format': 'carousel',
            'objective': 'engagement',
            'tone': 'conversational',
            'hook': 'Updated hook line',
            'outline_text': 'Slide 1\nSlide 2',
            'caption_draft': 'Updated caption draft',
            'hashtags_text': '#OOTD #StyleTips',
            'call_to_action': 'Drop a comment',
            'estimated_difficulty': 'Beginner',
            'is_favorite': True,
        })
        self.assertEqual(edit_res.status_code, 302)
        idea.refresh_from_db()
        self.assertEqual(idea.title, 'Updated Title')
        self.assertEqual(idea.hook, 'Updated hook line')
        self.assertEqual(idea.outline, ['Slide 1', 'Slide 2'])

        # Delete idea
        del_res = self.client.post(reverse('idea_delete', args=[idea.id]))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(ContentIdea.objects.filter(id=idea.id).exists())


# =============================================================================
# 5. Content Planner Test Suite
# =============================================================================
class PlannerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='planner_user', password='Password123!')
        self.client.login(username='planner_user', password='Password123!')

    def test_planner_create_edit_delete(self):
        # Create planner entry
        create_res = self.client.post(reverse('planner_create'), {
            'title': 'Test Scheduled Reel',
            'content_format': 'reels',
            'planned_date': str(date.today()),
            'status': 'planned',
            'notes': 'Filming on Saturday morning',
        })
        self.assertEqual(create_res.status_code, 302)
        self.assertTrue(PlannerEntry.objects.filter(user=self.user, title='Test Scheduled Reel').exists())
        entry = PlannerEntry.objects.get(user=self.user, title='Test Scheduled Reel')

        # Edit planner entry
        edit_res = self.client.post(reverse('planner_edit', args=[entry.id]), {
            'title': 'Updated Scheduled Reel',
            'content_format': 'reels',
            'planned_date': str(date.today()),
            'status': 'ready',
            'notes': 'Edited and ready to publish',
        })
        self.assertEqual(edit_res.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.status, 'ready')

        # Delete planner entry
        del_res = self.client.post(reverse('planner_delete', args=[entry.id]))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(PlannerEntry.objects.filter(id=entry.id).exists())


# =============================================================================
# 6. Caption & Hashtag Studio Test Suite
# =============================================================================
class CaptionStudioTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='studio_user', password='Password123!')
        self.client.login(username='studio_user', password='Password123!')

    def test_caption_generator_logic(self):
        results = generate_studio_caption(topic='Productivity Systems', niche='technology', audience='professionals')
        self.assertIn('story_caption', results)
        self.assertIn('list_caption', results)
        self.assertIn('convo_caption', results)
        self.assertIn('hashtags', results)
        self.assertTrue(len(results['hashtags']) > 0)

    def test_studio_page_post(self):
        res = self.client.post(reverse('caption_studio'), {
            'topic': 'Morning Routine Hacks',
            'niche': 'lifestyle',
            'audience': 'beginners',
            'tone': 'conversational',
            'style': 'story',
        })
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Morning Routine Hacks')
        self.assertContains(res, 'Editable Caption Canvas')


# =============================================================================
# 7. Media Library & File Validation Test Suite
# =============================================================================
class MediaLibraryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='media_user', password='Password123!')
        self.client.login(username='media_user', password='Password123!')

    def _generate_test_image(self):
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(file, 'jpeg')
        file.seek(0)
        return SimpleUploadedFile('test_photo.jpg', file.read(), content_type='image/jpeg')

    def test_media_upload_and_delete(self):
        test_img = self._generate_test_image()
        response = self.client.post(reverse('media_library'), {
            'title': 'Test Reference Photo',
            'image': test_img,
            'caption_notes': 'Blue aesthetic backdrop',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReferenceMedia.objects.filter(user=self.user, title='Test Reference Photo').exists())
        media = ReferenceMedia.objects.get(user=self.user, title='Test Reference Photo')
        self.assertTrue(media.file_size > 0)

        # Delete media
        del_res = self.client.post(reverse('media_delete', args=[media.id]))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(ReferenceMedia.objects.filter(id=media.id).exists())

    def test_media_upload_invalid_file(self):
        fake_file = SimpleUploadedFile('malicious.exe', b'bad executable content', content_type='application/octet-stream')
        response = self.client.post(reverse('media_library'), {
            'title': 'Invalid File Test',
            'image': fake_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ReferenceMedia.objects.filter(title='Invalid File Test').exists())


# =============================================================================
# 8. Data Isolation Security Test Suite
# =============================================================================
class UserDataIsolationTestCase(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()

        self.user1 = User.objects.create_user(username='user_alice', password='Password123!')
        self.user2 = User.objects.create_user(username='user_bob', password='Password123!')

        self.client1.login(username='user_alice', password='Password123!')
        self.client2.login(username='user_bob', password='Password123!')

        # Create idea for Alice
        self.alice_idea = ContentIdea.objects.create(
            user=self.user1,
            title='Alice Secret Campaign',
            hook='Exclusive hook',
            caption_draft='Confidential draft'
        )

        # Create planner entry for Alice
        self.alice_planner = PlannerEntry.objects.create(
            user=self.user1,
            title='Alice Scheduled Post',
            status='planned'
        )

    def test_bob_cannot_access_or_edit_alice_idea(self):
        # Bob tries to view Alice's idea
        response = self.client2.get(reverse('idea_detail', args=[self.alice_idea.id]))
        self.assertEqual(response.status_code, 404)

        # Bob tries to edit Alice's idea
        edit_res = self.client2.post(reverse('idea_edit', args=[self.alice_idea.id]), {
            'title': 'Hacked Title',
            'content_format': 'reels',
            'hook': 'Hacked hook',
            'caption_draft': 'Hacked caption',
        })
        self.assertEqual(edit_res.status_code, 404)
        self.alice_idea.refresh_from_db()
        self.assertEqual(self.alice_idea.title, 'Alice Secret Campaign')

    def test_bob_cannot_delete_alice_planner(self):
        # Bob tries to delete Alice's planner entry
        del_res = self.client2.post(reverse('planner_delete', args=[self.alice_planner.id]))
        self.assertEqual(del_res.status_code, 404)
        self.assertTrue(PlannerEntry.objects.filter(id=self.alice_planner.id).exists())

    def test_bob_cannot_delete_alice_media(self):
        # Create media for Alice
        file = io.BytesIO()
        img = Image.new('RGB', (50, 50), color='red')
        img.save(file, 'jpeg')
        file.seek(0)
        alice_img = SimpleUploadedFile('alice_private.jpg', file.read(), content_type='image/jpeg')

        alice_media = ReferenceMedia.objects.create(
            user=self.user1,
            title='Alice Private Media',
            image=alice_img,
            file_size=len(alice_img)
        )

        # Bob tries to delete Alice's media item
        del_res = self.client2.post(reverse('media_delete', args=[alice_media.id]))
        self.assertEqual(del_res.status_code, 404)
        self.assertTrue(ReferenceMedia.objects.filter(id=alice_media.id).exists())

    def test_dashboard_metrics_are_strictly_isolated(self):
        # Alice's dashboard shows 1 idea and 1 planner entry
        alice_dash = self.client1.get(reverse('dashboard'))
        self.assertEqual(alice_dash.context['stats']['total_ideas'], 1)
        self.assertEqual(alice_dash.context['stats']['planned_posts'], 1)

        # Bob's dashboard shows 0 ideas and 0 planner entries
        bob_dash = self.client2.get(reverse('dashboard'))
        self.assertEqual(bob_dash.context['stats']['total_ideas'], 0)
        self.assertEqual(bob_dash.context['stats']['planned_posts'], 0)

