from fastapi import FastAPI
from app.routers import users, courses, reports

app = FastAPI()

# Routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
@app.get("/")
def root():
    return {"message": "Welcome to Study Tracker API"}
