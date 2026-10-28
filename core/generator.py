"""
CreatorSpark — Transparent Rule-Based Content Idea Generation Engine
Provides structured, deterministic, and highly varied content suggestions
for Instagram creators without paid external AI or Instagram API dependencies.
"""

import json
import random
from typing import List, Dict, Any


# -----------------------------------------------------------------------------
# Niche Knowledge Bases
# -----------------------------------------------------------------------------
NICHE_TOPICS = {
    'beauty': {
        'default_topic': 'Long-lasting Makeup Application',
        'subtopics': ['Base prep for oily vs dry skin', 'No-foundation makeup routine', 'Drugstore vs luxury comparisons', 'Brush cleaning hygiene', 'Cream vs powder blush'],
        'pain_points': ['Cakey foundation after 2 hours', 'Uneven eyeliner wings', 'Makeup separating around the nose', 'Wasting money on viral products that don’t work'],
        'hashtags': ['#BeautyTips', '#MakeupRoutine', '#GlowMakeup', '#DrugstoreBeauty', '#MakeupHacks', '#BeautyCommunity', '#EverydayMakeup'],
    },
    'skincare': {
        'default_topic': 'Barrier Repair and Layering',
        'subtopics': ['AM vs PM active ingredients layering', 'Sunscreen myths and white-cast fixes', 'Double cleansing without irritation', 'Acne spot treatment dos and don’ts', 'Exfoliation schedule'],
        'pain_points': ['Damaged skin barrier burning', 'Pores looking enlarged', 'Dry patches under foundation', 'Conflicting ingredient combinations'],
        'hashtags': ['#SkincareEducation', '#SkinBarrierRepair', '#HealthySkinTips', '#DermTok', '#SkincareRoutine', '#GlowUpDaily', '#SkincareCommunity'],
    },
    'fashion': {
        'default_topic': 'Capsule Wardrobe Styling',
        'subtopics': ['1 shirt styled 4 different ways', 'Thrifting secrets and fabric checks', 'Color palette coordination', 'Elevating basic outfits with accessories', 'Flattering silhouettes'],
        'pain_points': ['A closet full of clothes with nothing to wear', 'Fast fashion falling apart after one wash', 'Feeling underdressed at events', 'Buying pieces that don’t match anything'],
        'hashtags': ['#OutfitInspo', '#CapsuleWardrobe', '#StyleHacks', '#StreetwearStyle', '#OOTDInspo', '#FashionCreator', '#ThriftedStyle'],
    },
    'fitness': {
        'default_topic': 'Efficient Strength Training',
        'subtopics': ['Squat and deadlift form fixes', 'Progressive overload tracking', 'Pre-workout nutrition timing', 'Quick 20-minute home workouts', 'Ankle and hip mobility drills'],
        'pain_points': ['Gym intimidation and not knowing what to do', 'Lifting heavy but seeing no progress', 'Knee or lower back ache after workouts', 'Inconsistent routine motivation'],
        'hashtags': ['#FitnessTips', '#GymFormCheck', '#StrengthTraining', '#WorkoutMotivation', '#LegDayRoutine', '#HealthyHabits', '#FitnessJourney'],
    },
    'food': {
        'default_topic': 'High-Protein Quick Meals',
        'subtopics': ['15-minute sheet pan dinners', 'Healthy lunchbox meal preps', 'Budget-friendly pantry staples', 'Restaurant-style knife skills', 'Single-serve guilt-free desserts'],
        'pain_points': ['Spending too much money on food delivery', 'Boring repetitive chicken and rice', 'Spending hours washing dishes', 'Ingredients spoiling in the fridge'],
        'hashtags': ['#QuickRecipes', '#MealPrepIdeas', '#HighProteinMeals', '#HomeCooking', '#FoodTok', '#EasyDinnerIdeas', '#HealthyEating'],
    },
    'travel': {
        'default_topic': 'Budget Travel Hacks',
        'subtopics': ['Carry-on packing for 10-day trips', 'Hidden gem destinations off the beaten path', 'Flight booking discount windows', 'Solo traveler safety rules', 'Local street food tours'],
        'pain_points': ['Airport baggage surprise fees', 'Tourist trap overpricing', 'Overcrowded destinations with ruined photos', 'Fear of solo travel logistics'],
        'hashtags': ['#TravelTips', '#BudgetTravel', '#HiddenGems', '#SoloTraveler', '#TravelHacks', '#BucketListTravel', '#WanderlustVibes'],
    },
    'technology': {
        'default_topic': 'Productivity Workflow & Desk Setup',
        'subtopics': ['Essential keyboard shortcuts for creators', 'Hidden smartphone battery-saving settings', 'Free AI productivity tools', 'Audio setup under $100', 'File backup & cloud safety'],
        'pain_points': ['Storage full warnings at the worst time', 'Slow computer lag during edits', 'Distracting notification fatigue', 'Overpaying for software subscriptions'],
        'hashtags': ['#TechHacks', '#ProductivityTools', '#DeskSetup', '#iPhoneTips', '#AndroidHacks', '#CreatorGear', '#TechEducation'],
    },
    'education': {
        'default_topic': 'Active Recall Study Methods',
        'subtopics': ['The Pomodoro method vs flow state', 'How to read 1 non-fiction book a week', 'Notion workspace organization', 'Public speaking without nervousness', 'Language learning immersion'],
        'pain_points': ['Procrastination until the night before', 'Reading 20 pages and remembering nothing', 'Mental burnout and brain fog', 'Overwhelmed by messy notes'],
        'hashtags': ['#StudyTips', '#StudyWithMe', '#ProductivityHacks', '#SelfImprovement', '#LearningEveryday', '#BookTok', '#StudentLife'],
    },
    'finance': {
        'default_topic': 'Simple Personal Budgeting',
        'subtopics': ['The 50/30/20 budget breakdown', 'High-yield savings accounts explained', 'Index funds vs individual stocks for beginners', 'Building good credit from scratch', 'Cutting impulse shopping'],
        'pain_points': ['Paycheck disappearing by the second week', 'Intimidated by complex stock market jargon', 'High credit card interest rates', 'No emergency fund cushion'],
        'hashtags': ['#PersonalFinance', '#MoneyTips', '#InvestingForBeginners', '#BudgetingHacks', '#FinTok', '#FinancialFreedom', '#MoneyMindset'],
    },
    'lifestyle': {
        'default_topic': 'Morning Routine & Reset Habits',
        'subtopics': ['Sunday reset checklist for a stress-free week', 'Digital detox before bedtime', 'Time blocking for busy schedules', 'Creating a cozy sanctuary space', 'Habit stacking for consistency'],
        'pain_points': ['Waking up tired and rushing to start the day', 'Endless doomscrolling in bed', 'Feeling like 24 hours isn’t enough', 'Setting goals and giving up after day 4'],
        'hashtags': ['#SundayReset', '#MorningRoutine', '#HealthyHabits', '#DailyRoutine', '#SlowLiving', '#ProductiveDay', '#MindfulLiving'],
    },
}

