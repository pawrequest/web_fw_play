from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from prices import HirePrice, HirePriceProfile, SalePrice, SalePriceProfile


class RadioBase(SQLModel):
    name: str = Field(index=True, unique=True)
    for_sale: bool
    for_hire: bool
    band: str

    sales_price_profile_id: Optional[int] = Field(default=None, foreign_key="salepriceprofile.id")
    hire_price_profile_id: Optional[int] = Field(default=None, foreign_key="hirepriceprofile.id")


class Radio(RadioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    sales_price_profile: Optional["SalePriceProfile"] = Relationship(back_populates="products")
    hire_price_profile: Optional["HirePriceProfile"] = Relationship(back_populates="products")


class RadioRead(RadioBase):
    id: int
    sales_prices: Optional[List[SalePrice]] = None
    hire_prices: Optional[List[HirePrice]] = None
    # sales_price_profile: Optional[SalePriceProfile] = None
    # hire_price_profile: Optional[HirePriceProfile] = None




class abstract(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)

    class Meta:
        abstract = True