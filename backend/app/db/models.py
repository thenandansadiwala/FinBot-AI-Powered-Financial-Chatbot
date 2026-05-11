from datetime import date
from typing import List, Optional, Any

from sqlalchemy import Integer, String, Float, Date, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class AMCProfile(Base):
    __tablename__ = "amc_profiles"

    amc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amc_name: Mapped[str] = mapped_column(String, unique=True, index=True)
    total_aum_cr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    funds: Mapped[List["FundMaster"]] = relationship(back_populates="amc", cascade="all, delete-orphan")


class FundCategory(Base):
    __tablename__ = "fund_categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    primary_category: Mapped[str] = mapped_column(String, index=True)
    sub_category: Mapped[str] = mapped_column(String, index=True)

    # Relationships
    funds: Mapped[List["FundMaster"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class FundMaster(Base):
    __tablename__ = "funds_master"

    ticker_symbol: Mapped[str] = mapped_column(String, primary_key=True)
    fund_name: Mapped[str] = mapped_column(String, index=True)
    amc_id: Mapped[int] = mapped_column(ForeignKey("amc_profiles.amc_id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("fund_categories.category_id", ondelete="CASCADE"))
    expense_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fund_size_cr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inception_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_direct: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    amc: Mapped["AMCProfile"] = relationship(back_populates="funds")
    category: Mapped["FundCategory"] = relationship(back_populates="funds")
    nav_history: Mapped[List["NavHistory"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    embeddings: Mapped[List["FundEmbedding"]] = relationship(back_populates="fund", cascade="all, delete-orphan")


class NavHistory(Base):
    __tablename__ = "nav_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("funds_master.ticker_symbol", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    close_price: Mapped[float] = mapped_column(Float)

    # Relationships
    fund: Mapped["FundMaster"] = relationship(back_populates="nav_history")

    __table_args__ = (
        UniqueConstraint("ticker_symbol", "date", name="uq_ticker_date"),
    )


class FundEmbedding(Base):
    __tablename__ = "fund_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("funds_master.ticker_symbol", ondelete="CASCADE"), index=True)
    context_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Any] = mapped_column(Vector(1536))

    # Relationships
    fund: Mapped["FundMaster"] = relationship(back_populates="embeddings")