# -----------------------------------------------------------------------------
# Audience Addressing Modifiers
# -----------------------------------------------------------------------------
AUDIENCE_CONTEXT = {
    'beginners': {
        'prefix': 'If you’re a complete beginner',
        'label': 'Beginner Friendly',
        'voice': 'Clear, jargon-free, and step-by-step',
        'audience_tag': '#BeginnerFriendly',
    },
    'students': {
        'prefix': 'If you’re a student balancing classes',
        'label': 'Student Focused',
        'voice': 'Affordable, time-efficient, and practical',
        'audience_tag': '#StudentLife',
    },
    'professionals': {
        'prefix': 'If you’re a busy working professional',
        'label': 'Career & Pro',
        'voice': 'High-yield, direct, and zero fluff',
        'audience_tag': '#CareerAdvice',
    },
    'enthusiasts': {
        'prefix': 'If you want to take your craft to the next level',
        'label': 'Advanced Enthusiast',
        'voice': 'Detailed, analytical, and nuance-driven',
        'audience_tag': '#LevelUp',
    },
    'custom': {
        'prefix': 'For your dedicated community',
        'label': 'Community Custom',
        'voice': 'Personalized and authentic',
        'audience_tag': '#CreatorCommunity',
    },
}

# -----------------------------------------------------------------------------
# Goal-Driven Calls to Action (CTAs)
# -----------------------------------------------------------------------------
GOAL_CTAS = {
    'engagement': [
        'Which of these do you do right now? Drop a comment below!',
        'Agree or disagree? Let’s debate in the comments! 👇',
        'Drop a “🔥” in the comments if you want Part 2 tomorrow!',
        'Tag a friend who desperately needs to see this today.',
    ],
    'education': [
        'Save this post so you have the cheat sheet ready when you need it! 📌',
        'Tap the bookmark icon to review this before your next session.',
        'Screenshot this slide so you never forget the order!',
        'Save this and share it with someone learning this skill.',
    ],
    'community': [
        'Be honest: what’s your biggest struggle with this? I’ll reply to every comment.',
        'Share your own favorite hack in the comments to help our community!',
        'DM me the word “SPARK” and let’s connect directly.',
        'Which one are you going to try first? Let’s hold each other accountable.',
    ],
    'awareness': [
        'Tap the link in my bio to explore the full guide & resources!',
        'Check the link in bio for the complete checklist and toolkit.',
        'Head to my profile link to grab the free downloadable template.',
        'Follow for daily breakdowns and updates on this topic.',
    ],
    'personal_brand': [
        'Follow @{handle} for honest, daily breakdowns you won’t hear from gurus.',
        'I test and break down these strategies weekly — follow along for more!',
        'Hit follow to join 10k+ creators leveling up without the fluff.',
        'Follow for the unfiltered truth on modern social creation.',
    ],
}

