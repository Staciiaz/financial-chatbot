from typing import Optional

from pydantic import BaseModel, Field


class FinancialData(BaseModel):
    company: str = Field(..., description="Name of the company")
    ticker: str = Field(..., description="Stock ticker symbol")
    sector: str = Field(..., description="Industry sector")
    year: int = Field(..., description="Fiscal year of the financial data")
    revenue: Optional[float] = Field(None, description="Total revenue for the fiscal year")
    net_income: Optional[float] = Field(None, description="Net income for the fiscal year")
    operating_income: Optional[float] = Field(None, description="Operating income for the fiscal year")
    gross_profit: Optional[float] = Field(None, description="Gross profit for the fiscal year")
