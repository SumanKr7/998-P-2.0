from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Home pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "current_path": request.url.path})

# About
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "current_path": request.url.path})

# Contact
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "current_path": request.url.path})

@app.get("/professionals", response_class=HTMLResponse)
async def professionals(request: Request):
    return templates.TemplateResponse("professionals.html", {"request": request, "current_path": request.url.path})

@app.get("/products-and-services", response_class=HTMLResponse)
async def products_and_services(request: Request):
    return templates.TemplateResponse("products-and-services.html", {"request": request, "current_path": request.url.path})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "current_path": request.url.path})