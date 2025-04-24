from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Routers
from routers import auth, employee_accounts, Products, ProductType

app = FastAPI()

# Serve static frontend files (if needed)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('frontend/LOG_IN_PAGE.html', 'r') as file:
        content = file.read()
    return HTMLResponse(content)

# Include routers
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(employee_accounts.router, prefix='/employee-accounts', tags=['employee-accounts'])
app.include_router(Products.router, prefix='/product', tags=['adding product'])
app.include_router(ProductType.router, prefix='/Product Type', tags=['adding Product Type'])

# CORS setup to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.100.10:3000"  # if accessing via local network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)
