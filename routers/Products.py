from fastapi import APIRouter, Form, Depends, HTTPException, status
from database import get_db_connection
from routers.auth import get_current_active_user, role_required

router = APIRouter()

# Create Product Route (Only admin can access)
@router.post("/add", dependencies=[Depends(role_required(["admin"]))])
async def create_product(
    productName: str = Form(...),
    productTypeName: str = Form(...),
    productCategory: str = Form(None),
    productDescription: str = Form(None),
    current_user=Depends(get_current_active_user)
):
    conn = await get_db_connection()
    cursor = await conn.cursor()

    # Check if the productTypeName exists in the ProductType table and get its ID
    await cursor.execute("SELECT productTypeID FROM ProductType WHERE productTypeName = ?", (productTypeName,))
    product_type = await cursor.fetchone()
    if not product_type:
        raise HTTPException(status_code=404, detail="Product type not found")

    productTypeID = product_type[0]

    try:
        # Insert the new product into the Products table
        await cursor.execute('''
            INSERT INTO Products (productName, productTypeID, productCategory, productDescription)
            VALUES (?, ?, ?, ?)
        ''', (productName, productTypeID, productCategory, productDescription))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

    return {"message": "Product added successfully"}
