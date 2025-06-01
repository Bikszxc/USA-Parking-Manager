from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from logic.models import create_reservation

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse("reservation_form.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def submit(request: Request, name: str = Form(...), owner_type: str = Form(...), email: str = Form(...), contact_number: str = Form(...), plate_number: str = Form(...), vehicle_type: str = Form(...), reservation_date: str = Form(...), reservation_time: str = Form(...)):

    if create_reservation(name, owner_type, email, contact_number, plate_number, vehicle_type, reservation_date, reservation_time):
        return templates.TemplateResponse("reservation_form.html", {"request": request, "message": "Submitted successfully!"})

    return templates.TemplateResponse("reservation_form.html", {"request": request, "message": "Failed to submit!"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
