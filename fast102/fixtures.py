from datetime import datetime
from typing import List

from sqlmodel import SQLModel, Session, select

from customers import Address, Customer
from db import engine
from prices import HirePrice, HirePriceProfile, SalePrice, SalePriceProfile
from products import Radio
from transactions import Hire
from users import User, get_password_hash


def create_db():
    SQLModel.metadata.create_all(engine)


def create_data():
    sale_prof = create_sale_profiles()
    hire_prof = create_hire_profiles()
    addresses = create_addresses()
    users = create_users()
    customers = create_customers(users=users, addresses=addresses)
    create_hires(customers=customers)
    create_radios(sale_profiles=sale_prof, hire_profiles=hire_prof)


def create_sale_profiles():
    with Session(engine) as session:
        profiles_ext = session.exec(select(SalePriceProfile)).all()
        profile_names = [i.name for i in profiles_ext]
        profiles = [
            SalePriceProfile(
                name='hytera_705',
                prices=[
                    SalePrice(quantity=1, price=100.00),
                    SalePrice(quantity=6, price=80.00),
                    SalePrice(quantity=12, price=60.00),
                ]
            ),
            SalePriceProfile(
                name='quansheng_330',
                prices=[
                    SalePrice(quantity=1, price=70.00),
                    SalePrice(quantity=6, price=50.00),
                    SalePrice(quantity=12, price=45.00),
                ]
            )]
        new_profiles = [profile for profile in profiles if profile.name not in profile_names]

        if new_profiles:
            [session.add(profile) for profile in new_profiles]
            session.commit()
    return profiles


def create_hire_profiles():
    with Session(engine) as session:
        profiles_ext = session.exec(select(HirePriceProfile)).all()
        profile_names = [i.name for i in profiles_ext]
        profiles = [
            HirePriceProfile(
                name='radio_hire_a',
                prices=[
                    HirePrice(weeks=1, quantity=1, price=10.00),
                    HirePrice(weeks=1, quantity=10, price=9.00),
                    HirePrice(weeks=1, quantity=20, price=8.00),
                    HirePrice(weeks=1, quantity=30, price=7.00),
                    HirePrice(weeks=2, quantity=1, price=8.00),
                    HirePrice(weeks=2, quantity=10, price=7.00),
                    HirePrice(weeks=2, quantity=20, price=6.00),
                    HirePrice(weeks=2, quantity=30, price=5.00),
                    HirePrice(weeks=4, quantity=1, price=6.00),
                    HirePrice(weeks=4, quantity=10, price=5.00),
                    HirePrice(weeks=4, quantity=20, price=4.00),
                    HirePrice(weeks=4, quantity=30, price=3.00),
                ]
            )
        ]
        new_profiles = [profile for profile in profiles if profile.name not in profile_names]
        [session.add(hire_profile) for hire_profile in new_profiles]
        session.commit()
    return profiles


def create_addresses():
    with Session(engine) as session:
        addresses_ext = session.exec(select(Address)).all()
        streets = [address.street for address in addresses_ext]
        addresses = [
            Address(
                street='1 Main Street',
                city='London',
                state='London',
                postcode='E1 1AA'
            ),
            Address(
                street='2 Other Street',
                city='Paris',
                state='Away',
                postcode='PPPPARIS'
            ),
        ]
        new_addresses = [address for address in addresses if address.street not in streets]
        if new_addresses:
            [session.add(address) for address in new_addresses]
            session.commit()
    return addresses


def create_users():
    with Session(engine) as session:
        users_ext = session.exec(select(User)).all()
        usernames_ext = [user.username for user in users_ext]
        users = [
            User(
                username='johndoe',
                email='joghndo@asdfg.com',
                full_name='John Doe',
                disabled=False,
                hashed_password=get_password_hash('secret')
            ),
            User(
                username='janedoe',
                email='jabneasfgj@asf.com',
                full_name='Jane Doe',
                disabled=False,
                hashed_password=get_password_hash('secrety')
            ),
        ]
        new_users = [user for user in users if user.username not in usernames_ext]
        if new_users:
            [session.add(user) for user in new_users]
            session.commit()
    return users


def create_customers(users: List[User], addresses: List[Address]):
    with Session(engine) as session:
        customers_ext = session.exec(select(Customer)).all()
        customer_names = [customer.name for customer in customers_ext]
        customers = [
            Customer(
                name='John Smith',
                addresses=[addresses[0]],
                users=[users[0]],
            ),
            Customer(
                name='Jane Doe',
                addresses=[addresses[1]],
                users=[users[1]],
            ),
        ]
        new_customers = [customer for customer in customers if customer.name not in customer_names]
        if new_customers:
            [session.add(customer) for customer in new_customers]
            session.commit()
    return customers


def create_hires(customers):
    with Session(engine) as session:
        ext_hires = session.exec(select(Hire)).all()
        due_dates = [hire.date_due_send for hire in ext_hires]
        hires = [
            Hire(customer=customers[0],
                 date_due_send=datetime(2023, 10, 1).date(),
                 date_due_return=datetime(2023, 11, 1).date()),
            Hire(customer=customers[1],
                 date_due_send=datetime(2023, 10, 5).date(),
                 date_due_return=datetime(2023, 12, 5).date()),
        ]
        new_hires = [hire for hire in hires if hire.date_due_send not in due_dates]
        if new_hires:
            [session.add(hire) for hire in new_hires]
            session.commit()
    return hires


def create_radios(sale_profiles: list, hire_profiles: list):
    with Session(engine) as session:
        radios_ext = session.exec(select(Radio)).all()
        radios_ext = [radio.name for radio in radios_ext]

        radios = [
            Radio(name='Hytera 705',
                  band='UHF',
                  for_sale=False,
                  for_hire=True,
                  hire_price_profile=hire_profiles[0]),
            Radio(name='Quansheng TG330',
                  band='UHF',
                  for_sale=True,
                  for_hire=False,
                  sales_price_profile=sale_profiles[0],
                  )
        ]
        new_radios = [radio for radio in radios if radio.name not in radios_ext]
        if new_radios:
            [session.add(radio) for radio in new_radios]
            session.commit()
    return radios
