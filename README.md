# Stylette - AI Fashion Stylist

An intelligent personal fashion styling assistant that combines **Google Gemini AI** with **real dataset processing** to provide personalized styling recommendations based on your actual fashion image collection.
Hey lets make some changes 

## 🌟 What is Stylette?

**Your Personal AI Fashion Stylist - Powered by Real Data**

- ✨ **Analyze outfit photos** instantly
- ✨ **Get personalized styling advice** tailored to your preferences  
- ✨ **Color analysis & recommendations** using advanced computer vision
- ✨ **Find similar styles** from 100+ curated fashion images
- ✨ **Smart matching** against body metrics & color science data

## 🏗️ System Architecture

```
Frontend (React + Tailwind) ← → FastAPI Backend ← → Dataset Processor
                                        ↓
                            Google Gemini AI + Your Datasets
                                   ↓
                        Stylette Personalized Recommendations
```

## 📊 Datasets Currently Integrated

1. **Women Fashion Collection** (104 images)
   - Anarkali suits, sarees, western dresses
   - Automatically indexed and searchable

2. **Body Metrics & Colors** (CSV data)
   - 1000+ body profiles with color recommendations
   - Scientific color matching data

3. **Body Shape Wise Clothes** (7 reference images)
   - Body type specific styling examples

4. **Fashion-MNIST Integration** (Clothing categories)
   - 10 standardized clothing types
   - Enhanced classification accuracy

## ✨ Features

### **Outfit Analysis with Dataset Integration**
- **Color Extraction**: Real-time dominant color analysis using OpenCV
- **Similar Style Matching**: Finds matches from curated collection
- **Body Metrics Integration**: Color recommendations from actual data
- **Style Classification**: Ethnic vs Western wear detection

### **Enhanced AI Styling Responses**
- **Dataset Context**: Stylette references your actual collection
- **Personalized Advice**: Based on your specific image metadata
- **Smart Matching**: "Found 8 similar outfits in your collection"
- **Color Science**: Recommendations backed by body metrics data

### **Natural Language Processing**
- **Intent Recognition**: Understands outfit advice, color matching, etc.
- **Fashion Entity Extraction**: Detects clothing types, colors, occasions
- **Sentiment Analysis**: Adapts responses to user confidence level
- **400+ Fashion Keywords**: Comprehensive fashion vocabulary

## 💻 Quick Start

### Backend (FastAPI + Datasets)
```bash
cd backend
chmod +x start.sh
./start.sh
# Server starts at http://localhost:8000
```

### Frontend (React + Tailwind)
```bash
cd frontend  
npm install
npm run dev
# Frontend at http://localhost:5173
```

### Configuration
```bash
# Edit backend/.env
GEMINI_API_KEY=your_api_key_here
FASHION_ANALYZER_PATH=/path/to/your/datasets  # Optional
```

## 🔧 How Dataset Processing Works

### **Automatic Image Indexing**
```python
# System automatically:
1. Scans women fashion/ directory → 104 images found
2. Extracts metadata from filenames
3. Classifies ethnic vs western wear  
4. Indexes colors, styles, clothing types
```

### **Real-Time Color Analysis**
```python
# When you upload an image:
1. OpenCV extracts dominant colors
2. Converts RGB to semantic color names
3. Matches against body metrics dataset
4. Provides personalized color recommendations
```

### **Smart Outfit Matching**  
```python
# System finds similar outfits by:
1. Text similarity matching
2. Color pattern matching
3. Clothing type matching
4. Style preference matching (ethnic/western)
```

## 📡 API Endpoints

### **Enhanced Endpoints**
- `POST /api/chat` - Chat with dataset integration
- `POST /api/analyze-image` - Image analysis + dataset matching
- `GET /api/dataset-stats` - View loaded dataset statistics
- `POST /api/color-recommendations` - Body metrics based color advice
- `POST /api/find-similar` - Find similar outfits in collection

### **Example Response**
```json
{
  "response": "Based on your red anarkali, I found 8 similar outfits in your collection...",
  "status": "success_with_datasets", 
  "dataset_analysis": {
    "similar_outfits": [...],
    "dominant_colors": ["red", "gold"],
    "dataset_stats": {
      "total_fashion_images": 104,
      "ethnic_wear_count": 67,
      "body_profiles": 1000
    }
  }
}
```

## 💡 How to Use

### **Analyze Real Fashion Images**
1. Upload clothing images through the React interface
2. System extracts colors using OpenCV computer vision
3. Finds similar outfits from your 104-image collection
4. AI provides recommendations enhanced with dataset insights

### **Ask Dataset-Powered Questions**
- "What colors go with this red anarkali?" → References body metrics data
- "Show me similar ethnic wear" → Searches your indexed collection
- "Professional outfit ideas" → Uses both AI + your dataset examples

### **Get Personalized Body Type Advice**
- Recommendations backed by 1000+ body profiles from CSV data
- Color suggestions based on scientific skin tone matching
- Style advice using your actual fashion image collection

## 🔬 Technical Architecture

### **Backend Stack**
- **FastAPI**: High-performance Python backend
- **Dataset Processor**: Custom image indexing and analysis
- **NLP Engine**: Fashion-specific natural language processing
- **Color Analyzer**: OpenCV-based computer vision
- **Gemini AI Integration**: Enhanced with dataset context

### **Frontend Stack** 
- **React 19**: Modern component-based UI
- **Tailwind CSS**: Utility-first styling
- **Vite**: Fast development and build tool
- **TypeScript**: Type-safe development

