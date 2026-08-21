from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models import User, Subscription

from schemas import (
    SubscriptionCreate,
    SubscriptionResponse
)

from dependencies import get_db

from utils.subscription_code import (
    generate_subscription_code
)


router = APIRouter(
    prefix="/api",
    tags=["Subscriptions"]
)



@router.post(
    "/subscribe",
    response_model=SubscriptionResponse
)
def create_subscription(
    sub_data: SubscriptionCreate,
    db: Session = Depends(get_db)
):


    user = (
        db.query(User)
        .filter(
            User.email == sub_data.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail=(
                "Пользователь не найден. "
                "Сначала зарегистрируйтесь через /marines."
            )
        )


    if sub_data.is_yearly:
        months = 12
    else:
        months = 1

    end_date = (
        datetime.utcnow()
        + timedelta(days=months * 30)
    )


    subscription_code = (
        generate_subscription_code(db)
    )


    new_subscription = Subscription(
        plan_name=sub_data.plan_name,

        is_yearly=sub_data.is_yearly,

        subscription_code=subscription_code,

        end_date=end_date,

        user_id=user.id,

        status="active"
    )

    db.add(new_subscription)

    db.commit()

    db.refresh(new_subscription)


    return SubscriptionResponse(
        success=True,

        message="Подписка оформлена успешно!",

        data={
            "userId": user.id,

            "subscriptionId": new_subscription.id,

            "plan": new_subscription.plan_name,

            "duration": (
                "1 год"
                if new_subscription.is_yearly
                else "1 месяц"
            ),

            "expiresAt": (
                new_subscription.end_date.isoformat()
            ),

            "status": new_subscription.status,

            "code": new_subscription.subscription_code
        }
    )


@router.get(
    "/subscription/{code}"
)
def get_subscription_by_code(
    code: str,
    db: Session = Depends(get_db)
):

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.subscription_code == code
        )
        .first()
    )

    if not subscription:

        raise HTTPException(
            status_code=404,
            detail="Подписка с таким кодом не найдена."
        )

    return {
        "success": True,

        "data": {

            "id": subscription.id,

            "code": subscription.subscription_code,

            "plan": subscription.plan_name,

            "isYearly": subscription.is_yearly,

            "startDate": (
                subscription.start_date.isoformat()
            ),

            "expiresAt": (
                subscription.end_date.isoformat()
            ),

            "status": subscription.status,

            "userId": subscription.user_id
        }
    }