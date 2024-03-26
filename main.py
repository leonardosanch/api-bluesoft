from fastapi import FastAPI
import uvicorn
from app.routers import user
from app.db.models import Base
from app.db.database import engine

app = FastAPI()
app.include_router(user.router)

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
