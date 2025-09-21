#!/usr/bin/env python3

import requests
import json

def test_sorting():
    base_url = "http://localhost:8000/v1/books/"
    
    # Test different sort combinations
    test_cases = [
        {"sortBy": "title", "sortOrder": "asc"},
        {"sortBy": "title", "sortOrder": "desc"},
        {"sortBy": "author", "sortOrder": "asc"},
        {"sortBy": "author", "sortOrder": "desc"},
    ]
    
    for case in test_cases:
        params = {
            "offset": 0,
            "limit": 5,
            **case
        }
        
        print(f"\n=== Testing {case} ===")
        try:
            response = requests.get(base_url, params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"Found {len(books)} books")
                for i, book in enumerate(books[:3]):
                    print(f"  {i+1}. {book.get('title', 'N/A')} by {book.get('author', 'N/A')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_sorting()
