from datetime import date, datetime
from sqlalchemy import ForeignKey, String, Float, Integer, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=3.0)  # 1-5 reliability score
    quotes: Mapped[list["Quote"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(20), default="pcs")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    unit_price: Mapped[float] = mapped_column(Float)
    lead_time_days: Mapped[int] = mapped_column(Integer)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    supplier: Mapped[Supplier] = relationship(back_populates="quotes")
    product: Mapped[Product] = relationship(back_populates="quotes")
