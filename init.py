from database import engine, Base
import models  # ensures all models are imported and registered with Base

def init():
    print("🚀 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    init()
