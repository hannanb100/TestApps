# 🔍 Job Search Application

A Python-based job search application that searches multiple job sites (LinkedIn, Indeed, Glassdoor, ZipRecruiter) for relevant positions based on location and keywords.

## ✨ Features

- **Multi-site search**: Searches LinkedIn, Indeed, Glassdoor, and ZipRecruiter
- **Location-based filtering**: Find jobs in specific cities, states, or remote positions
- **Keyword relevance scoring**: Up to 3 keywords for precise job type matching
- **Job status verification**: Ensures jobs are currently open and accessible
- **Smart ranking**: Results sorted by relevance score
- **Export functionality**: Save results to JSON files with timestamps

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd Jobsearch
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
The application automatically loads from your existing `.env` file in the APPS directory. You can optionally add these keys:

```bash
# Optional API keys for enhanced functionality
LINKEDIN_API_KEY=your_linkedin_api_key
INDEED_API_KEY=your_indeed_api_key
GLASSDOOR_API_KEY=your_glassdoor_api_key
```

### 3. Run the Application
```bash
python job_search.py
```

## 📝 Usage

### Input Requirements
- **Location**: City, state, or "remote" for remote positions
- **Keywords**: Up to 3 job-related keywords (e.g., "python", "developer", "senior")

### Example Session
```
🔍 JOB SEARCH APPLICATION
==================================================
📍 Enter job location (city, state, or 'remote'): San Francisco, CA
🔑 Enter up to 3 job keywords (press Enter after each, or 'done' when finished):
Keyword 1: python
Keyword 2: developer
Keyword 3: senior

📡 Searching LinkedIn...
📡 Searching Indeed...
📡 Searching Glassdoor...
📡 Searching ZipRecruiter...

🎯 Found 20 relevant jobs:
==================================================
```

## 🏗️ Architecture

### Core Components

1. **JobSearchEngine**: Main search orchestrator
2. **JobListing**: Data structure for job information
3. **Site-specific parsers**: HTML parsing for each job site
4. **Relevance scoring**: Algorithm to rank job relevance
5. **Status verification**: Check if jobs are currently open

### Search Flow
1. **Input validation** - Location and keywords
2. **Multi-site search** - Parallel search across job sites
3. **HTML parsing** - Extract job information from search results
4. **Relevance scoring** - Calculate match quality (0.0 - 1.0)
5. **Status verification** - Ensure jobs are currently open
6. **Result ranking** - Sort by relevance score
7. **Output display** - Console output and JSON export

## 🔧 Configuration

### Job Sites Supported
- **LinkedIn**: Professional networking and job board
- **Indeed**: Major job search engine
- **Glassdoor**: Company reviews and job listings
- **ZipRecruiter**: AI-powered job matching

### Relevance Scoring Algorithm
- **Location match**: 30% of total score
- **Keyword relevance**: 50% of total score
- **Recency**: 20% of total score (recent jobs get higher scores)

### Filtering Criteria
- Minimum relevance score: 0.3
- Jobs must be currently open
- Results limited to specified max_results

## 📊 Output Format

### Console Display
```
1. Senior Python Developer
   Company: TechCorp Inc
   Location: San Francisco, CA
   Source: LinkedIn
   Relevance: 0.85
   Status: 🟢 Open
   Salary: $120,000 - $150,000
   URL: https://linkedin.com/jobs/view/12345
```

### JSON Export
Results are saved to timestamped files:
```json
{
  "search_criteria": {
    "location": "San Francisco, CA",
    "keywords": ["python", "developer", "senior"],
    "timestamp": "20241228_143022"
  },
  "jobs": [
    {
      "title": "Senior Python Developer",
      "company": "TechCorp Inc",
      "location": "San Francisco, CA",
      "description": "Job description...",
      "url": "https://linkedin.com/jobs/view/12345",
      "source": "LinkedIn",
      "posted_date": "2024-12-20",
      "salary": "$120,000 - $150,000",
      "job_type": "Full-time",
      "relevance_score": 0.85,
      "is_currently_open": true
    }
  ]
}
```

## 🚧 Current Limitations

### Web Scraping
- **Rate limiting**: 1-second delay between site searches
- **HTML parsing**: Currently uses placeholder implementations
- **Site changes**: Job sites may change their HTML structure

### API Integration
- **LinkedIn API**: Requires developer account and approval
- **Indeed API**: Limited access, requires partnership
- **Glassdoor API**: Restricted access

## 🔮 Future Enhancements

1. **Real HTML parsing** using BeautifulSoup
2. **Selenium automation** for dynamic content
3. **Email notifications** for new job matches
4. **Web interface** with Flask/FastAPI
5. **Database storage** for job history
6. **Advanced filtering** by salary, company size, etc.

## 🛠️ Development

### Prerequisites
- Python 3.8+
- pip package manager
- Access to job sites (some may block automated access)

### Testing
```bash
# Test basic functionality
python job_search.py

# Test with sample data
python -c "from job_search import JobSearchEngine; print('Import successful')"
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for educational and personal use. Please respect job sites' terms of service and rate limiting policies.

## 🤝 Support

For issues or questions:
1. Check the README for common solutions
2. Review the code comments for implementation details
3. Ensure your environment variables are set correctly
4. Verify internet connectivity and site accessibility

---

**Note**: This application is designed for educational purposes. In production use, consider implementing proper rate limiting, user agent rotation, and compliance with each job site's terms of service.

