from fastapi import APIRouter, HTTPException, Depends, status, Form
from datetime import datetime
from database import get_db_connection
from routers.auth import get_current_active_user, role_required
import bcrypt

router = APIRouter()

@router.post('/create', dependencies=[Depends(role_required(["admin"]))])
async def create_user(
    fullName: str = Form(...),
    username: str = Form(None),
    password: str = Form(...),
    userRole: str = Form(...),
    current_user=Depends(get_current_active_user)
):
    if userRole not in ['admin', 'manager', 'cashier']:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not password.strip():
        raise HTTPException(status_code=400, detail="Password is required")

    conn = await get_db_connection()
    cursor = await conn.cursor()

    # Check if FullName already exists for any role
    await cursor.execute("SELECT 1 FROM Users WHERE FullName = ? AND isDisabled = 0", (fullName,))
    if await cursor.fetchone():
        raise HTTPException(status_code=400, detail="Full name is already used")

    if userRole == 'cashier':
        username = "cashier"

        # Check if the password is already used by another active cashier
        await cursor.execute('''
            SELECT UserPassword FROM Users WHERE UserRole = 'cashier' AND isDisabled = 0
        ''')
        all_cashier_passwords = await cursor.fetchall()
        for row in all_cashier_passwords:
            if bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8')):
                raise HTTPException(status_code=400, detail="This password is already used by another cashier.")
    else:
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="Username is required for admin/manager roles")

        # Check if the username already exists
        await cursor.execute("SELECT 1 FROM Users WHERE Username = ? AND isDisabled = 0", (username,))
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username is already taken")

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        await cursor.execute('''
            INSERT INTO Users (FullName, Username, UserPassword, UserRole, CreatedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (fullName, username, hashed_password, userRole, datetime.utcnow()))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

    return {'message': f'{userRole.capitalize()} created successfully!'}


@router.get('/list-employee-accounts', dependencies=[Depends(role_required(['admin']))])
async def list_users():
    conn = await get_db_connection()
    cursor = await conn.cursor()

    await cursor.execute(''' 
        SELECT UserID, FullName, Username, UserRole, CreatedAt
        FROM Users
        WHERE isDisabled = 0
    ''')
    users = await cursor.fetchall()
    await conn.close()

    return [{"userID": u[0], "fullName": u[1], "username": u[2], "userRole": u[3], "createdAt": u[4]}
            for u in users]


@router.put("/update/{user_id}", dependencies=[Depends(role_required(['admin']))])
async def update_user(
    user_id: int,
    fullName: str | None = Form(None),
    password: str | None = Form(None)
):
    conn = await get_db_connection()
    cursor = await conn.cursor()

    updates = []
    values = []

    if fullName:
        updates.append('FullName = ?')
        values.append(fullName)
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        updates.append('UserPassword = ?')
        values.append(hashed_password)
    updates.append('CreatedAt = ?')
    values.append(datetime.utcnow())

    values.append(user_id)

    if updates:
        try:
            await cursor.execute(f'''
                UPDATE Users
                SET {', '.join(updates)}
                WHERE UserID = ? AND isDisabled = 0
            ''', (*values,))
            await conn.commit()
        finally:
            await cursor.close()
            await conn.close()

        return {'message': 'User updated successfully'}

    return {'message': 'No fields to update'}


@router.delete('/delete/{user_id}', dependencies=[Depends(role_required(['admin']))])
async def delete_user(user_id: int):
    conn = await get_db_connection()
    cursor = await conn.cursor()

    try:
        await cursor.execute(''' 
            UPDATE Users
            SET isDisabled = 1
            WHERE UserID = ? 
        ''', (user_id,))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

    return {'message': 'User deleted successfully'}


@router.put('/self-update', dependencies=[Depends(role_required(['cashier', 'manager']))])
async def update_self(
    fullName: str | None = Form(None),
    password: str | None = Form(None),
    current_user=Depends(get_current_active_user)
):
    conn = await get_db_connection()
    cursor = await conn.cursor()

    updates = []
    values = []

    if fullName:
        updates.append("FullName = ?")
        values.append(fullName)
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        updates.append("UserPassword = ?")
        values.append(hashed_password)
    updates.append('CreatedAt = ?')
    values.append(datetime.utcnow())

    values.append(current_user.username)

    if updates:
        try:
            await cursor.execute(f'''
                UPDATE Users
                SET {', '.join(updates)}
                WHERE Username = ? AND isDisabled = 0
            ''', (*values,))
            await conn.commit()
        finally:
            await cursor.close()
            await conn.close()

        return {'message': 'Your account details have been updated!'}

    return {'message': 'No fields to update'}