# -----------------------------------------------------------------------------
# Format Sequence Builders
# -----------------------------------------------------------------------------
def build_reels_outline(topic: str, pain: str, solution: str) -> List[str]:
    return [
        f"0-3s Hook: Visual pattern interrupt pointing to camera with on-screen text: '{pain}?'",
        f"3-8s Problem: Demonstrate the mistake with exaggerated body language or side-by-side clip.",
        f"8-18s Solution: Clear 3-step breakdown of how to solve it using {solution}.",
        "18-25s Closing & CTA: Show the polished end-result with arrow pointing down to save/comment.",
    ]

def build_carousel_outline(topic: str, pain: str, solution: str) -> List[str]:
    return [
        f"Slide 1 (Cover): Bold high-contrast headline: 'Stop making this mistake with {topic}'.",
        f"Slide 2 (The Trap): Explain why 90% of people struggle with {pain}.",
        f"Slide 3 (The Mindset Shift): Reframe the issue and introduce {solution}.",
        f"Slide 4 (Actionable Steps): Bulleted 3-part blueprint ready to implement today.",
        "Slide 5 (Summary & CTA): Cheat-sheet recap graphic + 'Save this post for later' prompt.",
    ]

def build_stories_outline(topic: str, pain: str, solution: str) -> List[str]:
    return [
        f"Story 1: Interactive Poll Sticker: 'Do you ever struggle with {pain}?' (Yes / Everyday).",
        f"Story 2: Candid behind-the-scenes selfie video explaining why most advice is wrong.",
        f"Story 3: Quick photo demonstration / screenshot of the {solution} in action.",
        "Story 4: Question Box Sticker: 'Ask me anything about this or drop your biggest hurdle'.",
    ]

def build_static_outline(topic: str, pain: str, solution: str) -> List[str]:
    return [
        f"Visual Focal Point: High-resolution aesthetic shot, quote graphic, or clean diagram of {topic}.",
        "Caption First Line: Intriguing one-line summary acting as the visual anchor.",
        f"Caption Body: 3-paragraph microblog breaking down the nuances of {solution}.",
        "Final Paragraph: Engaging question prompting thoughtful long-form comments.",
    ]

def build_series_outline(topic: str, pain: str, solution: str) -> List[str]:
    return [
        f"Part 1: The Diagnosis — Unpacking why {pain} is sabotaging your results.",
        f"Part 2: The Framework — Step-by-step masterclass on {solution}.",
        "Part 3: The Routine — Creating a sustainable daily/weekly workflow for long-term consistency.",
    ]


