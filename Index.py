from fastapi import FastAPI, Query
import httpx
import asyncio

app = FastAPI(
    title="Unified Lookup Wrapper API",
    description="FastAPI Wrapper for external lookup services",
    version="1.0.0"
)

TIMEOUT = 12.0  # Seconds timeout for external API requests


async def fetch_json(url: str, params: dict = None):
    """Helper function to perform async HTTP GET requests safely."""
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": f"API Error HTTP {exc.response.status_code}", "detail": exc.response.text}
        except Exception as exc:
            return {"error": "Failed to connect to backend service", "detail": str(exc)}


@app.get("/")
def root():
    return {"status": "online", "message": "FastAPI Wrapper Service is Running"}


# 1. Search API
@app.get("/search")
async def search_api(q: str = Query(..., description="Search query parameter")):
    url = "https://leakapi.duckdns.org/search"
    return await fetch_json(url, params={"q": q})


# 2. Chain API
@app.get("/chain")
async def chain_api(q: str = Query(..., description="Chain query parameter")):
    url = "https://leakapi.duckdns.org/chain"
    return await fetch_json(url, params={"q": q})


# 3. Phone Lookup API
@app.get("/lookup")
async def lookup_api(
    phone: str = Query(..., description="Phone number"),
    key: str = Query("ftgamer@2026", description="API Key")
):
    url = "https://leakapi.duckdns.org/lookup"
    return await fetch_json(url, params={"phone": phone, "key": key})


# 4. NumLeak API (Enforces compulsory '91' prefix)
@app.get("/numleak")
async def numleak_api(
    num: str = Query(..., description="Phone number"),
    key: str = Query("chut", description="API Key")
):
    clean_num = num.strip()
    
    # Compulsory 91 prefix enforcement (e.g. 9860319038 -> 919860319038)
    if not clean_num.startswith("91"):
        clean_num = f"91{clean_num}"

    url = "https://ftosint.world/api/numleak"
    return await fetch_json(url, params={"key": key, "num": clean_num})


# 5. Num2Veh API
@app.get("/num2veh")
async def num2veh_api(num: str = Query(..., description="Phone or Vehicle number")):
    url = "https://leakapi.duckdns.org/num2veh"
    return await fetch_json(url, params={"num": num})


# 6. NumToUPI API
@app.get("/numtoupi")
async def numtoupi_api(
    num: str = Query(..., description="Phone number"),
    key: str = Query("chut", description="API Key")
):
    url = "https://ftosint.world/api/numtoupi"
    return await fetch_json(url, params={"key": key, "num": num})


# 7. Combined Endpoint (All APIs run in parallel)
@app.get("/all")
async def all_in_one(
    phone: str = Query(..., description="10-digit Phone number"),
    lookup_key: str = Query("ftgamer@2026"),
    ft_key: str = Query("chut")
):
    clean_num = phone.strip()
    numleak_phone = f"91{clean_num}" if not clean_num.startswith("91") else clean_num

    # Execute all requests concurrently using asyncio.gather
    results = await asyncio.gather(
        fetch_json("https://leakapi.duckdns.org/search", params={"q": clean_num}),
        fetch_json("https://leakapi.duckdns.org/chain", params={"q": clean_num}),
        fetch_json("https://leakapi.duckdns.org/lookup", params={"phone": clean_num, "key": lookup_key}),
        fetch_json("https://ftosint.world/api/numleak", params={"key": ft_key, "num": numleak_phone}),
        fetch_json("https://leakapi.duckdns.org/num2veh", params={"num": clean_num}),
        fetch_json("https://ftosint.world/api/numtoupi", params={"key": ft_key, "num": clean_num}),
        return_exceptions=True
    )

    return {
        "search": results[0],
        "chain": results[1],
        "lookup": results[2],
        "numleak": results[3],
        "num2veh": results[4],
        "numtoupi": results[5]
    }
