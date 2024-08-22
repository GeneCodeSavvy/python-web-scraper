from bs4 import BeautifulSoup
import re
import logging
from playwright.sync_api import sync_playwright
from datetime import datetime

#normal-font ion-color ion-color-se-grey md hydrated market cap

# Setup logging to a file that appends logs every day
log_filename = f"scraping_log_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Regex pattern for market cap
pattern = re.compile(r'\d{1,2}(?:,\d{2})*(?:,\d{3})* Cr\.')

def scrape_stock_details(url: str):
    market_cap = None
    curr_price = None
    pe_ratio = None
    industry_pe_ratio = None

    retries = 0
    max_retries = 3
    success = False

    while retries < max_retries and not success:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Set a timeout for page loading (optional)
                page.set_default_timeout(30000)  # 30 seconds

                logging.info(f"Navigating to the stock page: {url}")
                page.goto(url)

                # Wait for the page to fully load
                page.wait_for_load_state('networkidle')

                logging.info("Page loaded successfully.")

                # Get the page content after JavaScript rendering
                html_content = page.content()
                

                browser.close()

            # Parse the rendered HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all elements with the Market Cap
            market_cap_elements = soup.find_all('ion-text', class_='normal-font ion-color ion-color-se-grey md hydrated')
            for ion_text in market_cap_elements:
                text_content = ion_text.get_text(strip=True)
                match = pattern.match(text_content)
                if match:
                    market_cap = match.group()
                    break
            if not market_cap:
                save_html(html_content)
                raise ValueError("Market Cap not found.")

            # Find element with current price
            curr_price_element = soup.find('ion-text', class_='x-normal-font ng-star-inserted ion-color ion-color-se-grey md hydrated')
            if curr_price_element:
                curr_price = curr_price_element.get_text(strip=True) + ' Rs.'
            else:
                save_html(html_content)
                raise ValueError("Current Price element not found.")

            # Find elements with the P/E ratios
            ion_text_elements = soup.find_all('ion-text', class_='normal-font ng-star-inserted md hydrated')
            if len(ion_text_elements) >= 2:
                industry_pe_ratio = ion_text_elements[1].get_text(strip=True)
                pe_ratio = ion_text_elements[0].get_text(strip=True)
            else:
                save_html(html_content)
                raise ValueError("PE Ratios not found.")

            # If we reach here, the scraping was successful
            success = True
            logging.info("Scraping completed successfully.")
            # save_html(html_content)
        
        except (TimeoutError, ValueError) as e:
            retries += 1
            logging.warning(f"Attempt {retries}/{max_retries} failed: {e}")
            if retries == max_retries:
                logging.error("Max retries reached. Exiting.")
                raise
            else:
                logging.info("Retrying...")
        

    # Return the scraped values as a list
    return [market_cap, curr_price, industry_pe_ratio, pe_ratio]

def save_html(content):
    """Save the HTML content to output.html with a timestamp."""
    output_filename = f"output_{datetime.now().strftime('%Y-%m-%d')}.html"
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(content)
    logging.info(f"HTML content saved to {output_filename}")


# scrape_stock_details('https://web.stockedge.com/share/sobha/7542?section=overview')
