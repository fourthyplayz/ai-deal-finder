import os
import sys

# Paste your Gemini API key here
API_KEY = "AIzaSyBlWq8eU6qMwvEHagxW3z3xxecELVpT6dQ"

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("The 'google-genai' library is required.")
    print("Please install it using: pip install google-genai")
    sys.exit(1)

def get_user_input():
    print("Welcome to the AI Deal Finder!")
    print("I will search the internet to find the best current open deals for you.\n")
    
    item = input("What specific model or item are you looking for? (e.g., iPhone 15 Pro Max): ")
    location = input("Where are you located? (e.g., Cairo, US, Online): ")
    budget = input("What is your budget? (e.g., Under $1000): ")
    
    return item, location, budget

def add_citations(response):
    text = response.text
    if not response.candidates or not response.candidates[0].grounding_metadata:
        return text
        
    metadata = response.candidates[0].grounding_metadata
    supports = metadata.grounding_supports
    chunks = metadata.grounding_chunks

    if not supports or not chunks:
        return text

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = " " + ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text

def find_deals():
    api_key = os.environ.get("GEMINI_API_KEY", API_KEY)
    if not api_key:
        api_key = input("Please enter your GEMINI_API_KEY: ")
        if not api_key:
            print("API Key is required to use the Gemini API.")
            sys.exit(1)
            
    client = genai.Client(api_key=api_key)
    
    item, location, budget = get_user_input()
    
    prompt = f"""
    You are an expert deal finder and personal shopper. 
    A user is looking for the best current open deals for the following:
    
    Item/Model: {item}
    Location: {location}
    Budget: {budget}
    
    Using Google Search, find the best actual links to purchase this item that fit the criteria.
    Focus on active, verifiable deals. If it's a specific location, look for local stores or stores that ship there.
    Provide a detailed summary of the best deals found, including the price, the store, and any relevant details (like shipping or refurbished status).
    """
    
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        temperature=0.2 # Lower temperature for more factual results
    )
    
    print("\nSearching the internet for the best deals... Please wait.")
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=config,
        )
        
        print("\n=== Best Deals Found ===")
        print(add_citations(response))
        print("========================")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    find_deals()
