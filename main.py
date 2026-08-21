from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import registration
from routers import subscriptions



Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Warhammer 40k Unified Backend"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Роуты
app.include_router(registration.router)
app.include_router(subscriptions.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Warhammer Backend is running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )