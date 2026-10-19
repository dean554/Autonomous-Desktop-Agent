from ddgs import DDGS
import time

def web_search(query, max_results):
    """Searches the web and yields results one by one."""
    try:
        with DDGS() as ddgs:
            # ddgs.text returns an iterator. We yield each item as it comes in.
            results = ddgs.text(query, max_results=max_results)
            
            for result in results:
                yield result # Stream the result out to the caller
                
    except Exception as e:
        print(f"An error occurred: {e}")

def image_search(query, max_results=3):
    """Searches for images and returns their source URLs."""
    print(f"\n--- Image Search Results for: '{query}' ---")
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=max_results)

            for i, result in enumerate(results, 1):
                print(f"{i}. Title: {result['title']}")
                print(f"   Image URL: {result['image']}")
                print(f"   Source Page: {result['url']}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def news_search(query, max_results=3):
    """Searches for recent news articles."""
    print(f"\n--- News Search Results for: '{query}' ---")
    try:
        with DDGS() as ddgs:
            results = ddgs.news(query, max_results=max_results)
            
            for i, result in enumerate(results, 1):
                print(f"{i}. Headline: {result['title']}")
                print(f"   Source: {result['source']} ({result['date']})")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['body']}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_query = "Python programming"

    print(f"\n--- Streaming Web Search Results for: '{search_query}' ---")
    # Run the different search modules with a 2-second pause in between
    for i, result in enumerate(web_search(search_query, max_results=3), 1):
    #for i, result in enumerate(web_search(search_query), 1):
 
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['href']}")
        print(f"   Snippet: {result['body']}\n")
    
    """print("Pausing to prevent rate limits...")
    time.sleep(2) 
    
    news_search(search_query, max_results=2)
    
    print("Pausing to prevent rate limits...")
    time.sleep(2)
    
    image_search(search_query, max_results=2)"""