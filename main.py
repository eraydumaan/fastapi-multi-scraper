from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, products, utils,crypto

# Scraper fonksiyonlarını import et
from services.scraper.books_scraper import scrape_books
from services.scraper.quotes_scraper import scrape_quotes
from services.scraper.laptops_scraper import scrape_laptops

app = FastAPI(
    title="Scraping API",
    description="Bu API, kitapları scrape eder ve CRUD işlemlerini yönetir.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlar
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(crypto.router,prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "docs_url": "/docs"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/api/ping", tags=["Health"])
def api_ping():
    return {"pong": True}


# -----------------------------
# Scraper'ları otomatik tetikle
# -----------------------------
@app.on_event("startup")
async def startup_scrapers():
    try:
        print("🚀 Scrapers başlatılıyor...")
        await scrape_quotes(user_id=None)
        await scrape_books(user_id=None)
        await scrape_laptops(user_id=None)
        print("✅ Scrapers tamamlandı ve MongoDB'ye veri kaydedildi.")
    except Exception as e:
        print("❌ Scraper çalıştırılamadı:", e)


# Route haritasını logla (debug için)
@app.on_event("startup")
async def print_routes_on_startup():
    print("\n=== ROUTE MAP ===")
    for r in app.routes:
        methods = sorted([m for m in getattr(r, "methods", set()) if m != "HEAD"])
        print(f"{methods} -> {getattr(r, 'path', '')}")
    print("=== END ROUTE MAP ===\n")
