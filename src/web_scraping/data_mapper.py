def map_to_model(scraped_data, source):
    return {
        'Address': scraped_data['address'],
        'Bedrooms': scraped_data['bedrooms'],
        'Bathrooms': scraped_data['bathrooms'],
        'SquareFootage': scraped_data['sqft'],
        'LotSize': scraped_data['lot_size'],
        'DataSource': source
    }