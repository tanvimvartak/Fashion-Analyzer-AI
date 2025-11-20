from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
import os
from dotenv import load_dotenv
import base64
from PIL import Image
import io
import json
from typing import List, Optional, Dict
import logging
from pydantic import BaseModel
import httpx
from nlp_utils import fashion_nlp
from dataset_processor import dataset_processor

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stylette - AI Fashion Stylist API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

class ChatRequest(BaseModel):
    message: str
    images: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    status: str

@app.get("/")
async def root():
    return {"message": "Stylette - Your AI Fashion Stylist API", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat endpoint that handles both text and image analysis with NLP enhancement and dataset integration
    """
    try:
        # Use NLP to analyze the request
        nlp_context = fashion_nlp.generate_response_context(request.message)
        
        # Get insights from our datasets
        dataset_insights = dataset_processor.get_dataset_insights(request.message)
        
        # Enhanced prompt based on NLP analysis AND dataset insights
        base_prompt = f"""You are a professional fashion stylist and AI assistant with access to comprehensive fashion datasets. I've analyzed the user's request and here's what I found:

NATURAL LANGUAGE ANALYSIS:
- Intent: {nlp_context['intent']}
- Sentiment: {nlp_context['sentiment']['overall_sentiment']}
- Fashion entities found: {nlp_context['entities']}

DATASET ANALYSIS:
- Total fashion images in database: {dataset_insights['dataset_stats']['total_fashion_images']}
- Ethnic wear collection: {dataset_insights['dataset_stats']['ethnic_wear_count']} items
- Western wear collection: {dataset_insights['dataset_stats']['western_wear_count']} items
- Body profiles in dataset: {dataset_insights['dataset_stats']['body_profiles']} profiles
- Similar outfits found: {len(dataset_insights['similar_outfits'])} matches

User's question: {request.message}

Based on this comprehensive analysis, provide detailed recommendations including:
1. **Item Description**: What items do you see?
2. **Color Analysis**: Do the colors work together? (Reference our body metrics dataset)
3. **Styling Verdict**: Overall rating and compatibility
4. **Dataset Insights**: How this relates to similar items in our collection
5. **How to Style**: Specific styling instructions (enhanced by dataset patterns)
6. **Complete the Look**: Shoes, accessories, etc.
7. **Occasion**: Where to wear this
8. **Pro Tips**: Quick styling hacks from our database

Be enthusiastic, helpful, and specific in your recommendations! Tailor your response to the user's {nlp_context['sentiment']['overall_sentiment']} sentiment and {nlp_context['intent']} intent. Reference the dataset insights where relevant."""

        # Prepare content for Gemini
        content = [base_prompt]
        image_colors = []
        
        # Process images if provided
        if request.images:
            import tempfile
            for image_data in request.images:
                try:
                    # Remove data URL prefix if present
                    if image_data.startswith('data:image'):
                        image_data = image_data.split(',')[1]
                    
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    content.append(image)
                    
                    # Analyze colors in the image using our dataset processor
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                        temp_file.write(image_bytes)
                        temp_path = temp_file.name
                    
                    color_analysis = dataset_processor.analyze_uploaded_image_colors(temp_path)
                    if color_analysis['dominant_colors']:
                        image_colors.extend([color['color_name'] for color in color_analysis['dominant_colors'][:3]])
                    
                    os.unlink(temp_path)
                    
                except Exception as e:
                    logger.warning(f"Error processing image: {e}")
                    continue
        
        # Generate response using Gemini
        try:
            response = model.generate_content(content)
            gemini_response = response.text if response.text else None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            gemini_response = None
        
        if gemini_response:
            # Enhance Gemini response with semantic similarity insights FIRST
            enhanced_response = gemini_response + "\n\n"
            
            # Add semantic similarity section prominently
            if dataset_insights['similar_outfits']:
                enhanced_response += "### 💎 Stylette Semantic Match Analysis\n"
                enhanced_response += f"**Found {len(dataset_insights['similar_outfits'])} similar styles from your dataset:**\n\n"
                
                for i, outfit in enumerate(dataset_insights['similar_outfits'], 1):
                    similarity_score = outfit.get('similarity_score', 0)
                    outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
                    
                    # Extract key features for explanation
                    clothing_types = ', '.join(outfit.get('clothing_types', [])[:2])
                    colors = ', '.join(outfit.get('colors', [])[:2])
                    occasions = ', '.join(outfit.get('occasions', [])[:1])
                    
                    enhanced_response += f"**{i}. {outfit_name}** (Match Score: {similarity_score:.1%})\n"
                    enhanced_response += f"   • Type: {clothing_types}\n"
                    if colors:
                        enhanced_response += f"   • Colors: {colors}\n"
                    if occasions:
                        enhanced_response += f"   • Occasion: {occasions}\n"
                    enhanced_response += "\n"
            
            # Add other dataset insights
            enhanced_response += "### 📊 Dataset-Powered Insights\n"
            
            if image_colors:
                enhanced_response += f"• **Detected colors in your image:** {', '.join(set(image_colors))}\n"
            
            color_recs = dataset_insights['color_recommendations']
            if color_recs['status'] == 'success':
                enhanced_response += f"• **Body profile insights:** Analyzed across {color_recs['total_profiles']} profiles\n"
            
            enhanced_response += f"• **Powered by:** {dataset_insights['dataset_stats']['total_fashion_images']} fashion images in Stylette's collection\n"
            
            return ChatResponse(response=enhanced_response, status="success_with_datasets")
        else:
            # Fallback response with NLP context and dataset insights
            fallback_response = get_enhanced_fallback_response_with_datasets(
                request.message, nlp_context, dataset_insights, image_colors
            )
            return ChatResponse(response=fallback_response, status="datasets_fallback")
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        # Return fallback response instead of error
        try:
            nlp_context = fashion_nlp.generate_response_context(request.message)
            dataset_insights = dataset_processor.get_dataset_insights(request.message)
            fallback_response = get_enhanced_fallback_response_with_datasets(
                request.message, nlp_context, dataset_insights, []
            )
        except:
            fallback_response = get_fallback_response(request.message)
        return ChatResponse(response=fallback_response, status="fallback")

def get_enhanced_fallback_response_with_datasets(message: str, nlp_context: dict, dataset_insights: dict, image_colors: list) -> str:
    """
    Enhanced fallback response using NLP context and dataset insights
    """
    intent = nlp_context.get('intent', 'general_fashion')
    sentiment = nlp_context.get('sentiment', {}).get('overall_sentiment', 'neutral')
    entities = nlp_context.get('entities', {})
    
    # Start with semantic matches if available (prominent display)
    response = ""
    if dataset_insights['similar_outfits']:
        response += "### 💎 Stylette Semantic Match Analysis\n"
        response += f"**Found {len(dataset_insights['similar_outfits'])} similar styles from your dataset:**\n\n"
        
        for i, outfit in enumerate(dataset_insights['similar_outfits'], 1):
            similarity_score = outfit.get('similarity_score', 0)
            outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
            
            # Extract key features for explanation
            clothing_types = ', '.join(outfit.get('clothing_types', [])[:2])
            colors = ', '.join(outfit.get('colors', [])[:2])
            occasions = ', '.join(outfit.get('occasions', [])[:1])
            
            response += f"**{i}. {outfit_name}** (Match Score: {similarity_score:.1%})\n"
            response += f"   • Type: {clothing_types}\n"
            if colors:
                response += f"   • Colors: {colors}\n"
            if occasions:
                response += f"   • Occasion: {occasions}\n"
            response += "\n"
        response += "---\n\n"
    
    # Build response based on intent with dataset enhancement
    if intent == 'outfit_advice':
        response += "**Outfit Styling Advice (Dataset-Enhanced)! ✨**\n\n"
        
        # Check for specific clothing items mentioned
        if entities.get('clothing_types'):
            items = ', '.join(entities['clothing_types'])
            response += f"I see you're asking about {items}! Here's what our fashion database suggests:\n\n"
        
        response += "**General Styling Rules:**\n"
        response += "• Balance proportions (fitted + loose)\n"
        response += "• Stick to 2-3 colors max\n"
        response += "• Add one statement piece\n"
        response += "• Confidence is key! 💕\n\n"
        
        if image_colors:
            response += f"**Color Analysis (Detected: {', '.join(set(image_colors))}):**\n"
            response += "• These colors work well with neutrals\n"
            response += "• Consider complementary color combinations\n"
            response += "• Add metallic accessories for elegance\n\n"
        
        if entities.get('colors'):
            colors = ', '.join(entities['colors'])
            response += f"**Color Coordination for {colors}:**\n"
            color_recs = dataset_insights['color_recommendations']
            if color_recs['status'] == 'success':
                response += f"Based on {color_recs['total_profiles']} body profiles in our dataset:\n"
                if 'recommendations' in color_recs:
                    recs = color_recs['recommendations']
                    if 'top_bottom_combinations' in recs:
                        for combo in recs['top_bottom_combinations'][:2]:
                            response += f"• {combo['top'].title()} + {combo['bottom'].title()} ({combo['occasion']})\n"
            else:
                response += "• Black goes with everything\n"
                response += "• White is universally flattering\n"
                response += "• Navy pairs beautifully with most colors\n"
            response += "\n"
            
    elif intent == 'color_matching':
        response += "**Color Matching Guide (Dataset-Powered)! 🎨**\n\n"
        if entities.get('colors'):
            colors = entities['colors']
            response += f"Great question about {', '.join(colors)}!\n\n"
        
        color_recs = dataset_insights['color_recommendations']
        if color_recs['status'] == 'success':
            response += f"**Database Insights** (from {color_recs['total_profiles']} profiles):\n"
            if 'recommendations' in color_recs:
                recs = color_recs['recommendations']
                if 'top_bottom_combinations' in recs:
                    response += "**Proven Color Combinations:**\n"
                    for combo in recs['top_bottom_combinations']:
                        response += f"• {combo['top'].title()} + {combo['bottom'].title()} = {combo['occasion']}\n"
                    response += "\n"
        
        response += "**Universal Color Rules:**\n"
        response += "• Black + white = timeless\n"
        response += "• Navy + white = classic\n"
        response += "• Denim + any bright color = fun\n"
        response += "• Monochrome = sophisticated\n\n"
        
    elif intent == 'occasion_dressing':
        occasions = entities.get('occasions', [])
        if occasions:
            response += f"**Dressing for {', '.join(occasions).title()}! 👗**\n\n"
        else:
            response += "**Occasion Dressing Guide (Dataset-Enhanced)! 👗**\n\n"
        
        # Add insights from similar outfits in dataset
        if dataset_insights['similar_outfits']:
            response += "**Inspiration from Our Collection:**\n"
            for outfit in dataset_insights['similar_outfits'][:3]:
                outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
                if outfit['ethnic_wear']:
                    response += f"• {outfit_name} (Perfect for traditional occasions)\n"
                else:
                    response += f"• {outfit_name} (Great for western occasions)\n"
            response += "\n"
            
        response += "**Quick Occasion Guide:**\n"
        response += "• **Casual:** Jeans + nice top + sneakers\n"
        response += "• **Work:** Blazer + blouse + trousers\n"
        response += "• **Party:** Dress + heels + statement jewelry\n"
        response += "• **Date:** Something that makes you feel confident!\n\n"
        
    else:
        response += get_fallback_response(message)
        
        # Enhance with dataset stats
        response += "\n\n**💎 Our Fashion Database:**\n"
        stats = dataset_insights['dataset_stats']
        response += f"• {stats['total_fashion_images']} fashion images analyzed\n"
        response += f"• {stats['ethnic_wear_count']} ethnic wear styles\n"
        response += f"• {stats['western_wear_count']} western wear styles\n"
        response += f"• {stats['body_profiles']} body profile insights\n"
    
    # Add sentiment-appropriate closing
    if sentiment == 'positive':
        response += "\nYou're going to look amazing! Our dataset analysis confirms it! ✨"
    elif sentiment == 'negative' or sentiment == 'uncertain':
        response += "\nDon't worry! Our fashion database has thousands of examples to inspire you. Fashion is all about experimenting! 💕"
    else:
        response += f"\nThis analysis is powered by our comprehensive fashion database with {dataset_insights['dataset_stats']['total_fashion_images']} images! 🌟"
        
    return response

def get_enhanced_fallback_response(message: str, nlp_context: dict) -> str:
    """
    Enhanced fallback response using NLP context
    """
    intent = nlp_context.get('intent', 'general_fashion')
    sentiment = nlp_context.get('sentiment', {}).get('overall_sentiment', 'neutral')
    entities = nlp_context.get('entities', {})
    
    # Build response based on intent
    if intent == 'outfit_advice':
        response = "**Outfit Styling Advice! ✨**\n\n"
        
        # Check for specific clothing items mentioned
        if entities.get('clothing_types'):
            items = ', '.join(entities['clothing_types'])
            response += f"I see you're asking about {items}! Here are some styling tips:\n\n"
        
        response += "**General Styling Rules:**\n"
        response += "• Balance proportions (fitted + loose)\n"
        response += "• Stick to 2-3 colors max\n"
        response += "• Add one statement piece\n"
        response += "• Confidence is key! 💕\n\n"
        
        if entities.get('colors'):
            colors = ', '.join(entities['colors'])
            response += f"**Color Coordination for {colors}:**\n"
            response += "• Black goes with everything\n"
            response += "• White is universally flattering\n"
            response += "• Navy pairs beautifully with most colors\n\n"
            
    elif intent == 'color_matching':
        response = "**Color Matching Guide! 🎨**\n\n"
        if entities.get('colors'):
            colors = entities['colors']
            response += f"Great question about {', '.join(colors)}!\n\n"
        
        response += "**Universal Color Rules:**\n"
        response += "• Black + white = timeless\n"
        response += "• Navy + white = classic\n"
        response += "• Denim + any bright color = fun\n"
        response += "• Monochrome = sophisticated\n\n"
        
    elif intent == 'occasion_dressing':
        occasions = entities.get('occasions', [])
        if occasions:
            response = f"**Dressing for {', '.join(occasions).title()}! 👗**\n\n"
        else:
            response = "**Occasion Dressing Guide! 👗**\n\n"
            
        response += "**Quick Occasion Guide:**\n"
        response += "• **Casual:** Jeans + nice top + sneakers\n"
        response += "• **Work:** Blazer + blouse + trousers\n"
        response += "• **Party:** Dress + heels + statement jewelry\n"
        response += "• **Date:** Something that makes you feel confident!\n\n"
        
    else:
        response = get_fallback_response(message)
    
    # Add sentiment-appropriate closing
    if sentiment == 'positive':
        response += "You're going to look amazing! ✨"
    elif sentiment == 'negative' or sentiment == 'uncertain':
        response += "Don't worry, fashion is all about experimenting and finding what makes YOU feel great! 💕"
    else:
        response += "Feel free to ask me anything about fashion - I'm here to help! 🌟"
        
    return response

def get_fallback_response(message: str) -> str:
    """
    Provide fallback fashion advice when AI service is unavailable
    """
    message_lower = message.lower()
    
    if "cute" in message_lower or "adorable" in message_lower:
        return """**Cute Outfit Ideas! 🎀**

Here are some adorable looks to try:

**Cute Casual:**
• Pastel sweater + high-waisted jeans + white sneakers
• Floral mini dress + denim jacket + ankle boots
• Oversized hoodie + bike shorts + chunky sneakers

**Cute Date Night:**
• Off-shoulder top + midi skirt + heeled sandals
• Fit-and-flare dress in soft pink or lavender

**Styling Tips:**
• Colors: pastels, soft pinks, baby blues, lavender
• Add cute accessories: hair clips, delicate jewelry
• Keep makeup fresh and natural!

You're going to look SO cute! 💕✨"""
    
    elif "professional" in message_lower or "interview" in message_lower:
        return """**Professional Look Guide! 💼**

**Interview Ready:**
• Blazer + blouse + tailored trousers + closed-toe heels
• Shift dress + blazer + pumps
• Button-up shirt + pencil skirt + flats

**Colors:** Navy, black, gray, white, beige
**Rules:** Minimal jewelry, closed-toe shoes, neat hair

You've got this! Good luck! 🌟"""
    
    elif "party" in message_lower or "night out" in message_lower:
        return """**Party Perfect Looks! 🎉**

**Party Ready:**
• Sequin dress + strappy heels + clutch
• Bodycon dress + statement jewelry + pumps
• Crop top + leather pants + heeled boots

**Colors:** Metallics, black, red, electric blue
**Tips:** Bold makeup, statement earrings, comfortable heels

Dance the night away! 💃🔥"""
    
    else:
        return """**Fashion Analysis Complete! ✨**

I'd love to help you with your fashion question! Here are some general styling tips:

**Universal Tips:**
• Balance proportions (fitted + loose)
• Choose 2-3 colors max
• Accessories can make or break an outfit
• Confidence is your best accessory!

**Color Combinations That Always Work:**
• Black + white + one accent color
• Navy + white + gold/silver
• Denim + white + any bright color

Feel free to ask more specific questions about styling, colors, or occasions! 💕"""

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    message: Optional[str] = Form(None)
):
    """
    Analyze a single uploaded image using both Gemini AI and local datasets
    """
    try:
        # Save uploaded image temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Read and process the uploaded image for Gemini
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Analyze image colors using our dataset processor
        color_analysis = dataset_processor.analyze_uploaded_image_colors(temp_path)
        
        # Get insights from our datasets
        dataset_insights = dataset_processor.get_dataset_insights(message or "analyze this outfit")
        
        # Prepare enhanced prompt with dataset information
        prompt = f"""You are a professional fashion stylist with access to extensive fashion datasets. 

User's question: {message or 'How does this look? Any styling suggestions?'}

DATASET ANALYSIS RESULTS:
- Dominant colors in image: {color_analysis.get('primary_color', 'unknown')}
- Color breakdown: {color_analysis.get('color_percentages', {})}
- Similar outfits in our dataset: {len(dataset_insights['similar_outfits'])} matches found
- Dataset recommendations: {dataset_insights['color_recommendations']['status']}

Based on this analysis and our fashion dataset knowledge, provide:
1. **Item Description**: What item do you see?
2. **Color Analysis**: Dominant colors and their harmony
3. **Dataset Matching**: How this compares to similar items in our collection
4. **Styling Suggestions**: How to wear this item (enhanced by dataset insights)
5. **Color Coordination**: What colors work with the detected palette
6. **Complete the Look**: What to pair it with (based on dataset patterns)
7. **Occasion**: Where to wear this
8. **Pro Tips**: Styling hacks from our fashion database

Be enthusiastic and reference the dataset insights where relevant!"""

        # Generate response using Gemini with enhanced prompt
        try:
            response = model.generate_content([prompt, image])
            gemini_response = response.text if response.text else None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            gemini_response = None
        
        # Create comprehensive response
        if gemini_response:
            # Enhance Gemini response with dataset information
            enhanced_response = gemini_response + "\n\n"
            
            if dataset_insights['similar_outfits']:
                enhanced_response += "**💎 Similar Styles in Our Collection:**\n"
                for i, outfit in enumerate(dataset_insights['similar_outfits'][:3]):
                    enhanced_response += f"{i+1}. {outfit['filename'].replace('.jpg', '').replace('_', ' ').title()}\n"
                enhanced_response += "\n"
            
            if color_analysis['dominant_colors']:
                enhanced_response += "**🎨 Color Analysis (From Your Image):**\n"
                for color_info in color_analysis['dominant_colors'][:3]:
                    enhanced_response += f"• {color_info['color_name'].title()}: {color_info['percentage']}%\n"
                enhanced_response += "\n"
            
            enhanced_response += f"**📊 Dataset Insights:** Analyzed against {dataset_insights['dataset_stats']['total_fashion_images']} fashion images in our database!"
            
            return {"response": enhanced_response, "status": "success_with_datasets", "dataset_analysis": dataset_insights}
        else:
            # Pure dataset-based fallback response
            fallback_response = generate_dataset_based_response(color_analysis, dataset_insights, message)
            return {"response": fallback_response, "status": "datasets_only", "dataset_analysis": dataset_insights}
            
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"response": "I'd love to help analyze your fashion item! Please try uploading the image again.", "status": "error"}
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

