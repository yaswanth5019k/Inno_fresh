import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import time
import re

class BaseScraper:
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    def extract_date(self, date_text: str) -> str:
        """Extract and normalize date from text"""
        if not date_text:
            return None
        # Basic date extraction - can be improved
        return self.clean_text(date_text)
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Override this method in specific scrapers"""
        raise NotImplementedError


class StartupIndiaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Startup India")
        self.base_url = "https://www.startupindia.gov.in"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Startup India events and programs"""
        events = []
        
        try:
            # Try multiple Startup India URLs
            urls = [
                f"{self.base_url}/content/sih/en/government-schemes.html",
                f"{self.base_url}/content/sih/en/startup-schemes.html",
                f"{self.base_url}/content/sih/en/startup-funding.html"
            ]
            
            soup = None
            for url in urls:
                soup = self.get_page(url)
                if soup:
                    break
            
            if not soup:
                return events
            
            # Example scraping logic - adjust selectors based on actual site structure
            event_cards = soup.find_all('div', class_='scheme-card') or soup.find_all('div', class_='card')
            
            for card in event_cards[:10]:  # Limit to 10 for now
                title_elem = card.find('h3') or card.find('h2') or card.find('.title')
                desc_elem = card.find('p') or card.find('.description')
                link_elem = card.find('a')
                
                if title_elem:
                    event = {
                        'title': self.clean_text(title_elem.get_text()),
                        'description': self.clean_text(desc_elem.get_text()) if desc_elem else None,
                        'organizer': 'Government of India - Startup India',
                        'source_url': self.base_url + (link_elem.get('href', '') if link_elem else ''),
                        'event_type': 'government_scheme',
                        'tags': ['startup', 'government', 'scheme'],
                        'location': 'India'
                    }
                    events.append(event)
        
        except Exception as e:
            print(f"Error scraping Startup India: {e}")
        
        return events


class THubScraper(BaseScraper):
    def __init__(self):
        super().__init__("T-Hub")
        self.base_url = "https://t-hub.co"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape T-Hub events and programs"""
        events = []
        
        try:
            # Example URL - needs actual T-Hub events page
            url = f"{self.base_url}/events"
            soup = self.get_page(url)
            
            if not soup:
                return events
            
            # Example scraping logic
            event_items = soup.find_all('div', class_='event-item') or soup.find_all('article')
            
            for item in event_items[:10]:
                title_elem = item.find('h2') or item.find('h3') or item.find('.event-title')
                desc_elem = item.find('p') or item.find('.event-description')
                date_elem = item.find('.event-date') or item.find('time')
                link_elem = item.find('a')
                
                if title_elem:
                    event = {
                        'title': self.clean_text(title_elem.get_text()),
                        'description': self.clean_text(desc_elem.get_text()) if desc_elem else None,
                        'date': self.extract_date(date_elem.get_text()) if date_elem else None,
                        'organizer': 'T-Hub',
                        'source_url': self.base_url + (link_elem.get('href', '') if link_elem else ''),
                        'event_type': 'incubator',
                        'tags': ['startup', 'incubator', 'hyderabad'],
                        'location': 'Hyderabad, India'
                    }
                    events.append(event)
        
        except Exception as e:
            print(f"Error scraping T-Hub: {e}")
        
        return events


class NasscomScraper(BaseScraper):
    def __init__(self):
        super().__init__("NASSCOM")
        self.base_url = "https://nasscom.in"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape NASSCOM events and startup programs"""
        events = []
        
        try:
            # Example URL - needs actual NASSCOM events page
            url = f"{self.base_url}/events"
            soup = self.get_page(url)
            
            if not soup:
                return events
            
            # Example scraping logic
            event_containers = soup.find_all('div', class_='event') or soup.find_all('.news-item')
            
            for container in event_containers[:10]:
                title_elem = container.find('h2') or container.find('h3')
                desc_elem = container.find('p')
                link_elem = container.find('a')
                
                if title_elem:
                    event = {
                        'title': self.clean_text(title_elem.get_text()),
                        'description': self.clean_text(desc_elem.get_text()) if desc_elem else None,
                        'organizer': 'NASSCOM',
                        'source_url': link_elem.get('href', self.base_url) if link_elem else self.base_url,
                        'event_type': 'startup_program',
                        'tags': ['startup', 'tech', 'nasscom'],
                        'location': 'India'
                    }
                    events.append(event)
        
        except Exception as e:
            print(f"Error scraping NASSCOM: {e}")
        
        return events


class ScraperManager:
    def __init__(self):
        self.scrapers = [
            StartupIndiaScraper(),
            THubScraper(),
            NasscomScraper()
        ]
    
    def run_all_scrapers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run all scrapers and collect results"""
        results = {}
        
        for scraper in self.scrapers:
            print(f"Running scraper for {scraper.source_name}...")
            try:
                events = scraper.scrape()
                results[scraper.source_name] = events
                print(f"Found {len(events)} events from {scraper.source_name}")
                time.sleep(2)  # Be respectful to servers
            except Exception as e:
                print(f"Error with {scraper.source_name}: {e}")
                results[scraper.source_name] = []
        
        return results