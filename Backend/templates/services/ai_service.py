"""
MAZINGIRA MIND - AI SERVICE MODULE
Hugging Face integration for mental health AI responses
"""

import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime
import re
import random

logger = logging.getLogger(__name__)

class MentalHealthAI:
    """
    AI SERVICE CLASS
    Handles all AI-related functionality using Hugging Face models
    """
    
    def __init__(self):
        """Initialize AI models"""
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """
        LOAD HUGGING FACE MODELS
        Loads pre-trained models for mental health analysis
        """
        try:
            logger.info("Loading AI models...")
            
            # 1. SENTIMENT ANALYSIS MODEL
            # For analyzing user emotional state
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # Use CPU (-1) or GPU (0)
            )
            
            # 2. TEXT CLASSIFICATION FOR MENTAL HEALTH
            # For detecting mental health conditions
            try:
                self.mental_health_classifier = pipeline(
                    "text-classification",
                    model="mental/mental-bert-base-uncased"
                )
            except:
                # Fallback if specialized model unavailable
                logger.warning("Specialized mental health model unavailable, using general classification")
                self.mental_health_classifier = None
            
            # 3. TEXT GENERATION FOR RESPONSES
            # For generating empathetic responses
            try:
                self.text_generator = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-small",
                    max_length=100,
                    do_sample=True,
                    temperature=0.7
                )
            except:
                logger.warning("Text generation model unavailable, using template responses")
                self.text_generator = None
            
            self.models_loaded = True
            logger.info("✅ AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load AI models: {e}")
            self.models_loaded = False
            # Continue with rule-based responses
    
    def process_chat_message(self, user_message, user_id):
        """
        MAIN AI PROCESSING METHOD
        Analyzes user message and generates appropriate response
        """
        try:
            # 1. CRISIS DETECTION (highest priority)
            crisis_result = self.detect_crisis(user_message)
            if crisis_result['is_crisis']:
                return crisis_result
            
            # 2. SENTIMENT ANALYSIS
            sentiment = self.analyze_sentiment(user_message)
            
            # 3. MENTAL STATE CLASSIFICATION
            mental_state = self.classify_mental_state(user_message)
            
            # 4. GENERATE CULTURALLY-APPROPRIATE RESPONSE
            ai_response = self.generate_response(user_message, sentiment, mental_state)
            
            # 5. ADD FOLLOW-UP SUGGESTIONS
            suggestions = self.generate_suggestions(user_message, sentiment)
            
            return {
                'message': ai_response,
                'is_crisis': False,
                'sentiment': sentiment,
                'mental_state': mental_state,
                'suggestions': suggestions,
                'confidence': self.calculate_confidence(user_message),
                'response_type': 'ai_generated' if self.models_loaded else 'template'
            }
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return self.fallback_response(user_message)
    
    def detect_crisis(self, message):
        """
        CRISIS DETECTION SYSTEM
        Identifies potential self-harm or emergency situations
        """
        try:
            # Define crisis keywords and phrases
            crisis_indicators = {
                'high_risk': [
                    'kill myself', 'end my life', 'suicide', 'better off dead',
                    'no point living', 'want to die', 'end it all'
                ],
                'medium_risk': [
                    'hurt myself', 'self harm', 'cut myself', 'overdose',
                    'can\'t go on', 'give up', 'hopeless'
                ],
                'contextual': [
                    'pills', 'rope', 'bridge', 'jump', 'knife'
                ]
            }
            
            lower_message = message.lower()
            crisis_score = 0
            detected_keywords = []
            
            # Check for direct crisis language
            for keyword in crisis_indicators['high_risk']:
                if keyword in lower_message:
                    crisis_score += 1.0
                    detected_keywords.append(keyword)
            
            for keyword in crisis_indicators['medium_risk']:
                if keyword in lower_message:
                    crisis_score += 0.7
                    detected_keywords.append(keyword)
            
            for keyword in crisis_indicators['contextual']:
                if keyword in lower_message and crisis_score > 0:
                    crisis_score += 0.3
                    detected_keywords.append(keyword)
            
            # Use AI model for subtle crisis detection if available
            if self.mental_health_classifier and crisis_score > 0:
                try:
                    classification = self.mental_health_classifier(message)
                    if isinstance(classification, list) and len(classification) > 0:
                        top_prediction = classification[0]
                        if 'severe' in top_prediction.get('label', '').lower():
                            crisis_score += 0.5
                except Exception as e:
                    logger.warning(f"Mental health classification failed: {e}")
            
            # Crisis threshold
            if crisis_score >= 0.7:
                return {
                    'message': self.get_crisis_response(crisis_score),
                    'is_crisis': True,
                    'crisis_level': 'high' if crisis_score >= 1.0 else 'moderate',
                    'detected_keywords': detected_keywords,
                    'emergency_contacts': self.get_kenyan_crisis_contacts(),
                    'immediate_actions': self.get_immediate_crisis_actions(),
                    'suggestions': ['Get immediate help', 'Contact emergency services', 'Reach out to family']
                }
            
            return {'is_crisis': False}
            
        except Exception as e:
            logger.error(f"Crisis detection error: {e}")
            return {'is_crisis': False}
    
    def get_crisis_response(self, crisis_score):
        """Generate appropriate crisis response based on severity"""
        if crisis_score >= 1.0:
            return """I'm very concerned about what you've shared. Please reach out for immediate help right now:

🚨 EMERGENCY CONTACTS:
• Kenya Red Cross Crisis Line: 1199
• Emergency Services: 999
• Befrienders Kenya: +254 722 178 177

You don't have to go through this alone. Professional help is available 24/7. Please contact one of these services immediately or go to the nearest hospital emergency room.

Your life has value, and there are people who want to help you through this difficult time."""
        
        else:
            return """I'm worried about you based on what you've shared. It sounds like you're going through a really difficult time, and I want you to know that help is available.

Please consider reaching out to:
• Kenya Red Cross Counseling: 1199
• Befrienders Kenya: +254 722 178 177
• Or speak with a trusted family member or friend

You don't have to handle this alone. These feelings can be temporary, even when they feel overwhelming. Would you like me to help you find professional support in your area?"""
    
    def get_kenyan_crisis_contacts(self):
        """Return Kenyan crisis contact information"""
        return [
            {
                'name': 'Kenya Red Cross Crisis Line',
                'number': '1199',
                'availability': '24/7',
                'type': 'Crisis counseling'
            },
            {
                'name': 'Emergency Services',
                'number': '999',
                'availability': '24/7',
                'type': 'Emergency medical response'
            },
            {
                'name': 'Befrienders Kenya',
                'number': '+254 722 178 177',
                'availability': '3PM - 9PM daily',
                'type': 'Emotional support'
            },
            {
                'name': 'Kenyatta National Hospital Emergency',
                'number': '+254 20 2726300',
                'availability': '24/7',
                'type': 'Emergency psychiatric services'
            }
        ]
    
    def get_immediate_crisis_actions(self):
        """Return immediate actions for crisis situations"""
        return [
            "Call one of the crisis hotlines immediately",
            "Go to the nearest hospital emergency room",
            "Remove any means of self-harm from your immediate area",
            "Contact a trusted family member or friend right now",
            "Stay with someone until you can get professional help",
            "Remember: This crisis is temporary, help is available"
        ]
    
    def analyze_sentiment(self, message):
        """
        SENTIMENT ANALYSIS
        Analyzes emotional tone of user message
        """
        try:
            if self.models_loaded and self.sentiment_analyzer:
                result = self.sentiment_analyzer(message)
                if isinstance(result, list) and len(result) > 0:
                    sentiment = result[0]
                    return {
                        'label': sentiment.get('label', 'NEUTRAL'),
                        'score': sentiment.get('score', 0.5),
                        'confidence': 'high' if sentiment.get('score', 0) > 0.8 else 'medium'
                    }
            
            # Fallback sentiment analysis using keywords
            return self.keyword_based_sentiment(message)
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'label': 'NEUTRAL', 'score': 0.5, 'confidence': 'low'}
    
    def keyword_based_sentiment(self, message):
        """Fallback sentiment analysis using keyword matching"""
        positive_words = ['good', 'great', 'happy', 'better', 'hope', 'grateful', 'blessed', 'joy']
        negative_words = ['sad', 'depressed', 'anxious', 'worried', 'stressed', 'angry', 'frustrated', 'hopeless']
        
        lower_message = message.lower()
        positive_count = sum(1 for word in positive_words if word in lower_message)
        negative_count = sum(1 for word in negative_words if word in lower_message)
        
        if positive_count > negative_count:
            return {'label': 'POSITIVE', 'score': 0.7, 'confidence': 'medium'}
        elif negative_count > positive_count:
            return {'label': 'NEGATIVE', 'score': 0.7, 'confidence': 'medium'}
        else:
            return {'label': 'NEUTRAL', 'score': 0.5, 'confidence': 'low'}
    
    def classify_mental_state(self, message):
        """
        MENTAL STATE CLASSIFICATION
        Identifies potential mental health concerns
        """
        try:
            if self.mental_health_classifier:
                result = self.mental_health_classifier(message)
                if isinstance(result, list) and len(result) > 0:
                    classification = result[0]
                    return {
                        'category': classification.get('label', 'general'),
                        'confidence': classification.get('score', 0.5)
                    }
            
            # Fallback classification using keywords
            return self.keyword_based_classification(message)
            
        except Exception as e:
            logger.error(f"Mental state classification error: {e}")
            return {'category': 'general', 'confidence': 0.5}
    
    def keyword_based_classification(self, message):
        """Fallback mental health classification"""
        categories = {
            'anxiety': ['anxious', 'worried', 'panic', 'nervous', 'fear', 'scared'],
            'depression': ['sad', 'depressed', 'hopeless', 'empty', 'worthless'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted'],
            'trauma': ['trauma', 'flashback', 'nightmare', 'abuse', 'assault'],
            'relationships': ['family', 'marriage', 'spouse', 'relationship', 'partner'],
            'financial': ['money', 'job', 'work', 'financial', 'bills', 'debt']
        }
        
        lower_message = message.lower()
        
        for category, keywords in categories.items():
            if any(keyword in lower_message for keyword in keywords):
                return {'category': category, 'confidence': 0.7}
        
        return {'category': 'general', 'confidence': 0.5}
    
    def generate_response(self, user_message, sentiment, mental_state):
        """
        RESPONSE GENERATION
        Creates culturally-appropriate therapeutic responses
        """
        try:
            # Get category-specific response
            category = mental_state.get('category', 'general')
            sentiment_label = sentiment.get('label', 'NEUTRAL')
            
            # African-context therapy responses
            responses = self.get_african_context_responses()
            
            # Select appropriate response category
            if category in responses:
                response_pool = responses[category]
            else:
                response_pool = responses['general']
            
            # Choose response based on sentiment
            if sentiment_label == 'NEGATIVE' and len(response_pool) > 1:
                chosen_response = response_pool[0]  # More empathetic responses first
            else:
                chosen_response = random.choice(response_pool)
            
            # Personalize the response
            return self.personalize_response(chosen_response, user_message)
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self.get_default_response()
    
    def get_african_context_responses(self):
        """
        CULTURALLY-APPROPRIATE RESPONSES
        Responses adapted for African cultural context
        """
        return {
            'anxiety': [
                "I can hear the worry in your words, and I want you to know that anxiety is something many people experience. In our communities, we often say 'pole pole' - take it slowly. Let's work through this step by step. What specific situation is making you feel most anxious right now?",
                "Anxiety can feel like a storm in your mind, but remember that even the strongest storms eventually pass. You mentioned feeling anxious - can you tell me more about what's triggering these feelings? Sometimes talking through our worries can help reduce their power over us."
            ],
            'depression': [
                "I hear the heaviness in what you've shared, and I want you to know that you're not alone in feeling this way. Depression can make everything feel more difficult, but reaching out like you have today shows real strength. What has been weighing on you most lately?",
                "Thank you for trusting me with your feelings. When we're feeling low, it can seem like the darkness will never lift, but healing is possible. In many African traditions, we understand that 'baada ya dhiki faraja' - after hardship comes ease. What would help you feel a little lighter today?"
            ],
            'stress': [
                "It sounds like you're carrying a heavy load right now. Stress is very common in our busy lives, especially when we're trying to balance family, work, and personal responsibilities. The Swahili saying 'haraka haraka haina baraka' reminds us that rushing brings no blessing. What's putting the most pressure on you?",
                "I can sense that you're feeling overwhelmed. Stress affects all of us, and it's important to acknowledge when the burden feels too heavy. Let's think about ways to lighten this load. What part of your stress feels most manageable to address first?"
            ],
            'relationships': [
                "Relationships, especially family ones, can be both our greatest source of joy and our biggest challenges. In African culture, we deeply value our connections with others, which can sometimes create complex dynamics. What relationship situation is concerning you most?",
                "I understand that relationship issues can be particularly difficult because they involve people we care about deeply. The concept of Ubuntu teaches us that we are interconnected, but it's also important to maintain healthy boundaries. Can you share more about what's happening?"
            ],
            'financial': [
                "Financial stress can affect every aspect of our lives - our sleep, relationships, and overall wellbeing. Many people are facing economic challenges, especially in these uncertain times. While I can't solve money problems directly, I can help you manage the emotional impact. How are these financial concerns affecting your daily life?",
                "Money worries can feel overwhelming and can consume our thoughts. You're not alone in facing financial challenges - many people in our community struggle with this. Let's talk about ways to manage the stress while you work on practical solutions. What aspect of your financial situation worries you most?"
            ],
            'trauma': [
                "Thank you for having the courage to share something so difficult. Trauma can have lasting effects on how we see ourselves and the world around us. Healing from trauma takes time, and everyone's journey is different. You don't have to go through this alone - there are people trained to help with trauma recovery. How are you feeling right now after sharing this?",
                "I'm honored that you felt safe enough to share your trauma with me. What you've experienced was not your fault, and your feelings about it are completely valid. Trauma recovery is possible, though it often requires professional support. Would you like me to help you find trauma-informed therapists in your area?"
            ],
            'general': [
                "Thank you for reaching out and sharing what's on your mind. It takes courage to talk about our mental health, and you've taken an important step today. I'm here to listen and support you through whatever you're experiencing. What would you like to explore together?",
                "I'm glad you decided to talk today. Sometimes just expressing our thoughts and feelings can provide some relief. Your mental health matters, and you deserve support. What's been on your mind lately that you'd like to discuss?"
            ]
        }
    
    def personalize_response(self, base_response, user_message):
        """Add personal touches to responses based on user input"""
        # This could be enhanced with more sophisticated personalization
        return base_response
    
    def get_default_response(self):
        """Safe default response when other methods fail"""
        return "I'm here to listen and support you. Thank you for sharing with me. What would you like to talk about today?"
    
    def generate_suggestions(self, user_message, sentiment):
        """Generate relevant follow-up suggestions"""
        lower_message = user_message.lower()
        
        if 'stress' in lower_message:
            return [
                "Try a 5-minute breathing exercise",
                "Take our detailed stress assessment", 
                "Learn stress management techniques",
                "Consider booking a therapy session"
            ]
        elif any(word in lower_message for word in ['sad', 'depressed', 'down']):
            return [
                "Complete our depression screening",
                "Explore mood tracking techniques",
                "Connect with a mental health professional",
                "Join a support group"
            ]
        elif 'anxious' in lower_message or 'anxiety' in lower_message:
            return [
                "Practice grounding techniques",
                "Learn about anxiety management",
                "Take our anxiety assessment",
                "Consider professional counseling"
            ]
        elif 'family' in lower_message:
            return [
                "Explore family therapy options",
                "Learn communication strategies",
                "Consider mediation services",
                "Join family support groups"
            ]
        else:
            return [
                "Take our comprehensive wellness assessment",
                "Explore our therapy directory",
                "Join community support groups",
                "Learn more about mental wellness"
            ]
    
    def calculate_confidence(self, user_message):
        """Calculate confidence in AI response quality"""
        if not self.models_loaded:
            return 0.3  # Low confidence for template responses
        
        # Factors that increase confidence
        confidence = 0.5  # Base confidence
        
        # Message length (optimal 10-100 words)
        word_count = len(user_message.split())
        if 10 <= word_count <= 100:
            confidence += 0.2
        
        # Clear emotional indicators
        emotion_words = ['feel', 'feeling', 'sad', 'happy', 'anxious', 'stressed', 'worried']
        if any(word in user_message.lower() for word in emotion_words):
            confidence += 0.2
        
        # Specific context provided
        if len(user_message) > 50:  # More detailed messages
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def fallback_response(self, user_message):
        """Fallback response when AI processing fails"""
        return {
            'message': "I'm here to listen and support you, though I'm having some technical difficulties processing your message right now. Your mental health is important, and I want to make sure you get the help you need. Can you try rephrasing your question, or would you like me to connect you with other resources?",
            'is_crisis': False,
            'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
            'suggestions': [
                'Try rephrasing your message',
                'Take our mental health assessment',
                'Contact our support team',
                'Explore local mental health resources'
            ],
            'response_type': 'fallback',
            'confidence': 0.2
        }