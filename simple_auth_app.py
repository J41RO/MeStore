import aiosqlite
from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_type: str = None


@app.post("/simple-login", response_model=LoginResponse)
async def simple_login(login_data: LoginRequest):
    """Simple authentication endpoint without complex dependencies"""

    try:
        async with aiosqlite.connect("./mestore_auth_test.db") as db:
            cursor = await db.execute(
                "SELECT password_hash, user_type, is_active FROM users WHERE email = ?",
                (login_data.email,),
            )
            user_data = await cursor.fetchone()

            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")

            password_hash, user_type, is_active = user_data

            if not is_active:
                raise HTTPException(status_code=401, detail="User not active")

            if pwd_context.verify(login_data.password, password_hash):
                return LoginResponse(
                    success=True,
                    message="Authentication successful",
                    user_type=user_type,
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid password")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Simple MeStore Auth"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
