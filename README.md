# 🎬 CineSmart AI - Advanced Movie Recommendation System

A comprehensive, AI-powered movie recommendation system with advanced features, built with Python and Streamlit. Specializes in South Indian cinema while supporting global content.

## ✨ Key Features

### 🤖 Advanced AI Recommendations
- **Hybrid Engine**: Combines collaborative filtering (SVD) and content-based filtering (TF-IDF)
- **Smart Recommendations**: Learns from user ratings and preferences
- **Recommendation Explanations**: Understand why movies were suggested
- **Cold Start Handling**: Works even for new users with no rating history

### 🎯 Personalized Experience
- **User Profiles**: Customize preferences for genres, languages, and content types
- **Rating System**: Rate movies to improve recommendation accuracy
- **Smart Watchlist**: Intelligent watchlist with analytics
- **Search History**: Track and reuse previous searches

### 🔍 Advanced Search & Discovery
- **Multi-Filter Search**: Search by title, genre, year, rating, language, and actors
- **Real-time Filtering**: Instant results as you type
- **Sort Options**: Sort by relevance, rating, year, or title
- **Search Suggestions**: Based on your search history

### 📊 Comprehensive Analytics
- **Personal Insights**: Your rating patterns and preferences
- **Content Analytics**: Deep dive into the movie database
- **User Activity**: Track your engagement and discoveries
- **Platform Statistics**: Overall trends and popular content

### 🎭 Rich Content Database
- **11,800+ Movies & Series**: Extensive collection across languages
- **Multi-language Support**: Tamil, Telugu, Malayalam, Kannada, Hindi, English
- **Detailed Metadata**: Cast, genres, ratings, posters, and more
- **Real-time Posters**: Integration with movie databases for images

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd movie-recommendation-system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
*Or use the provided batch file:*
```bash
install_deps.bat
```

3. **Prepare the data:**
```bash
python src/data_preprocessing.py
```

4. **Launch the application:**
```bash
streamlit run app/streamlit_app.py
```
*Or use the provided batch file:*
```bash
run_app.bat
```

5. **Open your browser** and navigate to `http://localhost:8501`

## 🏗️ Project Architecture

```
movie-recommendation-system/
├── 📱 app/
│   └── streamlit_app.py          # Main Streamlit application
├── 🧠 src/
│   ├── models/
│   │   ├── cbf.py               # Content-based filtering
│   │   ├── cf.py                # Collaborative filtering
│   │   ├── cold_start.py        # Cold start problem handling
│   │   └── hybrid.py            # Hybrid recommendation system
│   ├── services/
│   │   ├── analytics.py         # Analytics and insights
│   │   ├── search.py            # Search functionality
│   │   └── tmdb.py              # TMDB API integration
│   ├── data/
│   │   └── indian_movies_generator.py  # Data generation utilities
│   ├── auth.py                  # User authentication
│   ├── database.py              # Database operations
│   ├── data_layer.py            # Data access layer
│   └── data_preprocessing.py    # Data preprocessing pipeline
├── 📊 data/
│   ├── raw/                     # Raw datasets
│   │   ├── ml-latest-small/     # MovieLens dataset
│   │   ├── indian_movies.csv    # Indian movies database
│   │   ├── south_indian_movies_ext.csv  # Extended South Indian content
│   │   └── synthetic_*.csv      # Generated synthetic data
│   └── processed/               # Processed data for ML models
├── 🛠️ Configuration Files
│   ├── requirements.txt         # Python dependencies
│   ├── install_deps.bat        # Windows dependency installer
│   └── run_app.bat             # Windows app launcher
└── 📚 README.md                # This file
```

## 🧠 How the AI Works

### 1. **Data Processing Pipeline**
- **Multi-source Integration**: MovieLens + Custom Indian database + Synthetic data
- **Feature Engineering**: TF-IDF vectorization of movie metadata
- **Similarity Computation**: Cosine similarity matrix for 11,800+ movies
- **Model Training**: SVD matrix factorization for collaborative filtering

### 2. **Recommendation Algorithms**

#### 🎯 Content-Based Filtering
```python
# Uses TF-IDF on combined features:
features = genres + language + actors + type + title
similarity_matrix = cosine_similarity(tfidf_matrix)
```

#### 👥 Collaborative Filtering
```python
# SVD Matrix Factorization:
user_item_matrix → SVD → predicted_ratings
```

#### 🔄 Hybrid Approach
```python
final_score = α × content_score + β × collaborative_score
# Where α and β are learned weights
```

### 3. **Smart Features**
- **Preference Learning**: Adapts to user ratings in real-time
- **Context Awareness**: Considers user's language and genre preferences
- **Diversity Optimization**: Ensures recommendation variety
- **Explanation Generation**: Provides reasoning for each recommendation

## 🎮 User Guide

