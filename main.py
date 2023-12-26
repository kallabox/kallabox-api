from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api.models as models
import api.database as database
import api.income as income
import api.expenditure as expenditure
import api.user as user
import api.expense_type as expense_type
import api.account as account
import api.super_admin as super_admin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(income.router)
app.include_router(user.router)
app.include_router(expenditure.router)
app.include_router(expense_type.router)
app.include_router(account.router)
app.include_router(super_admin.router)


@app.get("/")
def root():
    return {"message": "Hello world"}
