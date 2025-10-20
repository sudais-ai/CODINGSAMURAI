import requests
from bs4 import BeautifulSoup
import time
def fetch_quotes():
    site = "https://quotes.toscrape.com/"
    try:
        res = requests.get(site)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            quotes_data = soup.find_all("span", class_="text")
            writer_names = soup.find_all("small", class_="author")
            return quotes_data, writer_names
        else:
            return None, None
    except Exception as e:
        print("Error:", e)
        return None, None
def show_quotes(quotes, writers):
    if not quotes or not writers:
        print("Sorry, could not get quotes.")
        return

    print("\n" + "=" * 55)
    print("           RANDOM QUOTES COLLECTION")
    print("=" * 55)
    for i in range(min(8, len(quotes))):
        time.sleep(0.7)
        print(f"\nQuote #{i+1}")
        print("-" * 35)
        print(quotes[i].text.strip())
        print(f"- {writers[i].text}")
        print("-" * 35)
    print("\nThanks for reading these quotes!")
    print("=" * 55)

def save_to_file(quotes, writers):
    if not quotes or not writers:
        return
    with open("my_quotes.txt", "w", encoding="utf-8") as f:
        f.write("QUOTES ARCHIVE\n")
        f.write("=" * 20 + "\n\n")
        for i in range(min(8, len(quotes))):
            f.write(f"Quote {i+1}:\n")
            f.write(quotes[i].text.strip() + "\n")
            f.write(f"By: {writers[i].text}\n")
            f.write("-" * 40 + "\n\n")
    print("All quotes have been saved in 'my_quotes.txt'")

def run():
    print("Starting program... Please wait!\n")
    q, w = fetch_quotes()
    if q and w:
        show_quotes(q, w)
        save_to_file(q, w)
    else:
        print("Could not get data from the website.")

if __name__ == "__main__":
    run()
