from fastapi import FastAPI
from services import router as auth_router
from database import Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include login routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
