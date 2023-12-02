from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from transactions import CustomerUserLink, Hire


class CustomerAddressLink(SQLModel, table=True):
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id", primary_key=True)
    address_id: Optional[int] = Field(default=None, foreign_key="address.id", primary_key=True)


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    street: str
    city: str = None
    state: str = None
    postcode: str

    customers: List["Customer"] = Relationship(back_populates="addresses", link_model=CustomerAddressLink)


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    addresses:List["Address"] = Relationship(back_populates="customers", link_model=CustomerAddressLink)
    hires:List["Hire"] = Relationship(back_populates="customer")
    users:List["User"] = Relationship(back_populates="customers", link_model=CustomerUserLink)
