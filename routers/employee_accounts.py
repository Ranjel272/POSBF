from fastapi import APIRouter, HTTPException, Depends, status, Form
from datetime import datetime
from database import get_db_connection
from routers.auth import get_current_active_user, role_required, get_password_hash

router = APIRouter()

# 🟢 Admin: Create a new employee account
@router.post('/create', dependencies=[Depends(role_required(["admin"]))])
async def create_user(
    fullName: str = Form(...),
    username: str | None = Form(None),  # Cashiers may not have usernames
    password: str | None = Form(None),  # Admin/Managers use passwords
    passcode: str | None = Form(None),  # Cashiers use passcodes
    userRole: str = Form(...)
):
    if userRole not in ['admin', 'manager', 'cashier']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    if userRole == 'cashier' and not passcode:
        raise HTTPException(status_code=400, detail="Cashiers require a passcode")
    
    if userRole in ['admin', 'manager'] and not password:
        raise HTTPException(status_code=400, detail="Admins & Managers require a password")

    hashed_password = get_password_hash(password) if password else None
    hashed_passcode = get_password_hash(passcode) if passcode else None

    conn = await get_db_connection()
    cursor = await conn.cursor()

    try:
        await cursor.execute('''
            INSERT INTO Users (FullName, Username, UserPassword, Passcode, UserRole)
            VALUES (?, ?, ?, ?, ?)
        ''', (fullName, username, hashed_password, hashed_passcode, userRole))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

    return {'message': 'User created successfully!'}

# 🟢 Admin: Fetch all active employee accounts
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

# 🟢 Admin: Update an employee account
@router.put("/update/{user_id}", dependencies=[Depends(role_required(['admin']))])
async def update_user(
    user_id: int,
    fullName: str | None = Form(None),
    password: str | None = Form(None),
    passcode: str | None = Form(None)
):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    
    updates = []
    values = []

    if fullName:
        updates.append('FullName = ?')
        values.append(fullName)
    if password:
        hashed_password = get_password_hash(password)
        updates.append('UserPassword = ?')
        values.append(hashed_password)
    if passcode:
        hashed_passcode = get_password_hash(passcode)
        updates.append('Passcode = ?')
        values.append(hashed_passcode)
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

# 🟢 Admin: Soft-delete an employee account
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

# 🟢 Employee: Update their own account details
@router.put('/self-update', dependencies=[Depends(role_required(['cashier', 'manager']))])
async def update_self(
    fullName: str | None = Form(None),
    password: str | None = Form(None),
    passcode: str | None = Form(None),
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
        hashed_password = get_password_hash(password)
        updates.append("UserPassword = ?")
        values.append(hashed_password)
    if passcode:
        hashed_passcode = get_password_hash(passcode)
        updates.append("Passcode = ?")
        values.append(hashed_passcode)
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
