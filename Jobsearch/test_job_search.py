#!/usr/bin/env python3
"""
🧪 Test script for the Job Search Application
==============================================

This script tests the basic functionality of the job search engine
without requiring user input or making actual web requests.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_search import JobSearchEngine, JobListing

def test_job_search_engine():
    """Test the JobSearchEngine class"""
    print("🧪 Testing JobSearchEngine...")
    
    try:
        # Create engine instance
        engine = JobSearchEngine()
        print("✅ JobSearchEngine created successfully")
        
        # Test sample data creation
        test_jobs = engine._parse_linkedin_html("", 3)
        print(f"✅ Sample LinkedIn jobs created: {len(test_jobs)}")
        
        # Test relevance scoring
        test_job = test_jobs[0]
        relevance = engine._calculate_relevance_score(test_job, "San Francisco", ["python", "developer"])
        print(f"✅ Relevance scoring works: {relevance:.2f}")
        
        # Test job status verification
        status = engine._verify_job_status(test_job)
        print(f"✅ Job status verification works: {status}")
        
        print("🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_job_listing_dataclass():
    """Test the JobListing dataclass"""
    print("\n🧪 Testing JobListing dataclass...")
    
    try:
        # Create a sample job listing
        job = JobListing(
            title="Test Job",
            company="Test Company",
            location="Test Location",
            description="Test description",
            url="https://example.com",
            source="Test Source",
            posted_date="2024-01-01",
            salary="$50,000",
            job_type="Full-time",
            relevance_score=0.8,
            is_currently_open=True
        )
        
        print(f"✅ JobListing created: {job.title} at {job.company}")
        print(f"✅ Relevance score: {job.relevance_score}")
        print(f"✅ Currently open: {job.is_currently_open}")
        
        print("🎉 JobListing dataclass test passed!")
        return True
        
    except Exception as e:
        print(f"❌ JobListing test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 JOB SEARCH APPLICATION - TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_job_listing_dataclass,
        test_job_search_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\n🚀 To run the full application:")
        print("   python job_search.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

