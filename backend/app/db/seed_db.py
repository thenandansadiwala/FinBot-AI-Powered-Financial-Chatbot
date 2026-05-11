import asyncio
import logging
from datetime import datetime
import yfinance as yf
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from app.db.database import async_session_maker
from app.db.models import AMCProfile, FundCategory, FundMaster, NavHistory, FundEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data(tickers):
    async with async_session_maker() as session:
        for symbol in tickers:
            logger.info(f"Fetching data for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # --- 1. Extract Info ---
            amc_name = info.get("fundFamily", "Unknown AMC")
            category_name = info.get("category", "Uncategorized")
            fund_name = info.get("longName", symbol)
            # converting assets to Cr. Assuming USD for now. 1 Cr = 10,000,000
            total_assets = info.get("totalAssets")
            fund_size_cr = total_assets / 10_000_000 if total_assets else None
            
            inception_timestamp = info.get("fundInceptionDate")
            inception_date = datetime.fromtimestamp(inception_timestamp).date() if inception_timestamp else None
            
            expense_ratio = info.get("navPrice") # yfinance sometimes doesn't have expenseRatio reliably, but let's try
            if not expense_ratio:
                expense_ratio = info.get("expenseRatio", 0.0)

            summary = info.get("longBusinessSummary", "No summary available.")

            # --- 2. Insert AMC ---
            result = await session.execute(select(AMCProfile).filter_by(amc_name=amc_name))
            amc = result.scalars().first()
            if not amc:
                amc = AMCProfile(amc_name=amc_name, total_aum_cr=fund_size_cr)
                session.add(amc)
                await session.flush()
            elif fund_size_cr and (amc.total_aum_cr is None or amc.total_aum_cr < fund_size_cr):
                amc.total_aum_cr += fund_size_cr

            # --- 3. Insert Category ---
            result = await session.execute(select(FundCategory).filter_by(primary_category="ETF", sub_category=category_name))
            category = result.scalars().first()
            if not category:
                category = FundCategory(primary_category="ETF", sub_category=category_name)
                session.add(category)
                await session.flush()

            # --- 4. Insert Fund ---
            result = await session.execute(select(FundMaster).filter_by(ticker_symbol=symbol))
            fund = result.scalars().first()
            if not fund:
                fund = FundMaster(
                    ticker_symbol=symbol,
                    fund_name=fund_name,
                    amc_id=amc.amc_id,
                    category_id=category.category_id,
                    expense_ratio=expense_ratio,
                    fund_size_cr=fund_size_cr,
                    inception_date=inception_date,
                    is_direct=True # ETFs are generally direct
                )
                session.add(fund)
                await session.flush()
            
            # --- 5. Insert Embeddings (Dummy 1536 dim) ---
            result = await session.execute(select(FundEmbedding).filter_by(ticker_symbol=symbol))
            embedding_entry = result.scalars().first()
            if not embedding_entry:
                dummy_vector = [0.0] * 1536
                # Let's set the first element to a non-zero value just to be safe
                dummy_vector[0] = 1.0
                embedding_entry = FundEmbedding(
                    ticker_symbol=symbol,
                    context_text=summary,
                    embedding=dummy_vector
                )
                session.add(embedding_entry)

            # --- 6. Fetch and Insert NAV History ---
            hist = ticker.history(period="1y")
            if not hist.empty:
                for date, row in hist.iterrows():
                    nav_date = date.date()
                    close_price = float(row["Close"])
                    
                    # Upsert using PostgreSQL ON CONFLICT DO NOTHING
                    stmt = insert(NavHistory).values(
                        ticker_symbol=symbol,
                        date=nav_date,
                        close_price=close_price
                    ).on_conflict_do_nothing(
                        index_elements=['ticker_symbol', 'date']
                    )
                    await session.execute(stmt)

            await session.commit()
            logger.info(f"Successfully inserted {symbol}")

if __name__ == "__main__":
    # Expanded list of popular thematic and index ETFs
    tickers_to_seed = ["SPY", "QQQ", "VTI", "VOO", "ARKK", "SCHD", "IWM", "IVV"]
    asyncio.run(seed_data(tickers_to_seed))
