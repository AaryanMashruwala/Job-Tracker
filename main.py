from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Application

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "applications": applications
    })


@app.post("/add")
def add_application(
    company: str = Form(...),
    role: str = Form(...),
    url: str = Form(""),
    date_applied: str = Form(...),
    status: str = Form("Applied"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    application = Application(
        company=company,
        role=role,
        url=url,
        date_applied=date_applied,
        status=status,
        notes=notes
    )
    db.add(application)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == app_id).first()
    if application:
        db.delete(application)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
