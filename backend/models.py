#Author: Carly Shearer
#Purpose: Connects database to Python APIs.

from sqlalchemy import create_engine, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

#Connect to database
DATABASE_URL = "sqlite:///./portfolio.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

#Pass database information from SQL to Python for use
class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id")
    )

    ticker: Mapped[str] = mapped_column(String(50))
    asset_type: Mapped[str] = mapped_column(String(20))
    value: Mapped[float] = mapped_column(Float)

    apy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    maturity_date: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id")
    )

    description: Mapped[str] = mapped_column(String(200))
    time_horizon_years: Mapped[int] = mapped_column()
    risk_tolerance: Mapped[str] = mapped_column(String(20))

class ETFHolding(Base):
    __tablename__ = "etf_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)

    etf_ticker: Mapped[str] = mapped_column(String(20))
    holding_ticker: Mapped[str] = mapped_column(String(20))
    weight: Mapped[float] = mapped_column(Float)