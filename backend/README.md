# Fashion Analyzer AI - Backend

## 🌟 Features

- **Gemini AI Integration**: Advanced image analysis and fashion recommendations
- **Dataset Integration**: Uses your actual fashion datasets for enhanced recommendations
- **NLP Analysis**: Natural language processing for understanding user queries
- **Color Analysis**: Extract and analyze colors from uploaded images
- **Fashion Matching**: Find similar outfits from your dataset collection

## 📊 Datasets Integrated

1. **Fashion-MNIST** (`Fashion 1/`) - 70k clothing images, 10 categories
2. **DeepFashion2** (`DeepFashion2-master/`) - Advanced fashion detection
3. **Body Metrics** (`body metrics/`) - Color recommendations based on body profiles
4. **Women Fashion** (`women fashion/`) - Real fashion images (ethnic & western)
5. **Body Shape Clothes** (`body shape wise clothes/`) - Body type specific styling

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **Configure API Key**:
   ```bash
   # Edit .env file
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Start Server**:
   ```bash
   python main.py
   # Or use: uvicorn main:app --reload
   ```

4. **Access API**:
   - Server: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 📡 API Endpoints

### Core Endpoints

- `POST /api/chat` - Chat with AI (text + images)
- `POST /api/analyze-image` - Analyze single image with datasets
- `GET /api/health` - Health check

### Dataset Endpoints

- `GET /api/dataset-stats` - Get dataset statistics
- `POST /api/color-recommendations` - Get color recommendations
- `POST /api/find-similar` - Find similar outfits from dataset

## 🔧 New Dataset Features

### What's Different Now?

**Before**: Pure Gemini AI responses
**Now**: Gemini AI + Your Dataset Analysis

### Enhanced Features:

1. **Color Analysis**: 
   - Extracts dominant colors from uploaded images
   - Matches against body metrics dataset for personalized recommendations

2. **Fashion Matching**:
   - Finds similar outfits from your `women fashion/` collection
   - Matches based on clothing type, color, and style

3. **Dataset Insights**:
   - References actual dataset statistics in responses
   - Uses body profile data for color recommendations
   - Ethnic vs Western wear classification

4. **NLP Enhancement**:
   - Understands fashion terminology
   - Intent detection (outfit advice, color matching, etc.)
   - Sentiment analysis for personalized responses

## 🎨 Example API Calls

### Analyze Image with Dataset Integration
```bash
curl -X POST "http://localhost:8000/api/analyze-image" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@outfit.jpg" \
     -F "message=How does this look?"
```

### Chat with Dataset Enhancement
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What should I wear for a wedding?",
       "images": ["data:image/jpeg;base64,/9j/4AAQ..."]
     }'
```

### Get Dataset Statistics
```bash
curl -X GET "http://localhost:8000/api/dataset-stats"
```

## 📝 Response Format

All responses now include dataset insights:

```json
{
  "response": "Fashion analysis with dataset insights...",
  "status": "success_with_datasets",
  "dataset_analysis": {
    "similar_outfits": [...],
    "color_recommendations": {...},
    "dataset_stats": {
      "total_fashion_images": 150,
      "ethnic_wear_count": 75,
      "western_wear_count": 75,
      "body_profiles": 1000
    }
  }
}
```

## 🔍 How It Works

1. **User uploads image/asks question**
2. **NLP analyzes user intent and entities**
3. **Dataset processor extracts colors and finds similar outfits**
4. **Gemini AI generates response with dataset context**
5. **Response enhanced with dataset insights**

## 🛠️ Development

### File Structure
```
backend/
├── main.py              # FastAPI application
├── nlp_utils.py         # NLP processing
├── dataset_processor.py # Dataset integration
├── requirements.txt     # Dependencies
├── start.sh            # Startup script
└── .env.example        # Environment template
```

### Key Classes

- `FashionNLP`: Natural language processing for fashion queries
- `DatasetProcessor`: Integrates and analyzes fashion datasets
- `ColorAnalyzer`: Extracts and analyzes colors from images

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **NLTK Data Missing**: Run the download script
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

3. **Dataset Not Loading**: Check file paths in `dataset_processor.py`

4. **Gemini API Errors**: Verify your API key in `.env`

### Debug Mode:
```bash
# Start with debug logging
export PYTHONPATH="${PYTHONPATH}:."
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py
```

## 🎯 Next Steps

1. **Add More Datasets**: Integrate additional fashion datasets
2. **Custom Models**: Train custom classification models
3. **Advanced NLP**: Add more sophisticated fashion understanding
4. **Real-time Processing**: Optimize for faster responses

---

**Now your Fashion Analyzer actually uses your datasets! 🎉**