### 🏠 Home Page
- **Trending Section**: Discover popular content
- **Personal Recommendations**: AI-curated suggestions based on your activity
- **Quick Recommendations**: Get instant suggestions by selecting a movie you liked

### 🔍 Advanced Search
- **Multi-criteria Filtering**: Combine multiple filters for precise results
- **Smart Sorting**: Sort by relevance, rating, year, or alphabetically
- **Search History**: Quickly access previous searches
- **Result Limits**: Control the number of results displayed

### 👤 My Profile
- **Preference Settings**: Set favorite genres, languages, and content types
- **Rating History**: View and manage all your movie ratings
- **Personalized Recommendations**: Get suggestions based on your profile
- **Activity Statistics**: Track your engagement metrics

### 📊 Analytics Dashboard
- **Overview Tab**: General statistics and distributions
- **Content Analysis**: Deep dive into the movie database
- **User Insights**: Your personal viewing patterns and preferences
- **Search Trends**: Analysis of search behavior and popular content

## 🛠️ Technical Specifications

### **Backend Technologies**
- **Python 3.10+**: Core programming language
- **Pandas & NumPy**: Data manipulation and numerical computing
- **Scikit-learn**: Machine learning algorithms and TF-IDF vectorization
- **Surprise Library**: Collaborative filtering and SVD implementation
- **SQLite**: Local database for user data persistence

### **Frontend Technologies**
- **Streamlit**: Interactive web application framework
- **Custom CSS**: Enhanced UI/UX with responsive design
- **Session State Management**: Persistent user data across sessions
- **Real-time Updates**: Dynamic content updates without page refresh

### **Data Sources**
- **MovieLens ml-latest-small**: 9,000+ movies with 100,000+ ratings
- **Custom Indian Movies Database**: 2,000+ Bollywood and regional films
- **South Indian Extended Collection**: 60+ recent movies and series
- **TMDB Integration**: Movie posters and additional metadata

### **Performance Optimizations**
- **Caching**: Streamlit caching for model loading and data processing
- **Efficient Storage**: Pickle serialization for processed data
- **Matrix Operations**: NumPy optimized similarity computations
- **Lazy Loading**: On-demand poster fetching

## 🎯 Advanced Features

### 🤖 AI-Powered Recommendations
- **Multi-algorithm Fusion**: Combines 3 different recommendation approaches
- **Real-time Learning**: Adapts to user behavior instantly
- **Explanation Engine**: Provides reasoning for each recommendation
- **Diversity Control**: Ensures variety in recommendations

### 📱 User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Automatic theme adaptation
- **Intuitive Navigation**: Easy-to-use interface with clear sections
- **Fast Performance**: Optimized for quick response times

### 🔍 Search & Discovery
- **Fuzzy Matching**: Find movies even with partial or misspelled names
- **Multi-language Search**: Search in different languages
- **Advanced Filters**: Combine multiple criteria for precise results
- **Smart Suggestions**: AI-powered search suggestions

### 📊 Analytics & Insights
- **Personal Analytics**: Understand your viewing preferences
- **Content Insights**: Explore the movie database statistics
- **Trend Analysis**: Discover popular content and patterns
- **Export Capabilities**: Download your data and insights

## 🚀 Recent Updates & Fixes

### ✅ Fixed Issues
- **Poster Display**: Fixed broken poster URLs and added comprehensive poster database
- **Movie Categorization**: Corrected misplaced Hollywood movies in South Indian category
- **Series Data**: Fixed "OFFICE" series name and proper Tamil categorization
- **Language Assignment**: Resolved Hindi movies being incorrectly labeled as English
- **Data Conflicts**: Eliminated duplicate movie IDs between datasets

### 🆕 New Features Added
- **Advanced Search Page**: Multi-criteria search with filters and sorting
- **User Profile System**: Comprehensive preference management
- **Rating System**: Interactive movie rating with real-time learning
- **Smart Recommendations**: AI-powered suggestions based on user behavior
- **Recommendation Explanations**: Understand why movies were suggested
- **Enhanced Analytics**: Multi-tab analytics dashboard with personal insights
- **Movie Details Modal**: Detailed movie information popup
- **Search History**: Track and reuse previous searches
- **Watchlist Management**: Enhanced watchlist with analytics

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
- Use the issue tracker to report bugs
- Include detailed steps to reproduce
- Provide system information and error messages

### 💡 Feature Requests
- Suggest new features through issues
- Explain the use case and expected behavior
- Consider implementation complexity

### 🔧 Code Contributions
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MovieLens** by GroupLens Research for the comprehensive movie dataset
- **TMDB** for movie metadata and poster images
- **Streamlit** team for the amazing web app framework
- **Scikit-learn** and **Surprise** communities for ML libraries
- **Open Source Community** for inspiration and support

---

**Made with ❤️ for movie lovers everywhere**

*Discover your next favorite movie with CineSmart AI!*