"""
مدل‌های دیتابیس (SQLAlchemy).
جدول‌ها: users, orders
"""
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, Numeric
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from config import DATABASE_URL

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # تلگرام user id
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    product_key = Column(String(50), nullable=False)   # مثلا product_1
    plan_key = Column(String(20), nullable=False)       # مثلا 1m / 6m / 12m
    price_usd = Column(Numeric(10, 2), nullable=False)

    status = Column(String(20), default="awaiting_receipt")
    # awaiting_receipt -> pending_review -> approved / rejected

    receipt_file_id = Column(String(255), nullable=True)

    admin_message_chat_id = Column(BigInteger, nullable=True)
    admin_message_id = Column(BigInteger, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(BigInteger, nullable=True)

    user = relationship("User", back_populates="orders")


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """ساخت جدول‌ها در صورت عدم وجود."""
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
