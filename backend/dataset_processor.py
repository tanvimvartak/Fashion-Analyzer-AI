import pandas as pd
import os
import json
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import colorsys
import cv2
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extract visual and semantic features from fashion images"""
    
    def __init__(self):
        self.color_analyzer = None  # Set by DatasetProcessor after initialization
    
    def extract_image_features(self, image_path: str) -> Dict:
        """Extract comprehensive features from an image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not read image: {image_path}")
                return self._get_empty_features()
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract color features
            color_features = self._extract_color_features(image_rgb)
            
            # Extract texture features (edge density, sharpness)
            texture_features = self._extract_texture_features(image)
            
            # Extract shape/composition features (symmetry, complexity)
            composition_features = self._extract_composition_features(image_rgb)
            
            return {
                'colors': color_features,
                'texture': texture_features,
                'composition': composition_features,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Error extracting features from {image_path}: {e}")
            return self._get_empty_features()
    
    def _extract_color_features(self, image_rgb: np.ndarray) -> Dict:
        """Extract dominant colors and color distribution"""
        try:
            data = image_rgb.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means for dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(data, 5, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            centers = np.uint8(centers)
            unique_labels, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels) * 100
            
            color_names = []
            color_histogram = {}
            
            for i, center in enumerate(centers):
                color_name = self._rgb_to_color_name(center)
                percentage = percentages[i]
                color_names.append(color_name)
                color_histogram[color_name] = round(percentage, 2)
            
            # Color diversity (how many distinct colors)
            color_diversity = len(set(color_names))
            
            return {
                'dominant_colors': color_names,
                'histogram': color_histogram,
                'diversity_score': color_diversity,
                'primary_color': color_names[0] if color_names else 'unknown'
            }
        except Exception as e:
            logger.warning(f"Color extraction failed: {e}")
            return {'dominant_colors': [], 'histogram': {}, 'diversity_score': 0, 'primary_color': 'unknown'}
    
    def _extract_texture_features(self, image: np.ndarray) -> Dict:
        """Extract texture features using edge detection"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sobel edge detection (measures detail/embellishment)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            edge_magnitude = np.sqrt(sobelx**2 + sobely**2)
            edge_density = np.mean(edge_magnitude) / 255.0  # Normalize
            
            # Laplacian for sharpness (high = embellished/patterned)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # Classify texture
            if sharpness > 500:
                texture_type = 'embellished'
            elif sharpness > 100:
                texture_type = 'patterned'
            else:
                texture_type = 'plain'
            
            return {
                'edge_density': round(float(edge_density), 3),
                'sharpness_score': round(float(sharpness), 2),
                'texture_type': texture_type
            }
        except Exception as e:
            logger.warning(f"Texture extraction failed: {e}")
            return {'edge_density': 0.0, 'sharpness_score': 0.0, 'texture_type': 'unknown'}
    
    def _extract_composition_features(self, image_rgb: np.ndarray) -> Dict:
        """Extract composition features (symmetry, brightness range)"""
        try:
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
            
            # Brightness distribution
            brightness_mean = np.mean(gray) / 255.0
            brightness_std = np.std(gray) / 255.0
            
            # Horizontal symmetry (left-right reflection)
            h, w = gray.shape
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            # Pad if needed
            if left_half.shape[1] != right_half.shape[1]:
                min_w = min(left_half.shape[1], right_half.shape[1])
                left_half = left_half[:, :min_w]
                right_half = right_half[:, :min_w]
            
            symmetry_score = np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
            
            return {
                'brightness_mean': round(brightness_mean, 3),
                'brightness_std': round(brightness_std, 3),
                'symmetry_score': round(float(symmetry_score), 3)
            }
        except Exception as e:
            logger.warning(f"Composition extraction failed: {e}")
            return {'brightness_mean': 0.5, 'brightness_std': 0.2, 'symmetry_score': 0.5}
    
    def _rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Convert RGB to color name"""
        r, g, b = rgb
        
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r < 100 and g < 100 and b < 100:
            return 'gray'
        elif r > 150 and g < 100 and b < 100:
            return 'red'
        elif r < 100 and g > 150 and b < 100:
            return 'green'
        elif r < 100 and g < 100 and b > 150:
            return 'blue'
        elif r > 150 and g > 150 and b < 100:
            return 'yellow'
        elif r > 150 and g < 100 and b > 150:
            return 'purple'
        elif r > 150 and g > 100 and b < 100:
            return 'orange'
        elif r > 100 and g > 50 and b < 50:
            return 'brown'
        elif r > 150 and g > 100 and b > 150:
            return 'pink'
        elif r < 50 and g < 100 and b > 100:
            return 'navy'
        else:
            hsv = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = hsv[0] * 360
            
            if hue < 30 or hue > 330:
                return 'red'
            elif hue < 90:
                return 'yellow'
            elif hue < 150:
                return 'green'
            elif hue < 210:
                return 'blue'
            elif hue < 270:
                return 'purple'
            else:
                return 'pink'
    
    def _get_empty_features(self) -> Dict:
        """Return empty feature dict"""
        return {
            'colors': {
                'dominant_colors': [],
                'histogram': {},
                'diversity_score': 0,
                'primary_color': 'unknown'
            },
            'texture': {
                'edge_density': 0.0,
                'sharpness_score': 0.0,
                'texture_type': 'unknown'
            },
            'composition': {
                'brightness_mean': 0.5,
                'brightness_std': 0.2,
                'symmetry_score': 0.5
            },
            'success': False
        }

class DatasetProcessor:
    def __init__(self, base_path: Optional[str] = None):
        # Make base path dynamic and server-ready
        if base_path:
            self.base_path = base_path
        else:
            # Try to detect the base path dynamically
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level from backend/ to the main project directory
            self.base_path = os.path.dirname(current_dir)
            
            # Fallback: check if we're in the right directory by looking for key folders
            if not self._validate_base_path(self.base_path):
                # Try environment variable
                self.base_path = os.getenv('FASHION_ANALYZER_PATH', self.base_path)
                
                # Last resort: use current directory
                if not self._validate_base_path(self.base_path):
                    self.base_path = os.getcwd()
        
        logger.info(f"📁 Using base path: {self.base_path}")
        
        self.body_metrics_data = None
        self.fashion_images_metadata = None
        self.feature_extractor = FeatureExtractor()
        self.color_analyzer = ColorAnalyzer()
        self.feature_extractor.color_analyzer = self.color_analyzer
        
        # Initialize semantic indexing attributes
        self.semantic_index = None
        self.semantic_matrix = None
        
        # Metadata cache path
        self.cache_dir = os.path.join(self.base_path, '.metadata_cache')
        self.metadata_cache_file = os.path.join(self.cache_dir, 'image_metadata.json')
        
        self.load_datasets()
    
    def _validate_base_path(self, path: str) -> bool:
        """Validate that the base path contains expected dataset directories"""
        required_dirs = ['body metrics', 'women fashion']
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(path, dir_name)):
                return False
        return True
    
    def load_datasets(self):
        """Load all dataset files into memory"""
        try:
            logger.info(f"🔍 Loading datasets from: {self.base_path}")
            
            # Validate base path
            if not self._validate_base_path(self.base_path):
                logger.warning(f"⚠️  Base path validation failed. Some datasets may not be found.")
                logger.info(f"📂 Looking for datasets in: {self.base_path}")
                logger.info(f"📋 Directory contents: {os.listdir(self.base_path) if os.path.exists(self.base_path) else 'Path does not exist'}")
            
            # Load body metrics CSV
            self.load_body_metrics()
            
            # Index fashion images with feature extraction
            self.index_fashion_images()
            
            # Save metadata cache
            self.save_metadata_cache()
            
            logger.info("✅ All datasets loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            logger.info("🔧 Tip: Set FASHION_ANALYZER_PATH environment variable to specify dataset location")
    
    def load_body_metrics(self):
        """Load body metrics and color recommendations"""
        try:
            csv_path = os.path.join(self.base_path, "body metrics", "Profile of Body Metrics and Fashion Colors.csv")
            logger.info(f"📊 Looking for body metrics CSV at: {csv_path}")
            
            if os.path.exists(csv_path):
                self.body_metrics_data = pd.read_csv(csv_path)
                logger.info(f"✅ Loaded body metrics data: {len(self.body_metrics_data)} records")
            else:
                logger.warning("⚠️  Body metrics CSV not found")
                logger.info(f"📁 Expected location: {csv_path}")
                # List available files in body metrics directory if it exists
                body_metrics_dir = os.path.join(self.base_path, "body metrics")
                if os.path.exists(body_metrics_dir):
                    available_files = os.listdir(body_metrics_dir)
                    logger.info(f"📋 Available files in body metrics/: {available_files}")
        except Exception as e:
            logger.error(f"Error loading body metrics: {e}")
    
    def index_fashion_images(self):
        """Create metadata index of all fashion images with feature extraction"""
        self.fashion_images_metadata = []
        
        # Try to load from cache first
        if os.path.exists(self.metadata_cache_file):
            try:
                logger.info("📦 Loading metadata from cache...")
                with open(self.metadata_cache_file, 'r') as f:
                    self.fashion_images_metadata = json.load(f)
                logger.info(f"✅ Loaded {len(self.fashion_images_metadata)} images from cache")
                
                # Build semantic index from cached metadata
                self._build_semantic_index()
                return
            except Exception as e:
                logger.warning(f"⚠️  Could not load cache: {e}. Rebuilding...")
        
        logger.info("🔨 Building metadata index with feature extraction...")
        
        # Index women fashion images
        women_fashion_path = os.path.join(self.base_path, "women fashion")
        logger.info(f"👗 Indexing women fashion images at: {women_fashion_path}")
        
        if os.path.exists(women_fashion_path):
            image_count = 0
            for filename in os.listdir(women_fashion_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    try:
                        image_path = os.path.join(women_fashion_path, filename)
                        metadata = self.extract_image_metadata(filename)
                        
                        # Extract visual features from image
                        features = self.feature_extractor.extract_image_features(image_path)
                        metadata['visual_features'] = features
                        
                        metadata['path'] = image_path
                        metadata['category'] = 'women_fashion'
                        self.fashion_images_metadata.append(metadata)
                        image_count += 1
                        
                        if image_count % 10 == 0:
                            logger.info(f"  ⏳ Processed {image_count} images...")
                    except Exception as e:
                        logger.warning(f"⚠️  Error processing {filename}: {e}")
            
            logger.info(f"✅ Indexed {image_count} women fashion images")
        else:
            logger.warning(f"⚠️  Women fashion directory not found: {women_fashion_path}")
        
        # Index body shape images
        body_shape_path = os.path.join(self.base_path, "body shape wise clothes")
        logger.info(f"👕 Indexing body shape images at: {body_shape_path}")
        
        if os.path.exists(body_shape_path):
            image_count = 0
            for filename in os.listdir(body_shape_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    try:
                        image_path = os.path.join(body_shape_path, filename)
                        metadata = self.extract_image_metadata(filename)
                        
                        # Extract visual features from image
                        features = self.feature_extractor.extract_image_features(image_path)
                        metadata['visual_features'] = features
                        
                        metadata['path'] = image_path
                        metadata['category'] = 'body_shape'
                        self.fashion_images_metadata.append(metadata)
                        image_count += 1
                        
                        if image_count % 10 == 0:
                            logger.info(f"  ⏳ Processed {image_count} images...")
                    except Exception as e:
                        logger.warning(f"⚠️  Error processing {filename}: {e}")
            
            logger.info(f"✅ Indexed {image_count} body shape images")
        else:
            logger.warning(f"⚠️  Body shape directory not found: {body_shape_path}")
        
        total_images = len(self.fashion_images_metadata)
        logger.info(f"📸 Total indexed images: {total_images}")
        
        if total_images == 0:
            logger.warning("⚠️  No fashion images found! Check your dataset paths.")
            logger.info(f"💡 Tip: Set FASHION_ANALYZER_PATH environment variable to: {os.path.dirname(self.base_path)}")
        
        # Build TF-IDF matrix for semantic similarity
        self._build_semantic_index()
        
        # Log some sample metadata for debugging
        if total_images > 0:
            sample = self.fashion_images_metadata[0]
            logger.debug(f"Sample metadata (truncated): filename={sample['filename']}, colors={sample['colors']}, texture={sample.get('visual_features', {}).get('texture', {}).get('texture_type', 'N/A')}")
    
    def extract_image_metadata(self, filename: str) -> Dict:
        """Extract fashion metadata from image filename"""
        filename_lower = filename.lower()
        
        metadata = {
            'filename': filename,
            'clothing_types': [],
            'colors': [],
            'occasions': [],
            'style_descriptors': [],
            'ethnic_wear': False
        }
        
        # Extract clothing types
        clothing_keywords = {
            'anarkali': 'anarkali',
            'saree': 'saree',
            'lehenga': 'lehenga',
            'dress': 'dress',
            'suit': 'suit',
            'top': 'top',
            'blouse': 'blouse',
            'skirt': 'skirt',
            'kurta': 'kurta',
            'pants': 'pants',
            'jeans': 'jeans',
            'jacket': 'jacket',
            'blazer': 'blazer'
        }
        
        for keyword, clothing_type in clothing_keywords.items():
            if keyword in filename_lower:
                metadata['clothing_types'].append(clothing_type)
        
        # Extract colors
        color_keywords = {
            'black': 'black',
            'white': 'white',
            'red': 'red',
            'blue': 'blue',
            'green': 'green',
            'yellow': 'yellow',
            'pink': 'pink',
            'purple': 'purple',
            'orange': 'orange',
            'brown': 'brown',
            'gray': 'gray',
            'grey': 'gray',
            'navy': 'navy',
            'burgundy': 'burgundy',
            'turquoise': 'turquoise',
            'olive': 'olive',
            'lavender': 'lavender',
            'coral': 'coral',
            'gold': 'gold',
            'silver': 'silver'
        }
        
        for keyword, color in color_keywords.items():
            if keyword in filename_lower:
                metadata['colors'].append(color)
        
        # Detect ethnic wear
        ethnic_keywords = ['anarkali', 'saree', 'lehenga', 'kurta', 'salwar', 'ethnic', 'traditional']
        metadata['ethnic_wear'] = any(keyword in filename_lower for keyword in ethnic_keywords)
        
        # Extract style descriptors
        style_keywords = {
            'embroidered': 'embroidered',
            'embellished': 'embellished',
            'sequin': 'sequined',
            'floral': 'floral',
            'printed': 'printed',
            'lace': 'lace',
            'silk': 'silk',
            'cotton': 'cotton',
            'formal': 'formal',
            'casual': 'casual',
            'party': 'party'
        }
        
        for keyword, style in style_keywords.items():
            if keyword in filename_lower:
                metadata['style_descriptors'].append(style)
        
        return metadata
    
    def get_color_recommendations(self, user_preferences: Dict) -> Dict:
        """Get color recommendations based on body metrics data"""
        if self.body_metrics_data is None:
            return self.get_default_color_recommendations()
        
        try:
            # For now, return aggregated color recommendations from the dataset
            # In a real implementation, you'd match user preferences to similar profiles
            
            popular_colors = {}
            if 'Recommended_Clothes_Color' in self.body_metrics_data.columns:
                color_counts = self.body_metrics_data['Recommended_Clothes_Color'].value_counts()
                popular_colors['clothes'] = color_counts.head(5).to_dict()
            
            if 'Recommended_Pants_Color' in self.body_metrics_data.columns:
                pants_counts = self.body_metrics_data['Recommended_Pants_Color'].value_counts()
                popular_colors['pants'] = pants_counts.head(5).to_dict()
            
            return {
                'status': 'success',
                'popular_colors': popular_colors,
                'total_profiles': len(self.body_metrics_data),
                'recommendations': self.generate_color_suggestions(popular_colors)
            }
            
        except Exception as e:
            logger.error(f"Error getting color recommendations: {e}")
            return self.get_default_color_recommendations()
    
    def get_default_color_recommendations(self) -> Dict:
        """Fallback color recommendations"""
        return {
            'status': 'fallback',
            'recommendations': {
                'universally_flattering': ['navy', 'white', 'black', 'gray'],
                'warm_skin_tones': ['coral', 'warm_red', 'golden_yellow', 'olive_green'],
                'cool_skin_tones': ['royal_blue', 'emerald_green', 'burgundy', 'silver'],
                'neutral_skin_tones': ['most_colors_work', 'avoid_very_pale_or_very_bright']
            }
        }
    
    def generate_color_suggestions(self, popular_colors: Dict) -> Dict:
        """Generate color combination suggestions"""
        suggestions = {
            'top_bottom_combinations': [
                {'top': 'white', 'bottom': 'navy', 'occasion': 'professional'},
                {'top': 'black', 'bottom': 'white', 'occasion': 'classic'},
                {'top': 'coral', 'bottom': 'white', 'occasion': 'summer'},
                {'top': 'burgundy', 'bottom': 'gray', 'occasion': 'autumn'}
            ],
            'monochrome_looks': ['all_black', 'all_white', 'all_navy', 'all_gray'],
            'accent_colors': ['gold_jewelry', 'silver_accessories', 'bold_bag', 'colorful_scarf']
        }
        return suggestions
    
    def find_similar_outfits(self, query: str, user_image_colors: List[str] = None) -> List[Dict]:
        """Find similar outfits from dataset based on query using semantic similarity"""
        if not self.fashion_images_metadata:
            return []
        
        query_lower = query.lower()
        matches = []
        
        try:
            # Build query feature vector
            query_features = self._build_query_vector(query_lower, user_image_colors)
            
            # Use semantic similarity with TF-IDF
            if (hasattr(self, 'semantic_index') and self.semantic_index is not None and 
                hasattr(self, 'semantic_matrix') and self.semantic_matrix is not None):
                try:
                    # Calculate cosine similarity with all indexed images
                    similarity_scores = cosine_similarity([query_features], self.semantic_matrix)[0]
                    
                    for idx, score in enumerate(similarity_scores):
                        if score > 0.1:  # Threshold for relevance
                            image_meta = self.fashion_images_metadata[idx].copy()
                            image_meta['similarity_score'] = float(score)
                            matches.append(image_meta)
                    
                    logger.info(f"✅ Found {len(matches)} semantic matches for query: '{query_lower}'")
                except Exception as e:
                    logger.warning(f"⚠️  Error using semantic matrix, falling back to keyword matching: {e}")
                    # Fallback to keyword-based matching
                    for image_meta in self.fashion_images_metadata:
                        similarity_score = self._calculate_keyword_similarity(
                            query_lower, image_meta, user_image_colors
                        )
                        if similarity_score > 0:
                            image_meta_copy = image_meta.copy()
                            image_meta_copy['similarity_score'] = similarity_score
                            matches.append(image_meta_copy)
            else:
                # Fallback: keyword-based matching
                logger.info("ℹ️  Semantic index not available, using keyword matching")
                for image_meta in self.fashion_images_metadata:
                    similarity_score = self._calculate_keyword_similarity(
                        query_lower, image_meta, user_image_colors
                    )
                    if similarity_score > 0:
                        image_meta_copy = image_meta.copy()
                        image_meta_copy['similarity_score'] = similarity_score
                        matches.append(image_meta_copy)
            
            # Sort by similarity score and return top matches
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            return matches[:5]
            
        except Exception as e:
            logger.error(f"Error in semantic similarity search: {e}")
            # Fallback to keyword matching
            return self._keyword_based_similar_outfits(query_lower, user_image_colors)
    
    def _build_semantic_index(self):
        """Build TF-IDF semantic index for similarity search"""
        # Skip if already built
        if self.semantic_index is not None and self.semantic_matrix is not None:
            logger.debug("✅ Semantic index already built, skipping rebuild")
            return
        
        try:
            if len(self.fashion_images_metadata) == 0:
                logger.warning("⚠️  No metadata to index")
                self.semantic_index = None
                self.semantic_matrix = None
                return
            
            # Build document texts from metadata
            documents = []
            for meta in self.fashion_images_metadata:
                doc_parts = [
                    ' '.join(meta.get('clothing_types', [])),
                    ' '.join(meta.get('colors', [])),
                    ' '.join(meta.get('occasions', [])),
                    ' '.join(meta.get('style_descriptors', [])),
                ]
                
                # Add visual features
                visual_features = meta.get('visual_features', {})
                if visual_features.get('colors'):
                    doc_parts.append(' '.join(visual_features['colors'].get('dominant_colors', [])))
                if visual_features.get('texture'):
                    doc_parts.append(visual_features['texture'].get('texture_type', ''))
                
                doc = ' '.join(doc_parts)
                documents.append(doc)
            
            # Build TF-IDF vectorizer and matrix
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            self.semantic_matrix = vectorizer.fit_transform(documents)
            self.semantic_index = vectorizer
            
            logger.info(f"✅ Built semantic index for {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error building semantic index: {e}")
            self.semantic_index = None
            self.semantic_matrix = None
    
    def _build_query_vector(self, query: str, user_colors: List[str] = None) -> np.ndarray:
        """Build feature vector for a query"""
        query_parts = [query]
        if user_colors:
            query_parts.extend(user_colors)
        
        query_text = ' '.join(query_parts)
        
        if self.semantic_index:
            try:
                vector = self.semantic_index.transform([query_text]).toarray()[0]
                if len(vector) == 0:
                    logger.warning(f"⚠️  Query vector is empty for: '{query_text}'")
                    return np.array([])
                return vector
            except Exception as e:
                logger.warning(f"⚠️  Query vector transformation failed: {e}")
                return np.array([])
        else:
            return np.array([])
    
    def _calculate_keyword_similarity(self, query: str, image_meta: Dict, user_colors: List[str] = None) -> float:
        """Calculate keyword-based similarity score"""
        score = 0.0
        
        # Clothing type matches (weight: 3)
        for clothing_type in image_meta.get('clothing_types', []):
            if clothing_type in query:
                score += 3
        
        # Color matches (weight: 2)
        for color in image_meta.get('colors', []):
            if color in query:
                score += 2
        
        # User uploaded image colors (weight: 2)
        if user_colors:
            for user_color in user_colors:
                if user_color in image_meta.get('colors', []):
                    score += 2
        
        # Style descriptor matches (weight: 1)
        for style in image_meta.get('style_descriptors', []):
            if style in query:
                score += 1
        
        # Visual texture matches (weight: 1.5)
        visual_features = image_meta.get('visual_features', {})
        texture_type = visual_features.get('texture', {}).get('texture_type', '')
        if texture_type and texture_type in query:
            score += 1.5
        
        # Ethnic wear preference (weight: 3)
        ethnic_keywords = ['ethnic', 'traditional', 'indian', 'anarkali', 'saree', 'lehenga']
        if any(keyword in query for keyword in ethnic_keywords) and image_meta.get('ethnic_wear'):
            score += 3
        
        return score
    
    def _keyword_based_similar_outfits(self, query: str, user_colors: List[str] = None) -> List[Dict]:
        """Fallback keyword-based similar outfit search"""
        matches = []
        for image_meta in self.fashion_images_metadata:
            score = self._calculate_keyword_similarity(query, image_meta, user_colors)
            if score > 0:
                image_meta_copy = image_meta.copy()
                image_meta_copy['similarity_score'] = score
                matches.append(image_meta_copy)
        
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:5]
    
    def save_metadata_cache(self):
        """Save metadata to cache file for faster startup"""
        try:
            # Create cache directory
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Convert metadata to JSON-serializable format
            cache_data = []
            for meta in self.fashion_images_metadata:
                meta_copy = meta.copy()
                # Remove non-serializable objects if any
                if 'similarity_score' in meta_copy:
                    meta_copy['similarity_score'] = float(meta_copy['similarity_score'])
                cache_data.append(meta_copy)
            
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"💾 Metadata cache saved to {self.metadata_cache_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save metadata cache: {e}")
    
    def analyze_uploaded_image_colors(self, image_path: str) -> Dict:
        """Analyze colors in user uploaded image"""
        try:
            return self.color_analyzer.extract_dominant_colors(image_path)
        except Exception as e:
            logger.error(f"Error analyzing image colors: {e}")
            return {'dominant_colors': [], 'color_percentages': {}}
    
    def get_dataset_insights(self, query: str) -> Dict:
        """Get insights from datasets based on user query"""
        insights = {
            'color_recommendations': self.get_color_recommendations({}),
            'similar_outfits': self.find_similar_outfits(query),
            'dataset_stats': {
                'total_fashion_images': len(self.fashion_images_metadata),
                'body_profiles': len(self.body_metrics_data) if self.body_metrics_data is not None else 0,
                'ethnic_wear_count': len([img for img in self.fashion_images_metadata if img['ethnic_wear']]),
                'western_wear_count': len([img for img in self.fashion_images_metadata if not img['ethnic_wear']])
            }
        }
        return insights

class ColorAnalyzer:
    """Analyze colors in fashion images"""
    
    def extract_dominant_colors(self, image_path: str, num_colors: int = 5) -> Dict:
        """Extract dominant colors from image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Reshape image to be a list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Use K-means to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert to color names and percentages
            centers = np.uint8(centers)
            
            # Count pixels for each cluster
            unique_labels, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels) * 100
            
            # Convert RGB to color names
            dominant_colors = []
            color_percentages = {}
            
            for i, center in enumerate(centers):
                color_name = self.rgb_to_color_name(center)
                percentage = percentages[i]
                
                dominant_colors.append({
                    'color_name': color_name,
                    'rgb': center.tolist(),
                    'percentage': round(percentage, 2)
                })
                
                color_percentages[color_name] = round(percentage, 2)
            
            # Sort by percentage
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            return {
                'dominant_colors': dominant_colors,
                'color_percentages': color_percentages,
                'primary_color': dominant_colors[0]['color_name'] if dominant_colors else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return {'dominant_colors': [], 'color_percentages': {}, 'primary_color': 'unknown'}
    
    def rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Convert RGB values to approximate color names"""
        r, g, b = rgb
        
        # Define color ranges
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r < 100 and g < 100 and b < 100:
            return 'gray'
        elif r > 150 and g < 100 and b < 100:
            return 'red'
        elif r < 100 and g > 150 and b < 100:
            return 'green'
        elif r < 100 and g < 100 and b > 150:
            return 'blue'
        elif r > 150 and g > 150 and b < 100:
            return 'yellow'
        elif r > 150 and g < 100 and b > 150:
            return 'purple'
        elif r > 150 and g > 100 and b < 100:
            return 'orange'
        elif r > 100 and g > 50 and b < 50:
            return 'brown'
        elif r > 150 and g > 100 and b > 150:
            return 'pink'
        elif r < 50 and g < 100 and b > 100:
            return 'navy'
        else:
            # Use HSV for better color detection
            hsv = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = hsv[0] * 360
            
            if hue < 30 or hue > 330:
                return 'red'
            elif hue < 90:
                return 'yellow'
            elif hue < 150:
                return 'green'
            elif hue < 210:
                return 'blue'
            elif hue < 270:
                return 'purple'
            else:
                return 'pink'

# Create global instance with optional configuration
def create_dataset_processor() -> DatasetProcessor:
    """Create dataset processor with environment-aware configuration"""
    # Check for custom base path from environment
    base_path = os.getenv('FASHION_ANALYZER_PATH')
    
    if base_path and os.path.exists(base_path):
        logger.info(f"🌍 Using environment path: {base_path}")
        return DatasetProcessor(base_path=base_path)
    else:
        logger.info("🔍 Auto-detecting dataset path...")
        return DatasetProcessor()

# Initialize the global instance
dataset_processor = create_dataset_processor()