### **Dataset Integration**
- **OpenCV**: Real-time color extraction from images
- **Pandas**: CSV data processing for body metrics
- **Scikit-learn**: Text similarity and outfit matching
- **NLTK**: Natural language processing for fashion terms

## 📈 Dataset Statistics

**Currently Loaded**:
- ✅ 104 fashion images indexed and searchable
- ✅ 1000+ body profiles with color recommendations  
- ✅ 67 ethnic wear items classified
- ✅ 37 western wear items classified
- ✅ 13 distinct clothing categories recognized
- ✅ 20+ color variations detected and mapped

## 🎯 What Makes This Special

### **Real Dataset Usage** (Not Just AI):
1. **Actual Fashion Images**: Your 104 images are indexed and searchable
2. **Scientific Color Analysis**: OpenCV extracts real color data
3. **Body Metrics Integration**: 1000+ profiles provide data-backed recommendations  
4. **Smart Matching**: Finds visually and contextually similar outfits

### **Hybrid Intelligence**:
- **Gemini AI**: Advanced reasoning and natural language understanding
- **Computer Vision**: Real color extraction and image analysis
- **Data Science**: Statistical analysis of fashion patterns
- **Machine Learning**: Outfit similarity and recommendation algorithms

## 📁 Project Structure

```
Fashion-Analyzer-AI/
├── 🏠 Main Application
│   ├── README.md                    # This file - system overview
│   ├── SYSTEM_ARCHITECTURE.md      # Detailed technical architecture  
│   └── DATASET_INTEGRATION.md      # How datasets are integrated
│
├── 🖥️ Backend (FastAPI + Dataset Processing)
│   ├── backend/
│   │   ├── main.py                  # FastAPI server with Gemini AI
│   │   ├── dataset_processor.py     # Core dataset integration
│   │   ├── nlp_utils.py            # Fashion NLP processing
│   │   ├── requirements.txt         # Python dependencies
│   │   ├── start.sh                # Quick startup script
│   │   └── README.md               # Backend documentation
│
├── 🎨 Frontend (React + Tailwind)
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.tsx             # Main React application
│   │   │   └── components/         # React components
│   │   ├── package.json            # Node.js dependencies
│   │   └── README.md              # Frontend documentation
│
└── 📊 Datasets (Your Fashion Data)
    ├── women fashion/               # 104 fashion images (indexed)
    ├── body metrics/               # CSV data + color science
    ├── body shape wise clothes/    # Body type references
    ├── Fashion 1/                  # Fashion-MNIST dataset
    ├── DeepFashion2-master/       # Advanced fashion detection
    └── sustainable fashion/        # Eco-fashion data
```

## 🔧 Development & Deployment

### **Local Development**
```bash
# Start backend
cd backend && ./start.sh

# Start frontend  
cd frontend && npm run dev

# Both running:
# Backend: http://localhost:8000 (with dataset processing)
# Frontend: http://localhost:5173 (React interface)
```

### **Production Deployment**
```bash
# Docker deployment (backend)
cd backend
docker build -t fashion-analyzer-backend .
docker run -p 8000:8000 -v /path/to/datasets:/datasets fashion-analyzer-backend

# Frontend build
cd frontend
npm run build
# Deploy dist/ to your hosting platform
```

### **Environment Configuration**
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key
FASHION_ANALYZER_PATH=/path/to/your/datasets
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com
```

## 🚨 Troubleshooting

### **Dataset Loading Issues**
```bash
# Check dataset status
curl http://localhost:8000/api/dataset-stats

# Expected response:
{
  "status": "success",
  "stats": {
    "total_fashion_images": 104,
    "body_profiles": 1000+,
    "ethnic_wear_count": 67
  }
}
```

### **Common Issues & Solutions**

1. **"No fashion images found"**
   - Set `FASHION_ANALYZER_PATH` environment variable
   - Ensure `women fashion/` directory exists with images

2. **"Body metrics CSV not found"**  
   - Check `body metrics/Profile of Body Metrics and Fashion Colors.csv` exists
   - Verify CSV file is readable

3. **"OpenCV installation failed"**
   - Install system dependencies: `sudo apt-get install libgl1-mesa-glx`
   - Use conda: `conda install opencv`

4. **"Gemini API errors"**
   - Verify API key in `.env` file
   - Check API quota and billing status

## 🎯 Future Enhancements

- [ ] **Custom Model Training**: Train on your specific fashion images
- [ ] **Advanced Color Science**: Skin tone analysis from user photos  
- [ ] **Virtual Wardrobe**: Personal closet management
- [ ] **Shopping Integration**: Links to purchase similar items
- [ ] **Style Quiz**: Automated body type and style preference detection
- [ ] **Trend Analysis**: Track fashion trends from your dataset
- [ ] **Size Recommendations**: Using body metrics for sizing advice

---

## 🎉 What You've Built

**A truly intelligent fashion assistant that:**
- ✅ Actually uses your 104 fashion images (not just generic AI)
- ✅ Analyzes real colors from uploaded photos using computer vision
- ✅ References 1000+ body profiles for scientific recommendations
- ✅ Understands fashion terminology through specialized NLP
- ✅ Combines AI reasoning with your personal dataset collection
- ✅ Provides personalized advice backed by real data

**Your Fashion Analyzer is now powered by YOUR data! 🚀**

Made with ❤️ by Stylette Team
