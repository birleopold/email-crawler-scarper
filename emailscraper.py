from bs4 import BeautifulSoup
import requests
import urllib.parse
from collections import deque
import re
import time

# User input for target URL
user_url = input('[+] Enter Target URL To Scan: ').strip()
urls = deque([user_url])

scraped_urls = set()
emails = set()

# Custom headers to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

count = 0
max_urls = 500  # Limit to prevent excessive requests

try:
    while urls:
        count += 1
        if count > max_urls:
            break

        url = urls.popleft()
        scraped_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        base_url = f"{parts.scheme}://{parts.netloc}"
        path = url[:url.rfind('/')+1] if '/' in parts.path else url

        print(f'[{count}] Processing {url}')
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
        except (requests.RequestException, requests.HTTPError) as e:
            print(f'[-] Request failed: {e}')
            continue

        # Extract emails using a refined regex
        new_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

        for anchor in soup.find_all("a", href=True):
            link = anchor["href"].strip()
            
            # Ignore 'mailto:' links
            if link.startswith("mailto:"):
                continue
            
            # Convert relative URLs to absolute URLs
            if link.startswith("/"):
                link = base_url + link
            elif not link.startswith("http"):
                link = path + link
            
            # Add only new URLs to the queue
            if link not in urls and link not in scraped_urls:
                urls.append(link)

        # Respect crawl delay to avoid being blocked
        time.sleep(1)

except KeyboardInterrupt:
    print('\n[-] Process interrupted by user.')

# Print all collected emails
print('\n[+] Collected Emails:')
for mail in emails:
    print(mail)
