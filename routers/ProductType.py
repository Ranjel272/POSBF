from fastapi import APIRouter, Form, Depends, HTTPException, status
from database import get_db_connection
from routers.auth import get_current_active_user, role_required

router = APIRouter()

# Create Product Type Route (Only admin can access)
@router.post("/create", dependencies=[Depends(role_required(["admin"]))])
async def create_product_type(
    productTypeName: str = Form(...),
    current_user=Depends(get_current_active_user)
):
    conn = await get_db_connection()
    cursor = await conn.cursor()

    # Check if product type already exists
    await cursor.execute("SELECT 1 FROM ProductType WHERE productTypeName = ?", (productTypeName,))
    if await cursor.fetchone():
        raise HTTPException(status_code=400, detail="Product type already exists")

    try:
        # Insert new product type into the ProductType table without specifying the auto-incremented productTypeID
        await cursor.execute('''
            INSERT INTO ProductType (productTypeName)
            VALUES (?)
        ''', (productTypeName,))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

    return {"message": "Product type created successfully"}
