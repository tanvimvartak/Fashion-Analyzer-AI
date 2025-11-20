import nltk
from textblob import TextBlob
import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

class FashionNLP:
    def __init__(self):
        self.fashion_keywords = {
            'clothing_types': [
                'dress', 'skirt', 'pants', 'jeans', 'shirt', 'blouse', 'top', 'sweater',
                'jacket', 'coat', 'blazer', 'hoodie', 'cardigan', 'kurta', 'anarkali',
                'saree', 'lehenga', 'jumpsuit', 'romper', 'shorts', 'leggings'
            ],
            'colors': [
                'black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 'purple',
                'orange', 'brown', 'gray', 'grey', 'navy', 'maroon', 'burgundy',
                'teal', 'turquoise', 'coral', 'lavender', 'beige', 'cream', 'gold', 'silver'
            ],
            'occasions': [
                'casual', 'formal', 'party', 'wedding', 'interview', 'date', 'work',
                'college', 'beach', 'festival', 'traditional', 'ethnic', 'western'
            ],
            'style_descriptors': [
                'cute', 'elegant', 'classy', 'sophisticated', 'trendy', 'chic',
                'bohemian', 'vintage', 'modern', 'minimalist', 'bold', 'edgy'
            ],
            'body_parts': [
                'waist', 'hips', 'shoulders', 'bust', 'legs', 'arms', 'neck'
            ],
            'fit_descriptors': [
                'fitted', 'loose', 'tight', 'baggy', 'oversized', 'slim', 'wide'
            ]
        }
        
        self.sentiment_keywords = {
            'positive': ['love', 'like', 'beautiful', 'gorgeous', 'stunning', 'amazing'],
            'negative': ['hate', 'dislike', 'ugly', 'terrible', 'awful', 'bad'],
            'uncertain': ['maybe', 'perhaps', 'not sure', 'confused', 'help']
        }
        
        # Initialize TF-IDF vectorizer for similarity matching
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def extract_fashion_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract fashion-related entities from text
        """
        text_lower = text.lower()
        entities = {category: [] for category in self.fashion_keywords.keys()}
        
        for category, keywords in self.fashion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities[category].append(keyword)
        
        # Remove duplicates
        for category in entities:
            entities[category] = list(set(entities[category]))
            
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of fashion-related text
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Custom fashion sentiment analysis
        text_lower = text.lower()
        positive_score = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_score = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        uncertain_score = sum(1 for word in self.sentiment_keywords['uncertain'] if word in text_lower)
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'positive_indicators': positive_score,
            'negative_indicators': negative_score,
            'uncertainty_indicators': uncertain_score,
            'overall_sentiment': 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'
        }
    
    def extract_intent(self, text: str) -> str:
        """
        Extract user intent from fashion query
        """
        text_lower = text.lower()
        
        # Define intent patterns
        intent_patterns = {
            'outfit_advice': [
                'what to wear', 'outfit suggestion', 'style advice', 'fashion advice',
                'how to style', 'what goes with', 'match with', 'pair with'
            ],
            'color_matching': [
                'color', 'colour', 'match', 'goes with', 'complement'
            ],
            'body_type': [
                'body type', 'body shape', 'figure', 'apple', 'pear', 'hourglass'
            ],
            'occasion_dressing': [
                'party', 'wedding', 'interview', 'date', 'work', 'casual', 'formal'
            ],
            'trend_inquiry': [
                'trend', 'trending', 'fashion', 'latest', 'current', 'popular'
            ],
            'item_analysis': [
                'analyze', 'opinion', 'thoughts', 'look good', 'suit me'
            ]
        }
        
        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return 'general_fashion'
    
    def extract_questions(self, text: str) -> List[str]:
        """
        Extract questions from user input
        """
        # Split by question marks and filter out empty strings
        questions = [q.strip() for q in text.split('?') if q.strip()]
        
        # Add question marks back
        questions = [q + '?' for q in questions if q]
        
        return questions
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for better analysis
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?]', '', text)
        
        return text
    
    def find_similar_queries(self, query: str, query_database: List[str]) -> List[Tuple[str, float]]:
        """
        Find similar queries in a database using TF-IDF cosine similarity
        """
        if not query_database:
            return []
        
        # Preprocess query and database
        processed_query = self.preprocess_text(query.lower())
        processed_database = [self.preprocess_text(q.lower()) for q in query_database]
        
        # Create TF-IDF vectors
        all_texts = [processed_query] + processed_database
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Return sorted similar queries with scores
        similar_queries = [(query_database[i], similarities[i]) for i in range(len(similarities))]
        similar_queries.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 5 similar queries with score > 0.1
        return [(query, score) for query, score in similar_queries if score > 0.1][:5]
    
    def generate_response_context(self, text: str) -> Dict:
        """
        Generate comprehensive context for response generation
        """
        entities = self.extract_fashion_entities(text)
        sentiment = self.analyze_sentiment(text)
        intent = self.extract_intent(text)
        questions = self.extract_questions(text)
        
        return {
            'entities': entities,
            'sentiment': sentiment,
            'intent': intent,
            'questions': questions,
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_images': 'image' in text.lower() or 'photo' in text.lower() or 'picture' in text.lower()
        }

# Create global instance
fashion_nlp = FashionNLP()
