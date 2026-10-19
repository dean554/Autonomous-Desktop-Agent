import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def crawl_site(start_url, max_pages=15, delay=1.0):
    """
    Crawls pages within the same domain, discovering and tracking links.
    """
    target_domain = urlparse(start_url).netloc
    
    # Trackers to manage crawler state
    urls_to_crawl = [start_url]
    visited_urls = set()

    print(f"Starting crawl on: {start_url}")

    while urls_to_crawl and len(visited_urls) < max_pages:
        # Get next URL from queue
        current_url = urls_to_crawl.pop(0)
        
        # Skip if already visited
        if current_url in visited_urls:
            continue
            
        try:
            print(f"[{len(visited_urls) + 1}/{max_pages}] Fetching: {current_url}")
            
            # Send HTTP request
            headers = {'User-Agent': 'Mozilla/5.0 (Compatible; MyPythonCrawler/1.0)'}
            response = requests.get(current_url, headers=headers, timeout=10)
            
            # Skip page if it fails or isn't HTML
            if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                continue
                
            visited_urls.add(current_url)
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and filter links
            for link in soup.find_all('a', href=True):
                # Convert relative links to absolute URLs
                absolute_url = urljoin(current_url, link['href'])
                
                # Normalize URL by removing fragments
                parsed_url = urlparse(absolute_url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                # Verify link stays within the target domain and hasn't been crawled yet
                if parsed_url.netloc == target_domain and clean_url not in visited_urls:
                    if clean_url not in urls_to_crawl:
                        urls_to_crawl.append(clean_url)
                        
            # Respectful delay between network calls
            time.sleep(delay)
            
        except Exception as e:
            print(f"Failed to crawl {current_url}: {e}")
            continue

    print(f"\nCrawling completed. Discovered and visited {len(visited_urls)} unique pages.")
    return visited_urls

if __name__ == "__main__":
    # Target URL must include protocol (http/https)
    START_URL = "https://google.com" 
    crawl_site(START_URL, max_pages=10)
