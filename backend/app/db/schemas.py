from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

# --- AMC Profiles ---

class AMCProfileBase(BaseModel):
    amc_name: str
    total_aum_cr: Optional[float] = None

class AMCProfileCreate(AMCProfileBase):
    pass

class AMCProfileResponse(AMCProfileBase):
    amc_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Fund Categories ---

class FundCategoryBase(BaseModel):
    primary_category: str
    sub_category: str

class FundCategoryCreate(FundCategoryBase):
    pass

class FundCategoryResponse(FundCategoryBase):
    category_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Funds Master ---

class FundMasterBase(BaseModel):
    ticker_symbol: str
    fund_name: str
    amc_id: int
    category_id: int
    expense_ratio: Optional[float] = None
    fund_size_cr: Optional[float] = None
    inception_date: Optional[date] = None
    is_direct: bool = False

class FundMasterCreate(FundMasterBase):
    pass

class FundMasterResponse(FundMasterBase):
    model_config = ConfigDict(from_attributes=True)

# --- NAV History ---

class NavHistoryBase(BaseModel):
    ticker_symbol: str
    date: date
    close_price: float

class NavHistoryCreate(NavHistoryBase):
    pass

class NavHistoryResponse(NavHistoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Fund Embeddings ---

class FundEmbeddingBase(BaseModel):
    ticker_symbol: str
    context_text: str
    embedding: List[float] = Field(..., max_length=1536, min_length=1536)

class FundEmbeddingCreate(FundEmbeddingBase):
    pass

class FundEmbeddingResponse(FundEmbeddingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
