
import re
import time
from urllib.parse import quote_plus, urljoin
import requests
import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="UK Pokémon Stock Finder", page_icon="🔎", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

RETAILERS = {
    "Smyths Toys": {
        "search": "https://www.smythstoys.com/uk/en-gb/search/?text={q}",
        "home": "https://www.smythstoys.com/uk/en-gb/"
    },
    "Argos": {
        "search": "https://www.argos.co.uk/search/{slug}/",
        "home": "https://www.argos.co.uk/"
    },
    "GAME": {
        "search": "https://www.game.co.uk/searchresults?descriptionfilter={q}",
        "home": "https://www.game.co.uk/"
    },
    "Pokémon Center UK": {
        "search": "https://www.pokemoncenter.com/en-gb/search/{q}",
        "home": "https://www.pokemoncenter.com/en-gb/"
    },
    "Magic Madhouse": {
        "search": "https://magicmadhouse.co.uk/search?q={q}",
        "home": "https://magicmadhouse.co.uk/"
    },
    "Chaos Cards": {
        "search": "https://www.chaoscards.co.uk/search?q={q}",
        "home": "https://www.chaoscards.co.uk/"
    },
    "Total Cards": {
        "search": "https://totalcards.net/search?q={q}",
        "home": "https://totalcards.net/"
    },
    "Zatu Games": {
        "search": "https://www.board-game.co.uk/?s={q}&post_type=product",
        "home": "https://www.board-game.co.uk/"
    },
    "The Game Collection": {
        "search": "https://www.thegamecollection.net/catalogsearch/result/?q={q}",
        "home": "https://www.thegamecollection.net/"
    },
    "John Lewis": {
        "search": "https://www.johnlewis.com/search?search-term={q}",
        "home": "https://www.johnlewis.com/"
    },
    "Very": {
        "search": "https://www.very.co.uk/e/q/{q}.end",
        "home": "https://www.very.co.uk/"
    },
    "Currys": {
        "search": "https://www.currys.co.uk/search?q={q}",
        "home": "https://www.currys.co.uk/"
    },
}

TRACKERS = {
    "Poké Tracker": "https://poketracker.co.uk/tracker",
    "StockRadar UK": "https://stocksradar.uk/",
    "PackHunt (local shelf reports)": "https://www.packhunt.app/",
}

POSITIVE = [
    "in stock", "add to basket", "add to cart", "buy now",
    "available for delivery", "click & collect", "click and collect"
]
NEGATIVE = [
    "out of stock", "sold out", "currently unavailable",
    "not available", "notify me", "coming soon"
]

def retailer_search_url(name, query):
    cfg = RETAILERS[name]
    q = quote_plus(query)
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
    return cfg["search"].format(q=q, slug=slug)

def extract_price(text):
    vals = re.findall(r"£\s?(\d+(?:\.\d{1,2})?)", text)
    nums = [float(v) for v in vals]
    return min(nums) if nums else None

def check_exact_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True).lower()
        pos = any(x in text for x in POSITIVE)
        neg = any(x in text for x in NEGATIVE)
        price = extract_price(text)
        if r.status_code >= 400:
            status = f"Blocked / HTTP {r.status_code}"
        elif pos and not neg:
            status = "Likely in stock"
        elif neg:
            status = "Likely out of stock"
        else:
            status = "Needs manual check"
        return status, price, r.status_code
    except Exception as e:
        return "Check failed", None, None

st.title("🔎 UK Pokémon Stock Finder")
st.caption("Built for fast UK sealed-product sourcing. Search retailers, compare against your buy ceiling, and monitor exact product pages.")

with st.sidebar:
    st.header("Buy criteria")
    query = st.text_input("Product / set", value="Pokémon 30th Celebration ETB")
    max_price = st.number_input("Maximum buy price (£)", min_value=0.0, value=50.0, step=1.0)
    target_sale = st.number_input("Expected resale price (£)", min_value=0.0, value=70.0, step=1.0)
    fee_pct = st.number_input("Estimated selling fees (%)", min_value=0.0, value=12.0, step=0.5)
    postage = st.number_input("Your postage / packing cost (£)", min_value=0.0, value=0.0, step=0.5)

fee = target_sale * fee_pct / 100
profit_at_ceiling = target_sale - fee - postage - max_price
roi = (profit_at_ceiling / max_price * 100) if max_price else 0

c1, c2, c3 = st.columns(3)
c1.metric("Max buy", f"£{max_price:.2f}")
c2.metric("Profit at max buy", f"£{profit_at_ceiling:.2f}")
c3.metric("ROI at max buy", f"{roi:.1f}%")

st.subheader("1. Search the main UK retailers")
st.write("These buttons open each retailer's current search results. For Argos/Smyths, select your local store/postcode on the retailer site to see local availability.")

cols = st.columns(3)
for i, name in enumerate(RETAILERS):
    with cols[i % 3]:
        st.link_button(name, retailer_search_url(name, query), use_container_width=True)

st.subheader("2. UK stock trackers")
st.write("Useful for finding listings you may not already know about.")
cols = st.columns(3)
for i, (name, url) in enumerate(TRACKERS.items()):
    with cols[i % 3]:
        st.link_button(name, url, use_container_width=True)

st.subheader("3. Check exact product pages")
st.write("Paste direct product URLs below. The checker looks for common UK stock wording and prices. Some retailers use anti-bot protection, so ambiguous results are deliberately marked for manual checking.")

default_urls = ""
urls_text = st.text_area("One product URL per line", value=default_urls, height=150)

if st.button("Check URLs", type="primary"):
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    if not urls:
        st.warning("Paste at least one product URL.")
    else:
        rows = []
        progress = st.progress(0)
        for idx, url in enumerate(urls):
            status, price, code = check_exact_url(url)
            qualifies = price is not None and price <= max_price and "in stock" in status.lower()
            profit = None
            roi_row = None
            if price is not None:
                profit = target_sale - fee - postage - price
                roi_row = profit / price * 100 if price else None
            rows.append({
                "URL": url,
                "Status": status,
                "Price": price,
                "Under max buy?": "YES" if price is not None and price <= max_price else "No / unknown",
                "Buy signal": "🔥 BUY" if qualifies else "",
                "Est. profit": round(profit, 2) if profit is not None else None,
                "Est. ROI %": round(roi_row, 1) if roi_row is not None else None,
                "HTTP": code
            })
            progress.progress((idx + 1) / len(urls))
            time.sleep(0.15)
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("4. Sourcing rule")
st.info(
    f"For the current numbers, treat £{max_price:.2f} as your ceiling. "
    f"At a £{target_sale:.2f} resale price, {fee_pct:.1f}% fees and £{postage:.2f} costs, "
    f"your estimated profit at that ceiling is £{profit_at_ceiling:.2f}."
)

st.caption(
    "Stock detection is intentionally conservative. Retailer layouts, queues, invitation systems, "
    "CAPTCHAs and app-only/local inventory can prevent automated confirmation. Always verify the basket before travelling or buying."
)
