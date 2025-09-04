# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode

# Router'ları en başta bir kere import ediyoruz
from api.routers import auth, products, utils, pages

# Kendi özel Jinja2 fonksiyonumuzu tanımlıyoruz
def dict_set(d, key, value):
    d_copy = d.copy()
    d_copy[key] = value
    return d_copy 

app = FastAPI(
    title="Scraping API - Refactored Edition",
    description="Bu API, kitapları scrape eder ve CRUD işlemlerini yönetir.",
    version="1.0.0"
)

# Jinja2 ortamına özel fonksiyon ve filtrelerimizi tanıtıyoruz
pages.templates.env.filters['dict_set'] = dict_set
pages.templates.env.filters["urlencode"] = urlencode
pages.templates.env.filters['dict'] = dict  

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotaları dahil et
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(utils.router)
app.include_router(pages.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "docs_url": "/docs"}