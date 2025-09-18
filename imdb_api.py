import requests
from bs4 import BeautifulSoup
import json
from fastapi import FastAPI, Query
import uvicorn

app = FastAPI(title="My IMDb Search API", version="1.0.0")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/108.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://www.imdb.com/find/"


def extract_results(html):
    """Parse __NEXT_DATA__ JSON from IMDb page and extract relevant data."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return []

    data = json.loads(script.string)
    try:
        titles = data["props"]["pageProps"]["titleResults"]["results"]
    except KeyError:
        return []

    results = []
    for t in titles:
        results.append({
            "id": t.get("id"),
            "title": t.get("titleNameText"),
            "year": t.get("titleReleaseText"),
            "cast": t.get("topCredits", []),
            "poster": t.get("titlePosterImageModel", {}).get("url")
        })
    return results


@app.get("/search")
def search_movies(q: str = Query(..., description="Search term, e.g., borbaad")):
    """Search IMDb movies and return JSON results."""
    params = {"q": q}
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    results = extract_results(resp.text)
    return {"query": q, "count": len(results), "results": results}


# ----------- Run the server ---------------
if __name__ == "__main__":
    uvicorn.run("imdb_api:app", host="127.0.0.1", port=8000, reload=True)