# -----------------------------------------------------------------------------
# Main Rule-Based Generator Function
# -----------------------------------------------------------------------------
def generate_content_ideas(
    niche: str = 'lifestyle',
    audience: str = 'beginners',
    content_format: str = 'reels',
    objective: str = 'engagement',
    tone: str = 'conversational',
    keywords: str = '',
    count: int = 3,
    user_handle: str = 'creatorspark'
) -> List[Dict[str, Any]]:
    """
    Generates a list of distinct, actionable content ideas based on combinatorial
    rules, niche knowledge, format structures, audience nuances, and user goals.
    """
    clean_niche = niche.lower().strip() if niche else 'lifestyle'
    niche_info = NICHE_TOPICS.get(clean_niche)

    # Fallback to lifestyle if custom niche has no pre-canned data
    if not niche_info:
        base_topic = keywords.strip() if keywords else clean_niche.capitalize()
        niche_info = {
            'default_topic': base_topic,
            'subtopics': [f'{base_topic} essentials', f'Common mistakes in {base_topic}', f'Best practices for {base_topic}'],
            'pain_points': [f'Getting overwhelmed starting with {base_topic}', f'Wasting time on inefficient {base_topic} methods'],
            'hashtags': [f'#{clean_niche.replace(" ", "")}', f'#{clean_niche.replace(" ", "")}Tips', '#CreatorStudio', '#ContentPlanning'],
        }

    audience_data = AUDIENCE_CONTEXT.get(audience, AUDIENCE_CONTEXT['beginners'])
    effective_topic = keywords.strip() if keywords else niche_info['default_topic']

    ctas = GOAL_CTAS.get(objective, GOAL_CTAS['engagement'])
    clean_handle = user_handle.lstrip('@') if user_handle else 'creator'

    # 4 Core Angle Archetypes to ensure meaningful variety
    angles = [
        {
            'title_template': '3 {topic} Mistakes You’re Making (And How to Fix Them)',
            'hook_template': '“If your {topic} feels frustrating, stop doing this immediately.”',
            'pain_index': 0,
            'difficulty': 'Beginner (15-20 min setup)',
            'caption_starter': f'We have all been there. When you start out with {effective_topic}, it is easy to pick up bad habits that slow you down.',
        },
        {
            'title_template': 'The Beginner’s Cheat Sheet to {topic} in 60 Seconds',
            'hook_template': '“Save this before you spend another dollar on {topic}.”',
            'pain_index': 1 % len(niche_info['pain_points']),
            'difficulty': 'Quick & Easy (10 min record)',
            'caption_starter': f'You don’t need an overly complicated strategy for {effective_topic}. Here is the exact blueprint I wish I had on day one.',
        },
        {
            'title_template': 'What Nobody Tells You About {topic}',
            'hook_template': '“Here’s the unfiltered truth about {topic} that most people ignore.”',
            'pain_index': min(2, len(niche_info['pain_points']) - 1),
            'difficulty': 'Intermediate (Talking head + b-roll)',
            'caption_starter': f'Let’s be honest for a second. The standard advice about {effective_topic} doesn’t always work for real people with busy lives.',
        },
        {
            'title_template': 'If I Had to Master {topic} From Scratch, Here’s My Day 1 Plan',
            'hook_template': '“Starting over in {topic}? Here are the only 3 steps you actually need.”',
            'pain_index': 0,
            'difficulty': 'Beginner friendly',
            'caption_starter': f'{audience_data["prefix"]}, tackling {effective_topic} can feel like drinking from a firehose. Let’s simplify it completely.',
        },
    ]

    results = []
    # Build ideas up to the requested count
    for i in range(min(count, len(angles))):
        angle = angles[i]
        pain_point = niche_info['pain_points'][angle['pain_index']]
        subtopic = niche_info['subtopics'][i % len(niche_info['subtopics'])]

        title = angle['title_template'].format(topic=effective_topic)
        hook = angle['hook_template'].format(topic=effective_topic)

        # Build format-specific outline
        if content_format == 'reels':
            outline = build_reels_outline(effective_topic, pain_point, subtopic)
        elif content_format == 'carousel':
            outline = build_carousel_outline(effective_topic, pain_point, subtopic)
        elif content_format == 'stories':
            outline = build_stories_outline(effective_topic, pain_point, subtopic)
        elif content_format == 'educational_series':
            outline = build_series_outline(effective_topic, pain_point, subtopic)
        else:
            outline = build_static_outline(effective_topic, pain_point, subtopic)

        # Select CTA
        cta_text = ctas[i % len(ctas)].replace('{handle}', clean_handle)

        # Assemble Caption Draft
        caption_lines = [
            f"{hook}",
            "",
            angle['caption_starter'],
            "",
            f"Here is what works best:",
            f"1️⃣ Identify where {pain_point} is tripping you up.",
            f"2️⃣ Shift focus toward {subtopic}.",
            f"3️⃣ Build consistency for 7 days before judging results.",
            "",
            f"{cta_text}",
        ]
        caption_draft = "\n".join(caption_lines)

        # Curate Hashtags
        curated_tags = list(niche_info['hashtags'][:5])
        curated_tags.append(audience_data['audience_tag'])
        if keywords:
            clean_kw = '#' + ''.join(c for c in keywords if c.isalnum())
            if clean_kw != '#':
                curated_tags.insert(0, clean_kw)
        curated_tags.extend(['#CreatorSpark', '#InstagramGrowth', '#ContentStrategy'])

        results.append({
            'title': title,
            'hook': hook,
            'outline': outline,
            'outline_json': json.dumps(outline),
            'caption_draft': caption_draft,
            'hashtags': curated_tags[:8],
            'hashtags_json': json.dumps(curated_tags[:8]),
            'call_to_action': cta_text,
            'content_format': content_format,
            'estimated_difficulty': angle['difficulty'],
            'niche': clean_niche,
            'audience': audience,
            'objective': objective,
            'tone': tone,
        })

    return results


