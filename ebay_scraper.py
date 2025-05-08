'''
Gets Ebay sold & complete listings, storing name, price and date in list of jsons.
Assumes python > 3.2.2 as html.parser is faster than previous versions. If < 3.2.2 or desire for speed, need XML lxml parser instead of built-in html.parser.
Encodes in utf-8
'''
from bs4 import BeautifulSoup as bs
from utils import write_csv,write_json
import requests

''' Layout (for 1 search string)
1. Use search string (space separated) to do a search on Ebay. Instead of using api, use url (which can change in future)
2. Get the url of the search, and from there, do a get. Save all pages and return the set
3. For each page, get json with keys: name, date sold, sold amonunt.

URL template for search: https://www.ebay.com/sch/i.html?_nkw=<KW1>+<KW2>+<KW3>+<KW4>&LH_Sold=1&LH_Complete=1
Ex: https://www.ebay.com/sch/i.html?_nkw=jackie+robinson+psa+10&LH_Sold=1&LH_Complete=1
As long as nkw=(search string separated by +) is in and &LH_Sold=1&LH_Complete=1 are in, we are good
LH_Sold=1 - Only show Sold Listings
LH_Complete=1 - Only show Completed Listings

Useful patterns:
<div class="s-item__detail s-item__detail--primary"><span class=s-item__price><!--F#f_0--><!--F#f_0--><span class=POSITIVE>$79.99</span><!--F/--><!--F/--></span></div> - A price
span class=s-item__price - The price tag, cannot use div as used elsewhere

<div class=s-item__caption--row><span class="s-item__caption--signal POSITIVE"><span>Sold  Apr 23, 2025</span></span></div> - A date
<span class="s-item__caption--signal POSITIVE"><span> - The date span
<div class=s-item__caption><div class=s-item__caption--row> - The date div

<div class=s-item__title><span role=heading aria-level=3><!--F#f_0-->PSA 10 GEM MINT JACKIE ROBINSON 1994 UPPER DECK /GM BASEBALL PREVIEW #7  POP 7<!--F/--></span></div> - A title
<div class=s-item__title> - The title div
'''

def get_search_string(search_url: str):
    if not search_url:
        return ''
    pat = 'https://www.ebay.com/sch/i.html?_nkw=<KEYWORDS>&LH_Sold=1&LH_Complete=1'
    # Spaces are + in Ebay search strings
    url = pat.replace('<KEYWORDS>',search_url.replace(' ','+'))
    return url

# Get list of all sets of pages
def get_list_page_sets(search_urls: list[str]) -> list[set[str]]:
    # None or empty list
    if not search_urls or isinstance(search_urls,list) and len(search_urls) == 0:
        return []
    
    fixed_urls = [get_search_string(url) for url in search_urls]
    result = []
    for url in fixed_urls:
        r = requests.get(url)
        if r.ok:
            soup = bs(r.content,'html.parser')
            # Set for no duplicate pages, gets first page even though it's default
            result.append({i['href'] for i in soup.find_all('a',href=True) if 'pgn=' in i['href']})
    return result

# Returns jsons, and writes files if wanted
def main(search_string_list: list[str] = [],output_json = '',output_csv = '',count_start = 0):
    # Use count param instead of loop var in case we want unique ids and know where they start
    count = count_start or 0
    # List of sets of pages to go through. Each set is tied to its specific search string
    sets = get_list_page_sets(search_string_list)
    if len(sets) == 0:
        return
    # Create rows and jsons for output into their respective files.
    jsons = []
    rows = []
    # For each set, get request for each page in set, and get all data.
    for set in sets:
        for page in set:
            r = requests.get(page)
            if r.ok:
                soup = bs(r.content,'html.parser')
                #  Dates
                date_divs = soup.find_all('div',class_='s-item__caption--row')
                    
                # Titles, use [2:] to remove the 2 "Shop on Ebay" strings at top of page
                title_divs = soup.find_all('div',class_='s-item__title')[2:]

                # Prices, use [2:] to remove the 2 at top of page that don't refer to any item
                price_spans = soup.find_all('span',class_='s-item__price')[2:]

            # Each list should be same length
            for i in range(len(title_divs)):
                name = title_divs[i].text
                date = date_divs[i].text.replace('Sold ','').strip()
                sold = price_spans[i].text
                jsons.append({'id': count,
                              'name': name,
                              'date sold': date,
                              'sold amount': sold})
                rows.append([count,name,date,sold])
                count += 1
    # Write
    if output_csv:
        header = ['id','Name','Date Sold','Sold Amount']
        write_csv(header,rows,output_csv)
    if output_json:
        write_json(jsons,output_json)
    return jsons

# Modify to run with whatever, should instead use sys to get args though
if __name__ == '__main__':
    main(['Huge Computer'],count_start=0,output_json='json_test.json',output_csv='csv_test.csv')