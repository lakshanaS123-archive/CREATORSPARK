"""
Context processors for CreatorSpark.
Provides global template variables across all views.
"""

def creatorspark_context(request):
    return {
        'APP_NAME': 'CreatorSpark',
        'APP_TAGLINE': 'Content Idea Generation & Planning Studio for Instagram Creators',
        'APP_VERSION': '1.0.0',
        'CURRENT_STAGE': 2,
        'TOTAL_STAGES': 5,
        'STAGE_NAME': 'Core Platform & Studio Features Complete',
    }
