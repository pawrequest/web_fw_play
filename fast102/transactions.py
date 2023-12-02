from datetime import date, datetime
from typing import Optional

from sqlalchemy import Enum
from sqlmodel import Field, Relationship, SQLModel

class CustomerUserLink(SQLModel, table=True):
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)


class PaymentStatus(str, Enum):
    PENDING = 'Pending'
    PAID = 'Paid'
    REFUNDED = 'Refunded'
    CANCELLED = 'Cancelled'


class TransactionBase(SQLModel):
    # date_created: datetime = datetime.utcnow()
    date_created: datetime = Field(default_factory=datetime.utcnow)
    customer_id: int = Field(default=None, foreign_key="customer.id")

    # payment_status:PaymentStatus = Field(Enum(PaymentStatus), default=PaymentStatus.PENDING, sa_column=Enum(PaymentStatus))
    # payment_status= Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    # payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, sa_column=Column(String, index=True))


class Hire(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_due_return:date
    date_due_send:date

    customer: Optional["Customer"] = Relationship(back_populates="hires")

class HireRead(Hire):
    customer_name: str