def generate_dataset_based_response(color_analysis: Dict, dataset_insights: Dict, message: str) -> str:
    """Generate response purely from dataset analysis"""
    response = "**Fashion Analysis (Dataset-Powered) ✨**\n\n"
    
    # Color analysis
    if color_analysis['dominant_colors']:
        response += "**🎨 Color Analysis:**\n"
        primary_color = color_analysis['primary_color']
        response += f"Primary Color: {primary_color.title()}\n"
        
        color_recommendations = dataset_insights['color_recommendations']
        if color_recommendations['status'] == 'success':
            response += f"Based on our body metrics database of {color_recommendations['total_profiles']} profiles:\n"
            if 'recommendations' in color_recommendations:
                recs = color_recommendations['recommendations']
                if 'top_bottom_combinations' in recs:
                    response += "\n**Recommended Color Combinations:**\n"
                    for combo in recs['top_bottom_combinations'][:3]:
                        response += f"• {combo['top'].title()} top + {combo['bottom'].title()} bottom ({combo['occasion']})\n"
        response += "\n"
    
    # Similar outfits from dataset
    if dataset_insights['similar_outfits']:
        response += "**👗 Similar Styles in Our Collection:**\n"
        response += f"Found {len(dataset_insights['similar_outfits'])} similar items:\n"
        for i, outfit in enumerate(dataset_insights['similar_outfits'][:3]):
            outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
            outfit_colors = ', '.join(outfit['colors']) if outfit['colors'] else 'Multi-color'
            response += f"{i+1}. {outfit_name} ({outfit_colors})\n"
        response += "\n"
    
    # Dataset statistics
    stats = dataset_insights['dataset_stats']
    response += "**📊 Dataset Insights:**\n"
    response += f"• Total Fashion Images: {stats['total_fashion_images']}\n"
    response += f"• Ethnic Wear Collection: {stats['ethnic_wear_count']} items\n"
    response += f"• Western Wear Collection: {stats['western_wear_count']} items\n"
    response += f"• Body Profile Database: {stats['body_profiles']} profiles\n\n"
    
    # General styling advice
    response += "**✨ Styling Suggestions:**\n"
    if primary_color in ['black', 'white', 'navy', 'gray']:
        response += "• Neutral colors like this are super versatile!\n"
        response += "• Add a pop of color with accessories\n"
        response += "• Perfect base for both casual and formal looks\n"
    else:
        response += f"• {primary_color.title()} is a bold choice - pair with neutrals\n"
        response += "• Keep accessories minimal to let the color shine\n"
        response += "• Great for making a statement!\n"
    
    response += "\n**💡 This analysis is powered by our comprehensive fashion datasets including body metrics, color science, and real fashion collections!**"
    
    return response

