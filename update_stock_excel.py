import pandas as pd
import time
from web_scraper import scrape_stock_details

# Read the Excel file into a DataFrame
df = pd.read_excel('example.xlsx')  # Adjust the path to your Excel file

# Filter rows where 'MARKET CAP(CR)' is NaN and 'Web Link' is not NaN
no_update_df = df[df['MARKET CAP(CR)'].isna() & df['Web Link'].notna()]

# Extract URLs from the filtered DataFrame
urls_with_no_market_cap = no_update_df['Web Link'].tolist()
updated_urls = [url+'?section=overview' for url in urls_with_no_market_cap]

# Update the 'Web Link' column in the original DataFrame with the modified URLs
df.loc[df['MARKET CAP(CR)'].isna() & df['Web Link'].notna(), 'Web Link'] = updated_urls

# List to store results
results = []

# Loop through each URL and scrape the details
for url in updated_urls:
    try:
        print(f"Scraping URL: {url}")
        scraped_data = scrape_stock_details(url)
        results.append({
            'URL': url,
            'Market Cap': scraped_data[0],
            'Current Price': scraped_data[1],
            'Industry P/E Ratio': scraped_data[2],
            'Company P/E Ratio': scraped_data[3]
        })
        time.sleep(10)
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# print(results)

for stock in results:
    # Clean and convert values to appropriate data types
    # Remove commas and currency/unit suffixes
    market_cap = stock['Market Cap'].replace(',', '').replace(' Cr.', '').strip()
    industry_pe = float(stock['Industry P/E Ratio'].replace(',', '').strip())
    stock_pe = float(stock['Company P/E Ratio'].replace(',', '').strip())
    
    # Clean the 'Current Price' by removing commas and 'Rs.'
    stock_price_str = stock['Current Price'].replace(',', '').replace(' Rs.', '').strip()
    
    try:
        market_cap = float(market_cap)
    except ValueError:
        market_cap = None  # or handle this case as needed
    
    try:
        stock_price = float(stock_price_str)
    except ValueError:
        stock_price = None  # or handle this case as needed

    # Match the URL and update corresponding columns
    df.loc[df['Web Link'] == stock['URL'], ['MARKET CAP(CR)', 'INDUSTRY PE', 'STOCK P/E', 'STOCK PRICE']] = [
        market_cap, industry_pe, stock_pe, stock_price
    ]
    
df.to_excel('example.xlsx', index=False, engine='openpyxl')

# df.to_csv('example.csv', index=False)

# print(df['STOCK PRICE'])
