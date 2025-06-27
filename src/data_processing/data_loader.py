# Add at the top
from web_scraping.scrapers import scrape_zillow, scrape_redfin
from web_scraping.data_mapper import map_to_model

# Modify load_data function
def load_data(input_source):
    if isinstance(input_source, list):  # List of URLs
        properties = []
        for url in input_source:
            if 'zillow' in url:
                scraped = scrape_zillow(url)
                if scraped:
                    properties.append(map_to_model(scraped, 'Zillow'))
            elif 'redfin' in url:
                scraped = scrape_redfin(url)
                if scraped:
                    properties.append(map_to_model(scraped, 'Redfin'))
        return pd.DataFrame(properties)
    else:  # CSV file path
        return pd.read_csv(input_source)