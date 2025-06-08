from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib
import os

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB setup

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["portfolio_db"]
users = db["users"]
portfolios = db["portfolios"]
likes = db["likes"]

security = HTTPBasic()

# Models
class User(BaseModel):
    username: str
    password: str

class Portfolio(BaseModel):
    username: str
    theme: str
    title: str
    overview: str
    media: list[str] = []
    timeline: str = ""
    tools: list[str] = []
    outcomes: str = ""
    views: int = 0
    likes: int = 0

# Helper function
def get_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Auth routes
@app.post("/register")
def register(user: User):
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user.password)
    users.insert_one(user_dict)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: User):
    existing = users.find_one({"username": user.username})
    if not existing or get_password_hash(user.password) != existing["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

# Portfolio routes
@app.post("/portfolio")
def save_portfolio(data: Portfolio):
    data_dict = data.dict()
    data_dict["views"] = 0
    data_dict["likes"] = 0
    result = portfolios.insert_one(data.dict())
    return {"message": "Saved", "id": str(result.inserted_id)}

@app.get("/portfolio/{username}")
def get_user_portfolios(username: str):
    result = list(portfolios.find({"username": username}))
    for r in result:
        r["id"] = str(r["_id"])
        del r["_id"]
    return result

@app.get("/portfolios")
def get_all_portfolios():
    result = list(portfolios.find())
    for r in result:
        r["id"] = str(r["_id"])
        del r["_id"]
    return result

@app.post("/portfolio/view/{portfolio_id}")
def increment_view(portfolio_id: str, request: Request):
    data = request.query_params
    viewer = data.get("viewer")
    portfolio = portfolios.find_one({"_id": ObjectId(portfolio_id)})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio["username"] != viewer:
        portfolios.update_one({"_id": ObjectId(portfolio_id)}, {"$inc": {"views": 1}})
    return {"message": "View counted"}

@app.post("/portfolio/like/{portfolio_id}")
def like_portfolio(portfolio_id: str, request: Request):
    data = request.query_params
    liker = data.get("liker")
    if likes.find_one({"portfolio_id": portfolio_id, "liker": liker}):
        raise HTTPException(status_code=400, detail="Already liked")
    likes.insert_one({"portfolio_id": portfolio_id, "liker": liker})
    portfolios.update_one({"_id": ObjectId(portfolio_id)}, {"$inc": {"likes": 1}})
    return {"message": "Liked"}