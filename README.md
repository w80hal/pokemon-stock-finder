# UK Pokémon Stock Finder

A lightweight Streamlit dashboard for UK Pokémon TCG sourcing.

## What it does

- Searches the main UK Pokémon retailers from one page.
- Gives direct access to UK stock-tracking services.
- Lets you paste exact product pages and performs a conservative stock/price check.
- Lets you define a maximum purchase price.
- Estimates resale profit and ROI using your expected sale price, selling fees and packing/postage costs.
- Highlights a BUY signal only when a page looks in-stock and the detected price is below your ceiling.

## Included retailers

Smyths Toys, Argos, GAME, Pokémon Center UK, Magic Madhouse, Chaos Cards,
Total Cards, Zatu Games, The Game Collection, John Lewis, Very and Currys.

## Run it

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:

   pip install -r requirements.txt

4. Then run:

   streamlit run pokemon_stock_finder.py

Your browser should open the dashboard automatically.

## Important limitations

Retailers frequently change their websites. Some use JavaScript rendering, queues,
CAPTCHAs, app-only inventory or anti-bot systems. Because of that, the exact-URL checker
uses conservative text detection and may say "Needs manual check".

Argos and Smyths local inventory often depends on your selected postcode/store, so use the
retailer button and choose your local branch.

This tool does not auto-buy products and does not bypass retailer restrictions.
