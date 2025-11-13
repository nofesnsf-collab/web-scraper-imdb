"""IMDb Web Scraper - Extract movie data and ratings

Extract movie titles, ratings, cast info from IMDb.
Uses BeautifulSoup for static content and Selenium for dynamic.
Exports data to CSV format.
"""

import requests
from bs4 import BeautifulSoup
import csv
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class IMDbScraper:
    """Professional IMDb web scraper."""
    
    BASE_URL = "https://www.imdb.com"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_top_movies(self, limit: int = 100) -> List[Dict]:
        """Scrape top rated movies from IMDb.
        
        Args:
            limit: Number of movies to scrape
            
        Returns:
            List of movie dictionaries with title, year, rating
        """
        movies = []
        try:
            url = f"{self.BASE_URL}/chart/top250/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rows = soup.find_all('tr', limit=limit)
            for row in rows:
                try:
                    title = row.find('td', class_='titleColumn').find('a').text
                    year = row.find('td', class_='titleColumn').find('span').text.strip('()')
                    rating = row.find('td', class_='ratingColumn imdbRating').find('strong').text
                    
                    movies.append({
                        'title': title,
                        'year': year,
                        'rating': rating
                    })
                except Exception as e:
                    logging.error(f"Error parsing movie: {e}")
                    continue
            
            logging.info(f"Successfully scraped {len(movies)} movies")
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
        
        return movies
    
    def export_to_csv(self, movies: List[Dict], filename: str = 'imdb_movies.csv'):
        """Export scraped movies to CSV file.
        
        Args:
            movies: List of movie dictionaries
            filename: Output CSV filename
        """
        if not movies:
            logging.warning("No movies to export")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['title', 'year', 'rating'])
                writer.writeheader()
                writer.writerows(movies)
            logging.info(f"Exported {len(movies)} movies to {filename}")
        except IOError as e:
            logging.error(f"File write error: {e}")
    
    def scrape_by_genre(self, genre: str) -> List[Dict]:
        """Scrape movies by specific genre.
        
        Args:
            genre: Movie genre (e.g., 'Action', 'Drama')
            
        Returns:
            List of genre movies
        """
        movies = []
        try:
            url = f"{self.BASE_URL}/search/title/?genres={genre.lower()}&sort=user_rating,-popularity"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = soup.find_all('div', class_='lister-item', limit=50)
            for item in items:
                try:
                    title_div = item.find('h3', class_='lister-item-header')
                    rating_div = item.find('div', class_='ratings-bar')
                    
                    if title_div and rating_div:
                        title = title_div.find('a').text
                        rating = rating_div.find('strong').text
                        
                        movies.append({'title': title, 'genre': genre, 'rating': rating})
                except Exception as e:
                    logging.debug(f"Parse error: {e}")
            
            logging.info(f"Scraped {len(movies)} {genre} movies")
        except Exception as e:
            logging.error(f"Error scraping genre: {e}")
        
        return movies


if __name__ == '__main__':
    scraper = IMDbScraper()
    
    # Example usage
    top_movies = scraper.scrape_top_movies(limit=25)
    scraper.export_to_csv(top_movies, 'top_imdb_movies.csv')
    
    # Scrape by genre
    action_movies = scraper.scrape_by_genre('Action')
    print(f"Found {len(action_movies)} action movies")
