from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class SalePriceProfileLink(SQLModel, table=True):
    price_id: Optional[int] = Field(default=None, foreign_key="saleprice.id", primary_key=True)
    profile_id: Optional[int] = Field(default=None, foreign_key="salepriceprofile.id", primary_key=True)


class SalePrice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int
    price: float

    profiles: List["SalePriceProfile"] = Relationship(back_populates="prices", link_model=SalePriceProfileLink)


class SalePriceProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    prices: List[SalePrice] = Relationship(back_populates="profiles", link_model=SalePriceProfileLink)
    products: List["Radio"] = Relationship(back_populates="sales_price_profile")


class HirePriceProfileLink(SQLModel, table=True):
    price_id: Optional[int] = Field(default=None, foreign_key="hireprice.id", primary_key=True)
    profile_id: Optional[int] = Field(default=None, foreign_key="hirepriceprofile.id", primary_key=True)


class HirePrice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    weeks: int
    quantity: int
    price: float

    hire_price_profiles: List["HirePriceProfile"] = Relationship(back_populates="prices",
                                                                 link_model=HirePriceProfileLink)


class RadioHireProfileLink(SQLModel, table=True):
    radio_id: Optional[int] = Field(default=None, foreign_key="radio.id", primary_key=True)
    profile_id: Optional[int] = Field(default=None, foreign_key="hirepriceprofile.id", primary_key=True)

class HirePriceProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    prices: List[HirePrice] = Relationship(back_populates="hire_price_profiles", link_model=HirePriceProfileLink)
    products: List["Radio"] = Relationship(back_populates="hire_price_profile", link_model=RadioHireProfileLink)
