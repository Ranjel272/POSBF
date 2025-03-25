from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
# from routers import inventory, auth, purchase_order, employee_accounts
from routers import auth, employee_accounts
import uvicorn

app = FastAPI()

# mount the frontend folder 
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('frontend/LOG_IN_PAGE.html', 'r') as file:
        content = file.read()
    return HTMLResponse(content)

# include routers 
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(employee_accounts.router, prefix='/employee-accounts', tags=['employee-accounts'])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://127.0.0.1"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        port=8000, 
        host="127.0.0.1", 
        reload=True
    )