@app.get("/api/dataset-stats")
async def get_dataset_stats():
    """Get statistics about loaded datasets"""
    try:
        insights = dataset_processor.get_dataset_insights("general")
        
        # Additional validation info
        validation_info = {
            "base_path": dataset_processor.base_path,
            "base_path_exists": os.path.exists(dataset_processor.base_path),
            "body_metrics_loaded": dataset_processor.body_metrics_data is not None,
            "fashion_images_indexed": len(dataset_processor.fashion_images_metadata) > 0,
            "dataset_directories": {}
        }
        
        # Check each dataset directory
        for dirname in ["body metrics", "women fashion", "body shape wise clothes"]:
            dir_path = os.path.join(dataset_processor.base_path, dirname)
            validation_info["dataset_directories"][dirname] = {
                "exists": os.path.exists(dir_path),
                "path": dir_path,
                "file_count": len(os.listdir(dir_path)) if os.path.exists(dir_path) else 0
            }
        
        return {
            "status": "success",
            "stats": insights['dataset_stats'],
            "validation": validation_info,
            "recommendations_available": insights['color_recommendations']['status'] == 'success'
        }
    except Exception as e:
        logger.error(f"Error getting dataset stats: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "base_path": getattr(dataset_processor, 'base_path', 'unknown'),
            "suggestion": "Check FASHION_ANALYZER_PATH environment variable or dataset file locations"
        }

@app.post("/api/color-recommendations")
async def get_color_recommendations(preferences: dict):
    """Get color recommendations from body metrics dataset"""
    try:
        recommendations = dataset_processor.get_color_recommendations(preferences)
        return recommendations
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/find-similar")
async def find_similar_outfits(request: dict):
    """Find similar outfits from dataset"""
    try:
        query = request.get('query', '')
        colors = request.get('colors', [])
        
        similar_outfits = dataset_processor.find_similar_outfits(query, colors)
        
        return {
            "status": "success",
            "query": query,
            "found": len(similar_outfits),
            "outfits": similar_outfits
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"✨ Starting Stylette - AI Fashion Stylist API...")
    logger.info(f"🌐 Server will be available at: http://{host}:{port}")
    logger.info(f"📚 API docs at: http://{host}:{port}/docs")
    logger.info(f"📁 Dataset path: {dataset_processor.base_path}")
    logger.info(f"📊 Loaded {len(dataset_processor.fashion_images_metadata)} fashion images")
    
    uvicorn.run(app, host=host, port=port)
