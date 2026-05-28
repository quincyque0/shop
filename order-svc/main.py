import os
import json
import asyncio
import grpc
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from contextlib import asynccontextmanager
import aio_pika

from database import engine, Base, get_session
from models import Order
import catalog_pb2
import catalog_pb2_grpc

app = FastAPI(title="Order Service")

CATALOG_GRPC_URL = os.getenv("CATALOG_GRPC_URL", "localhost:50051")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@localhost:5672/")

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    customer_email: str

class OrderOut(OrderCreate):
    id: int
    total_price: float
    status: str
mq_connection = None
mq_channel = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mq_connection, mq_channel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    try:
        mq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
        mq_channel = await mq_connection.channel()
        await mq_channel.declare_queue("notifications", durable=True)
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        
    yield
    
    if mq_connection:
        await mq_connection.close()

app.router.lifespan_context = lifespan

async def check_product_in_catalog(product_id: int):
    async with grpc.aio.insecure_channel(CATALOG_GRPC_URL) as channel:
        stub = catalog_pb2_grpc.CatalogServiceStub(channel)
        try:
            response = await stub.CheckProduct(catalog_pb2.CheckProductRequest(product_id=product_id))
            return response
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            raise HTTPException(status_code=503, detail="Catalog service unavailable")

@app.post("/api/orders", response_model=OrderOut)
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_session)):
    catalog_response = await check_product_in_catalog(order.product_id)
    if not catalog_response.exists:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
        
    total_price = catalog_response.price * order.quantity
    
    new_order = Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        customer_email=order.customer_email,
        status="CREATED"
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    
    if mq_channel:
        message_body = json.dumps({
            "event": "OrderCreated",
            "order_id": new_order.id,
            "product_name": catalog_response.name,
            "total_price": new_order.total_price,
            "customer_email": new_order.customer_email
        }).encode()
        
        await mq_channel.default_exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="notifications",
        )
        
    return new_order

@app.get("/api/orders", response_model=list[OrderOut])
async def list_orders(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Order))
    orders = result.scalars().all()
    return orders

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
