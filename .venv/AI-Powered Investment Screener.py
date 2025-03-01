import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import concurrent.futures
import logging
import csv
import random

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Rotating User-Agents to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
]

def fetch_headlines(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headlines = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'a']):
            text = tag.get_text(strip=True)
            link = tag.get('href')
            if text and len(text.split()) > 3 and not any(keyword in text.lower() for keyword in ['privacy', 'sign in', 'terms', 'cookie']):
                if any(keyword in text.lower() for keyword in ['investment', 'funding', 'capital', 'deal', 'acquisition', 'merger', 'raise', 'venture']):
                    full_link = urljoin(url, link) if link else None
                    headlines.append({'text': text, 'link': full_link})
        
        return headlines[:10]  # Limit to 10 headlines
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return []

def fetch_all_sources(sources):
    all_headlines = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_headlines, sources)
    
    for source, headlines in zip(sources, results):
        print(f"Fetching headlines from: {source}")
        if headlines:
            for i, headline in enumerate(headlines, 1):
                print(f"{i}. {headline['text']}\nLink: {headline['link']}")
                all_headlines.append(headline)
        else:
            print("No relevant headlines found.")
        print("-" * 80)
    
    return all_headlines

def save_to_csv(data, filename="headlines.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "link"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Headlines saved to {filename}")

# List of sources
sources = [
    "https://www.globalprivatecapital.org/industry-news/",
    "https://psgcapital.com/news-insights/latest-transactions/",
    "https://www.ifc.org/en/pressroom",
    "https://www.bayportfinance.com/latest-investor-news/",
    "https://www.zawya.com/en/news/latest",
    "https://www.africaprivateequitynews.com/t/deals",
    "https://www.africaprivateequitynews.com/t/exits",
    "https://www.africaprivateequitynews.com/t/debt-and-mez",
    "https://www.africaprivateequitynews.com/t/venture-capital",
    "https://www.avca.africa/news-insights/industry-news/",
    "https://african.business"
]

# Run scraper and save results
all_headlines = fetch_all_sources(sources)
save_to_csv(all_headlines)
