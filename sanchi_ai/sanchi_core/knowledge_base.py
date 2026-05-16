"""
Sanchi's Extended Knowledge Base
Provides structured knowledge for offline/enhanced responses.
"""


class KnowledgeBase:
    """Structured knowledge for Sanchi's domains of expertise."""

    DARK_PSYCHOLOGY = {
        "manipulation_tactics": {
            "gaslighting": {
                "definition": "Making someone question their own reality and memory",
                "signs": [
                    "They deny things you know happened",
                    "They trivialize your feelings",
                    "They shift blame to you",
                    "You constantly second-guess yourself",
                ],
                "defense": [
                    "Document interactions",
                    "Trust your gut instincts",
                    "Seek outside perspectives",
                    "Set firm boundaries",
                ],
            },
            "love_bombing": {
                "definition": "Overwhelming someone with attention and "
                "affection to gain control",
                "signs": [
                    "Excessive flattery early on",
                    "Rushing intimacy",
                    "Constant contact and attention",
                    "Grand gestures that feel too fast",
                ],
                "defense": [
                    "Pace the relationship",
                    "Watch for consistency over time",
                    "Don't ignore red flags because of gifts",
                ],
            },
            "silent_treatment": {
                "definition": "Using silence as punishment to control behavior",
                "signs": [
                    "Withdrawal after disagreement",
                    "Ignoring you completely",
                    "Making you desperate to fix things",
                ],
                "defense": [
                    "Don't chase - maintain your peace",
                    "Communicate your boundaries",
                    "Recognize it as manipulation, not maturity",
                ],
            },
        },
        "persuasion_principles": {
            "reciprocity": "People feel obligated to return favors",
            "scarcity": "People value what's limited or rare",
            "authority": "People trust and follow perceived experts",
            "consistency": "People want to be consistent with past commitments",
            "liking": "People are persuaded by those they like",
            "social_proof": "People follow what others are doing",
            "unity": "People are influenced by shared identity",
        },
    }

    BUSINESS_STRATEGY = {
        "startup_framework": [
            "Problem Identification - What pain are you solving?",
            "Customer Validation - Talk to 50+ potential customers",
            "MVP Development - Build the simplest version that works",
            "Metrics & Iteration - Measure, learn, improve",
            "Scaling - Only scale what's proven to work",
        ],
        "pricing_psychology": {
            "anchoring": "Show expensive option first",
            "charm_pricing": "Use .99 endings",
            "decoy_effect": "Add a less attractive option to push preference",
            "bundle_pricing": "Combine products for perceived value",
            "price_framing": "Compare to daily cost of coffee",
        },
        "negotiation_tactics": [
            "Never negotiate against yourself",
            "Let the other party make the first offer when possible",
            "Use silence as a tool",
            "Always have a BATNA (Best Alternative)",
            "Focus on interests, not positions",
            "The person who cares less has more power",
        ],
    }

    PERSONALITY_DEVELOPMENT = {
        "confidence_building": [
            "Track 3 wins every day - no matter how small",
            "Adopt power poses before important situations",
            "Set and achieve micro-goals consistently",
            "Face one fear per week - systematic desensitization",
            "Stop apologizing for existing - replace 'sorry' with 'thank you'",
        ],
        "emotional_intelligence": {
            "self_awareness": "Know your emotional triggers",
            "self_regulation": "Respond, don't react",
            "motivation": "Connect daily actions to deeper purpose",
            "empathy": "Listen to understand, not to reply",
            "social_skills": "Read the room and adapt",
        },
        "communication_mastery": [
            "Listen 80%, speak 20%",
            "Mirror body language to build rapport",
            "Use people's names - it's powerful",
            "Ask questions that make people think",
            "Master the pause - silence is powerful",
            "Tell stories, not just facts",
        ],
        "body_language_hacks": {
            "confidence": "Open posture, steady eye contact, slow movements",
            "trust": "Visible palms, slight head tilt, genuine smile",
            "dominance": "Wide stance, less blinking, lower vocal pitch",
            "deception_signs": (
                "Face touching, inconsistent micro-expressions, "
                "overly rehearsed delivery"
            ),
        },
    }

    @classmethod
    def get_topic_info(cls, category: str, topic: str) -> str:
        """Retrieve structured information about a topic."""
        categories = {
            "dark_psychology": cls.DARK_PSYCHOLOGY,
            "business": cls.BUSINESS_STRATEGY,
            "personality": cls.PERSONALITY_DEVELOPMENT,
        }

        cat_data = categories.get(category, {})
        return str(cat_data.get(topic, "Topic not found in knowledge base"))

    @classmethod
    def get_all_topics(cls) -> list:
        """Get all available topics."""
        topics = []
        topics.extend(
            [f"dark_psychology/{k}" for k in cls.DARK_PSYCHOLOGY.keys()]
        )
        topics.extend(
            [f"business/{k}" for k in cls.BUSINESS_STRATEGY.keys()]
        )
        topics.extend(
            [f"personality/{k}" for k in cls.PERSONALITY_DEVELOPMENT.keys()]
        )
        return topics