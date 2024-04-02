import datetime
from typing import List

import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

DATABASE_URL = "sqlite:///less_6_users.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
...
# engine = sqlalchemy.create_engine(DATABASE_URL)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("firstname", sqlalchemy.String(32)),
    sqlalchemy.Column("lastname", sqlalchemy.String(32)),
    sqlalchemy.Column("birthday", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("address", sqlalchemy.String(128)),
)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class User(BaseModel):
    firstname: str = Field(title="firstname", max_length=32)
    lastname: str = Field(title="lastname", max_length=32)
    birthday: str = Field(title="Birthday", max_length=32)
    email: str = Field(title="Email", max_length=128)
    address: str = Field(title="address", min_length=5)


class User_with_ID(User):
    user_id: int = Field(title="ID")


@app.get("/fake_users/{count}")
async def create_note(count: int):
    for i in range(count):
        query = users.insert().values(
            firstname=f'firstname {i}',
            lastname=f'lastname {i}',
            birthday=f'{datetime.datetime.today().strftime("%Y-%m-%d")}',
            email=f'email {i}',
            address=f'{i}{i}{i}{i}{i}'
        )
        await database.execute(query)
    return {"message": f"{count} fake users create"}


# create
@app.post("/users/", response_model=User_with_ID)
async def create_user(user: User):
    query = users.insert().values(
        firstname=user.firstname, lastname=user.lastname, birthday=user.birthday, email=user.email, address=user.address
    )
    last_record_id = await database.execute(query)
    # print(user.model_dump())
    return {**user.model_dump(), "user_id": last_record_id}


# @app.get("/users/", response_model=List[User_with_ID])
# async def read_users():
# query = users.select()
# return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=User_with_ID)
async def get_user(user_id: int):
    query = users.select().where(users.c.user_id == user_id)
    return await database.fetch_one(query)


@app.get("/users/", response_model=List[User_with_ID])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
