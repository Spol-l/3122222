import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env!")

app = FastAPI(title="Warhammer 40k Unified Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    chapter = Column(String)
    rank = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    subscriptions = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, nullable=False)
    is_yearly = Column(Boolean, default=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default="active")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="subscriptions")



Base.metadata.create_all(bind=engine)



class SpaceMarineCreate(BaseModel):
    name: str
    chapter: str
    rank: str
    email: str
    password: str


class SpaceMarineResponse(SpaceMarineCreate):
    id: int

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    email: str
    plan_name: str
    is_yearly: bool


class SubscriptionResponse(BaseModel):
    success: bool
    message: str
    data: dict



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/marines", response_model=SpaceMarineResponse)
def create_marine(marine: SpaceMarineCreate, db: SessionLocal = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == marine.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")

    db_user = User(**marine.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/marines", response_model=list[SpaceMarineResponse])
def get_marines(db: SessionLocal = Depends(get_db)):
    return db.query(User).all()



@app.post("/api/subscribe", response_model=SubscriptionResponse)
def create_subscription(sub_data: SubscriptionCreate, db: SessionLocal = Depends(get_db)):

    user = db.query(User).filter(User.email == sub_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден. Сначала зарегистрируйтесь через /marines.")


    months = 12 if sub_data.is_yearly else 1
    end_date = datetime.utcnow() + timedelta(days=months * 30)


    new_sub = Subscription(
        plan_name=sub_data.plan_name,
        is_yearly=sub_data.is_yearly,
        end_date=end_date,
        user_id=user.id,
        status="active"
    )

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    return SubscriptionResponse(
        success=True,
        message="Подписка оформлена успешно!",
        data={
            "userId": user.id,
            "plan": new_sub.plan_name,
            "duration": "1 год" if new_sub.is_yearly else "1 месяц",
            "expiresAt": new_sub.end_date.isoformat(),
            "status": new_sub.status
        }
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Warhammer Backend is running"}


if __name__ == "__main__":
    import uvicorn


    uvicorn.run(app, host="0.0.0.0", port=8000)
