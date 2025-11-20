from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import base64
from PIL import Image
import io
from typing import List, Optional, Dict
import logging
from pydantic import BaseModel
from nlp_utils import fashion_nlp
from dataset_processor import dataset_processor
from smart_response_generator import smart_generator

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fashion Analyzer AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    images: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    status: str

@app.get("/")
async def root():
    return {"message": "Fashion Analyzer AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat endpoint that handles both text and image analysis with NLP enhancement and dataset integration
    Uses pure NLP and dataset analysis - no external AI APIs
    """
    try:
        # Use NLP to analyze the request
        nlp_context = fashion_nlp.generate_response_context(request.message)
        
        # Get insights from our datasets
        dataset_insights = dataset_processor.get_dataset_insights(request.message)
        
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
        
        # Generate intelligent response using smart NLP generator
        response_text = smart_generator.generate_intelligent_response(
            request.message, nlp_context, dataset_insights, image_colors
        )
        
        return ChatResponse(response=response_text, status="success_nlp_datasets")
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again!",
            status="error"
        )



@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    message: Optional[str] = Form(None)
):
    """
    Analyze a single uploaded image using NLP and local datasets only
    No external AI APIs - pure computer vision and dataset analysis
    """
    try:
        # Save uploaded image temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Analyze image colors using our dataset processor (OpenCV)
        color_analysis = dataset_processor.analyze_uploaded_image_colors(temp_path)
        
        # Extract detected colors
        image_colors = []
        if color_analysis.get('dominant_colors'):
            image_colors = [color['color_name'] for color in color_analysis['dominant_colors'][:3]]
        
        # Get insights from our datasets
        dataset_insights = dataset_processor.get_dataset_insights(message or "analyze this outfit")
        
        # Use NLP to analyze the message
        nlp_context = fashion_nlp.generate_response_context(message or "How does this look?")
        
        # Generate intelligent response using smart generator
        response_text = smart_generator.generate_intelligent_response(
            message or "How does this look? Any styling suggestions?",
            nlp_context,
            dataset_insights,
            image_colors
        )
        
        return {"response": response_text, "status": "success_nlp_datasets", "dataset_analysis": dataset_insights}
            
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"response": "I'd love to help analyze your fashion item! Please try uploading the image again.", "status": "error"}
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass



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
    
    logger.info(f"🚀 Starting Fashion Analyzer API server...")
    logger.info(f"🌐 Server will be available at: http://{host}:{port}")
    logger.info(f"📚 API docs at: http://{host}:{port}/docs")
    logger.info(f"📁 Dataset path: {dataset_processor.base_path}")
    logger.info(f"📊 Loaded {len(dataset_processor.fashion_images_metadata)} fashion images")
    
    uvicorn.run(app, host=host, port=port)
