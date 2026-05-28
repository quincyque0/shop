import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import grpc
from pydantic import BaseModel
from contextlib import asynccontextmanager

from database import engine, Base, get_session, async_session
from models import Product
import catalog_pb2
import catalog_pb2_grpc

app = FastAPI(title="Catalog Service")


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int


class ProductOut(ProductCreate):
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    server = grpc.aio.server()
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(
        CatalogService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()

    yield
    await server.stop(0)

app.router.lifespan_context = lifespan


@app.post("/api/products", response_model=ProductOut)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_session)):
    new_product = Product(**product.dict())
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product


@app.get("/api/products", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product))
    products = result.scalars().all()
    return products


class CatalogService(catalog_pb2_grpc.CatalogServiceServicer):
    async def CheckProduct(self, request, context):
        async with async_session() as session:
            result = await session.execute(select(Product).filter(Product.id == request.product_id))
            product = result.scalars().first()
            if product:
                return catalog_pb2.CheckProductResponse(
                    exists=True,
                    price=product.price,
                    name=product.name
                )
            return catalog_pb2.CheckProductResponse(exists=False)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
