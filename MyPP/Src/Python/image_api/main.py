from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

from models import Base, Image
from schemas import ImageCreate, ImageInfo, RenameImage, ImageResponse

import aiofiles

DATABASE_URL = "sqlite:///./images.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    images = db.query(Image).all()
    return templates.TemplateResponse("index.html", {
    "request": request, "images": images})

@app.post("/upload/")
async def upload_image(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    filename_ext = os.path.splitext(file.filename)[1].lower()
    save_path = os.path.join(UPLOAD_FOLDER, name + filename_ext)

    if os.path.exists(save_path):
        return templates.TemplateResponse("index.html", {
            "request": Request,
            "error": "Файл с таким именем уже существует.",
            "images": db.query(Image).all()
        })

    async with aiofiles.open(save_path, 'wb') as out_file:
        await out_file.write(contents)

    try:
        with PILImage.open(save_path) as img:
            width, height = img.size
            format_type = img.format.lower()
            size_bytes = len(contents)

            new_image = Image(
                name=name,
                size=size_bytes,
                width=width,
                height=height,
                type=format_type,
                date_added=datetime.utcnow(),
                file_path=save_path,
            )
            db.add(new_image)
            db.commit()
            db.refresh(new_image)
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        os.remove(save_path)
        return templates.TemplateResponse("index.html", {
            "request": Request,
            "error": f"Ошибка обработки изображения: {e}",
            "images": db.query(Image).all()
        })

@app.get("/info/{image_id}")
def get_image_info(image_id: int, request: Request, db: Session = Depends(get_db)):
    image_record = db.query(Image).filter(Image.id == image_id).first()
    if not image_record:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Изображение не найдено.",
            "images": db.query(Image).all()
        })
    return templates.TemplateResponse("index.html", {
        "request": request,
        "images": db.query(Image).all(),
        "info_image": image_record,
        "show_info": True,
    })

@app.post("/rename/{image_id}")
def rename_image(image_id: int, new_name: str = Form(...), db: Session = Depends(get_db)):
    image_record = db.query(Image).filter(Image.id == image_id).first()
    if not image_record:
        return RedirectResponse("/", status_code=303)

    old_path = image_record.file_path
    filename_ext = os.path.splitext(old_path)[1]
    new_path = os.path.join(UPLOAD_FOLDER, new_name + filename_ext)

    if os.path.exists(new_path):
        return RedirectResponse("/", status_code=303)

    try:
        os.rename(old_path, new_path)
        image_record.name = new_name
        image_record.file_path = new_path
        db.commit()
    except Exception:
        pass

    return RedirectResponse("/", status_code=303)

@app.get("/images/")
def list_images(db: Session = Depends(get_db)):
    images = db.query(Image).all()
    return images
