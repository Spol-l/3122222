from pydantic import BaseModel


# =========================
# РЕГИСТРАЦИЯ
# =========================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


# =========================
# ВХОД
# =========================

class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# ПОДПИСКА
# =========================

class SubscriptionCreate(BaseModel):
    email: str
    plan_name: str
    is_yearly: bool = False


class SubscriptionData(BaseModel):
    userId: int
    subscriptionId: int
    plan: str
    duration: str
    expiresAt: str
    status: str
    code: str


class SubscriptionResponse(BaseModel):
    success: bool
    message: str
    data: SubscriptionData