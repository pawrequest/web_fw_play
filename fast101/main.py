from datetime import timedelta
from typing import Annotated, List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

import db
import fixtures  # beware import order matters!
import products
import transactions
from store import SessionData, backend, cookie, verifier
from users import ACCESS_TOKEN_EXPIRE_MINUTES, Token, User, authenticate_user, create_access_token, \
    get_current_active_user

app = FastAPI()


@app.on_event("startup")
def on_startup():
    fixtures.create_db()
    fixtures.create_data()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/hires/", response_model=list[transactions.HireRead])
# async def read_hires(*, session: Session = Depends(db.get_session)):
#     hires = session.exec(select(transactions.Hire)).all()
#     hires_data = []
#     for hire in hires:
#         hire_data = hire.dict()
#         hire_data['customer_name'] = hire.customer.name
#         hires_data.append(hire_data)
#     # hd_filtered = [hd for hd in hires_data if hd['customer_name'] != session.get(
#     #
#     # ).name]
#     return hires_data


@app.get("/hires/", response_model=List[transactions.HireRead])
async def read_hires(*, session: Session = Depends(db.get_session),
                     current_user: Annotated[User, Depends(get_current_active_user)]):
    hires = session.exec(select(transactions.Hire)).all()
    hires_data = []
    for hire in hires:
        hire_data = hire.dict()
        hire_data['customer_name'] = hire.customer.name
        hires_data.append(hire_data)
    hd_filtered = [hd for hd in hires_data if hd['customer_name'] == current_user.username]
    return hd_filtered


@app.get("/radios/{radio_id}", response_model=products.RadioRead)
async def read_radio(*, session: Session = Depends(db.get_session), radio_id=1):
    rad = session.get(products.Radio, radio_id)
    radio_data = rad.dict()

    if rad.sales_price_profile:
        radio_data["sales_prices"] = rad.sales_price_profile.prices

    if rad.hire_price_profile:
        radio_data["hire_prices"] = rad.hire_price_profile.prices

    return radio_data


@app.get("/radios/", response_model=list[products.RadioRead])
async def read_radios(*, session: Session = Depends(db.get_session)):
    radios = session.exec(select(products.Radio)).all()
    return radios


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: Annotated[User, Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]


#
# @app.post("/create_session/{name}")
# async def create_session(name: str, response: Response):
#
#     session = uuid4()
#     data = SessionData(username=name)
#
#     await backend.create(session, data)
#     cookie.attach_to_response(response, session)
#
#     return f"created session for {name}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"
