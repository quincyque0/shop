import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="API Gateway")

CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog-svc:8000")
ORDER_URL = os.getenv("ORDER_URL", "http://order-svc:8000")


async def proxy_request(request: Request, base_url: str, path: str):
    url = f"{base_url}/{path}"
    async with httpx.AsyncClient() as client:
        try:
            req_body = await request.body()
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=req_body,
                params=request.query_params
            )
            return JSONResponse(content=response.json() if response.content else None, status_code=response.status_code)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, detail=f"Service unavailable: {exc}")


@app.api_route("/api/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catalog_proxy(request: Request, path: str):
    return await proxy_request(request, CATALOG_URL, f"api/products/{path}")


@app.api_route("/api/products", methods=["GET", "POST"])
async def catalog_root_proxy(request: Request):
    return await proxy_request(request, CATALOG_URL, "api/products")


@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def order_proxy(request: Request, path: str):
    return await proxy_request(request, ORDER_URL, f"api/orders/{path}")


@app.api_route("/api/orders", methods=["GET", "POST"])
async def order_root_proxy(request: Request):
    return await proxy_request(request, ORDER_URL, "api/orders")


@app.get("/health")
def health():
    return {"status": "ok"}
