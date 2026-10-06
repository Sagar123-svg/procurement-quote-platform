from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .ranking import rank_quotes
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Procurement Quote Platform", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Suppliers ----------
@app.post("/suppliers", response_model=schemas.SupplierOut, status_code=201)
def create_supplier(payload: schemas.SupplierCreate, db: Session = Depends(get_db)):
    supplier = models.Supplier(**payload.model_dump())
    db.add(supplier)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Supplier with this name already exists")
    db.refresh(supplier)
    return supplier


@app.get("/suppliers", response_model=list[schemas.SupplierOut])
def list_suppliers(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.scalars(select(models.Supplier).offset(skip).limit(limit)).all()


@app.get("/suppliers/{supplier_id}", response_model=schemas.SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    return supplier


@app.put("/suppliers/{supplier_id}", response_model=schemas.SupplierOut)
def update_supplier(supplier_id: int, payload: schemas.SupplierCreate, db: Session = Depends(get_db)):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    for key, value in payload.model_dump().items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.delete("/suppliers/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    db.delete(supplier)
    db.commit()


# ---------- Products ----------
@app.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Product with this name already exists")
    db.refresh(product)
    return product


@app.get("/products", response_model=list[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.scalars(select(models.Product).offset(skip).limit(limit)).all()


# ---------- Quotes ----------
@app.post("/quotes", response_model=schemas.QuoteOut, status_code=201)
def create_quote(payload: schemas.QuoteCreate, db: Session = Depends(get_db)):
    if not db.get(models.Supplier, payload.supplier_id):
        raise HTTPException(404, "Supplier not found")
    if not db.get(models.Product, payload.product_id):
        raise HTTPException(404, "Product not found")
    quote = models.Quote(**payload.model_dump())
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@app.get("/quotes", response_model=list[schemas.QuoteOut])
def list_quotes(product_id: int | None = None, supplier_id: int | None = None,
                skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(models.Quote)
    if product_id is not None:
        stmt = stmt.where(models.Quote.product_id == product_id)
    if supplier_id is not None:
        stmt = stmt.where(models.Quote.supplier_id == supplier_id)
    return db.scalars(stmt.order_by(models.Quote.id).offset(skip).limit(limit)).all()
# ---------- Compare ----------
@app.get("/products/{product_id}/compare", response_model=list[schemas.RankedQuote])
def compare_quotes(product_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Product, product_id):
        raise HTTPException(404, "Product not found")
    quotes = db.scalars(select(models.Quote).where(models.Quote.product_id == product_id)).all()
    return rank_quotes(quotes)