# -----------------------------------------------------------------------------
# Caption & Hashtag Studio Generator Helper
# -----------------------------------------------------------------------------
def generate_studio_caption(
    topic: str,
    niche: str = 'lifestyle',
    audience: str = 'beginners',
    tone: str = 'conversational',
    style: str = 'story'
) -> Dict[str, Any]:
    """
    Generates refined, distinct caption variations and tiered hashtags
    for the Caption and Hashtag Studio.
    """
    clean_topic = topic.strip() if topic else 'Consistency in Creation'
    clean_niche = niche.lower() if niche else 'lifestyle'
    niche_info = NICHE_TOPICS.get(clean_niche, NICHE_TOPICS['lifestyle'])

    # Style 1: Relatable Storytelling
    story_caption = (
        f"A few months ago, I made a huge mistake with {clean_topic} that cost me hours of wasted effort.\n\n"
        f"I thought that more effort automatically meant better results. But here is the hard truth: "
        f"without a clear framework, you're just running on a hamster wheel.\n\n"
        f"Once I shifted my approach to focus on simplicity and consistency, everything unlocked.\n\n"
        f"If you're currently navigating this: be patient with your progress. The breakthrough happens right after the frustration.\n\n"
        f"Have you experienced this too? Let me know below! 👇"
    )

    # Style 2: Quick Value / Actionable Listicle
    list_caption = (
        f"3 quick rules for {clean_topic} you will wish you knew sooner:\n\n"
        f"1. Focus on the core foundation before obsessing over tiny aesthetic details.\n"
        f"2. Audit what your audience actually saves and shares — not just what they passively view.\n"
        f"3. 80% finished and published always beats 100% perfect in your drafts folder.\n\n"
        f"Bookmark this cheat sheet so it’s handy when you plan your next post! 📌"
    )

    # Style 3: Engaging Conversation Starter
    convo_caption = (
        f"Unpopular opinion about {clean_topic}:\n\n"
        f"Most people overcomplicate the process because they are comparing their Day 1 to someone else’s Year 5.\n\n"
        f"You don't need a huge budget or fancy equipment. You just need a genuine point of view and a willingness to show up consistently.\n\n"
        f"What’s your current take? Drop your thoughts in the comments — I’m replying to everyone today! 💬"
    )

    # Hashtags tiered into Broad, Niche, and Community
    broad_tags = ['#ContentCreator', '#InstagramTips', '#SocialMediaStrategy', '#CreativeProcess']
    niche_tags = list(niche_info['hashtags'][:4])
    kw_tag = '#' + ''.join(c for c in clean_topic if c.isalnum())
    community_tags = [kw_tag, '#CreatorCommunity', '#BuildInPublic']

    all_tags = [t for t in (niche_tags + broad_tags + community_tags) if len(t) > 2]

    return {
        'topic': clean_topic,
        'story_caption': story_caption,
        'list_caption': list_caption,
        'convo_caption': convo_caption,
        'hashtags': all_tags,
        'hashtags_json': json.dumps(all_tags),
        'hashtags_string': ' '.join(all_tags),
    }
