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

logger = logging.getLogger(__name__)

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
        self.color_analyzer = ColorAnalyzer()
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
            
            # Index fashion images
            self.index_fashion_images()
            
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
        """Create metadata index of all fashion images"""
        self.fashion_images_metadata = []
        
        # Index women fashion images
        women_fashion_path = os.path.join(self.base_path, "women fashion")
        logger.info(f"👗 Looking for women fashion images at: {women_fashion_path}")
        
        if os.path.exists(women_fashion_path):
            image_count = 0
            for filename in os.listdir(women_fashion_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    try:
                        metadata = self.extract_image_metadata(filename)
                        metadata['path'] = os.path.join(women_fashion_path, filename)
                        metadata['category'] = 'women_fashion'
                        self.fashion_images_metadata.append(metadata)
                        image_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️  Error processing {filename}: {e}")
            
            logger.info(f"✅ Indexed {image_count} women fashion images")
        else:
            logger.warning(f"⚠️  Women fashion directory not found: {women_fashion_path}")
        
        # Index body shape images
        body_shape_path = os.path.join(self.base_path, "body shape wise clothes")
        logger.info(f"👕 Looking for body shape images at: {body_shape_path}")
        
        if os.path.exists(body_shape_path):
            image_count = 0
            for filename in os.listdir(body_shape_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    try:
                        metadata = self.extract_image_metadata(filename)
                        metadata['path'] = os.path.join(body_shape_path, filename)
                        metadata['category'] = 'body_shape'
                        self.fashion_images_metadata.append(metadata)
                        image_count += 1
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
        
        # Log some sample metadata for debugging
        if total_images > 0:
            sample = self.fashion_images_metadata[0]
            logger.debug(f"Sample metadata: {sample}")
    
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
        """Find similar outfits from dataset based on query"""
        if not self.fashion_images_metadata:
            return []
        
        # Use text similarity to find relevant images
        query_lower = query.lower()
        matches = []
        
        for image_meta in self.fashion_images_metadata:
            similarity_score = 0
            
            # Check clothing type matches
            for clothing_type in image_meta['clothing_types']:
                if clothing_type in query_lower:
                    similarity_score += 3
            
            # Check color matches
            for color in image_meta['colors']:
                if color in query_lower:
                    similarity_score += 2
            
            # Check if user uploaded image colors match
            if user_image_colors:
                for user_color in user_image_colors:
                    if user_color in image_meta['colors']:
                        similarity_score += 2
            
            # Check style matches
            for style in image_meta['style_descriptors']:
                if style in query_lower:
                    similarity_score += 1
            
            # Check ethnic wear preference
            ethnic_keywords = ['ethnic', 'traditional', 'indian', 'anarkali', 'saree', 'lehenga']
            if any(keyword in query_lower for keyword in ethnic_keywords) and image_meta['ethnic_wear']:
                similarity_score += 3
            
            if similarity_score > 0:
                image_meta['similarity_score'] = similarity_score
                matches.append(image_meta)
        
        # Sort by similarity score and return top matches
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:5]
    
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
        """Extract dominant colors from image, filtering out background colors"""
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
            
            # Convert RGB to color names and filter
            all_colors = []
            clothing_colors = []  # Non-background colors
            
            for i, center in enumerate(centers):
                color_name = self.rgb_to_color_name(center)
                percentage = percentages[i]
                
                color_info = {
                    'color_name': color_name,
                    'rgb': center.tolist(),
                    'percentage': round(percentage, 2)
                }
                
                all_colors.append(color_info)
                
                # Filter out likely background colors (white, black, gray)
                # But keep them if they're the dominant color with high percentage
                if color_name not in ['white', 'black', 'gray'] or percentage > 60:
                    clothing_colors.append(color_info)
            
            # Sort both lists by percentage
            all_colors.sort(key=lambda x: x['percentage'], reverse=True)
            clothing_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Determine primary color (prefer clothing colors over background)
            if clothing_colors:
                primary_color = clothing_colors[0]['color_name']
                # Use clothing colors as dominant, but include background info
                dominant_colors = clothing_colors + [c for c in all_colors if c not in clothing_colors]
            else:
                primary_color = all_colors[0]['color_name']
                dominant_colors = all_colors
            
            # Create color percentages dict
            color_percentages = {}
            for color in dominant_colors:
                color_percentages[color['color_name']] = color['percentage']
            
            return {
                'dominant_colors': dominant_colors[:5],  # Return top 5
                'color_percentages': color_percentages,
                'primary_color': primary_color
            }
            
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return {'dominant_colors': [], 'color_percentages': {}, 'primary_color': 'unknown'}
    
    def rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Convert RGB values to accurate color names using HSV color space"""
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        
        # Convert to HSV for better color detection
        hsv = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        hue = hsv[0] * 360  # 0-360
        saturation = hsv[1] * 100  # 0-100
        value = hsv[2] * 100  # 0-100 (brightness)
        
        # Check for achromatic colors first (low saturation)
        if saturation < 10:
            if value > 85:
                return 'white'
            elif value < 20:
                return 'black'
            else:
                return 'gray'
        
        # Check for very dark colors (low brightness)
        if value < 25:
            return 'black'
        
        # Check for very light colors (high brightness, low saturation)
        if value > 85 and saturation < 30:
            return 'white'
        
        # Now check hue-based colors with better ranges
        # Red/Maroon/Burgundy (0-15 or 345-360)
        if (hue >= 345 or hue <= 15):
            if value < 50:
                return 'maroon'  # Dark red
            elif saturation > 70:
                return 'red'
            else:
                return 'pink'
        
        # Orange (15-45)
        elif 15 < hue <= 45:
            if value < 50:
                return 'brown'
            elif saturation > 60:
                return 'orange'
            else:
                return 'beige'
        
        # Yellow (45-70)
        elif 45 < hue <= 70:
            if saturation < 40:
                return 'cream'
            elif value > 70:
                return 'yellow'
            else:
                return 'gold'
        
        # Green (70-150)
        elif 70 < hue <= 150:
            if value < 40:
                return 'dark green'
            elif saturation < 40:
                return 'sage'
            else:
                return 'green'
        
        # Cyan/Turquoise (150-190)
        elif 150 < hue <= 190:
            if saturation > 50:
                return 'turquoise'
            else:
                return 'teal'
        
        # Blue (190-250)
        elif 190 < hue <= 250:
            if value < 40:
                return 'navy'
            elif saturation > 60:
                return 'blue'
            else:
                return 'light blue'
        
        # Purple/Violet (250-290)
        elif 250 < hue <= 290:
            if value < 40:
                return 'dark purple'
            elif saturation > 50:
                return 'purple'
            else:
                return 'lavender'
        
        # Magenta/Pink (290-330)
        elif 290 < hue <= 330:
            if saturation > 60:
                return 'magenta'
            else:
                return 'pink'
        
        # Burgundy/Wine (330-345)
        elif 330 < hue < 345:
            if value < 50:
                return 'burgundy'
            elif saturation > 50:
                return 'wine'
            else:
                return 'rose'
        
        # Fallback based on RGB dominance
        if r > g and r > b:
            if r > 150 and g < 100 and b < 100:
                return 'red'
            elif r > 100 and g > 50 and b > 50:
                return 'pink'
            else:
                return 'maroon'
        elif g > r and g > b:
            return 'green'
        elif b > r and b > g:
            if b > 150:
                return 'blue'
            else:
                return 'navy'
        else:
            return 'brown'

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
