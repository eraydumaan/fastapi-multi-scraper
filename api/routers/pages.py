from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from collections import defaultdict
import math # Sayfa sayısını hesaplamak için

from db import repository as repo
from models.product import ProductPublic

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/show-products", response_class=HTMLResponse)
async def show_all_products(
    request: Request,
    page: int = Query(1, ge=1), # Sayfa numarasını URL'den alıyoruz (örn: ?page=2), varsayılan 1
    size: int = Query(50, ge=1, le=100) # Her sayfadaki öğe sayısı, varsayılan 50
):
    all_products_docs = repo.list_products_repo(query={}, limit=2000)
    grouped_products = defaultdict(list)
    for p_doc in all_products_docs:
        product = ProductPublic(**p_doc)
        grouped_products[product.source].append(product)
    
    # Her kaynak için veriyi sayfalandırıyoruz
    paginated_data = {}
    for source, items in grouped_products.items():
        total_items = len(items)
        total_pages = math.ceil(total_items / size)
        
        # URL'den gelen sayfa numarasını o kaynağın sayfa parametresi olarak alıyoruz
        # Örn: /show-products?books_page=2&quotes_page=1
        source_page_query = f"{source}_page"
        current_page = int(request.query_params.get(source_page_query, 1))

        start_index = (current_page - 1) * size
        end_index = start_index + size
        
        paginated_items = items[start_index:end_index]
        
        paginated_data[source] = {
            "items": paginated_items,
            "total_pages": total_pages,
            "current_page": current_page,
            "total_items": total_items,
            "page_query_param": source_page_query
        }

    return templates.TemplateResponse(
        "products.html", 
        {
            "request": request, 
            "paginated_data": paginated_data,
            "query_params": request.query_params
        }
    )