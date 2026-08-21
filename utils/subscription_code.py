import secrets
import string

from sqlalchemy.orm import Session

from models import Subscription


def generate_subscription_code(db: Session) -> str:
    """
    Генерирует уникальный код подписки.

    Пример:

    WH40K-A7K2-91PQ-X8M4
    """

    alphabet = string.ascii_uppercase + string.digits

    while True:

        part1 = "".join(
            secrets.choice(alphabet)
            for _ in range(4)
        )

        part2 = "".join(
            secrets.choice(alphabet)
            for _ in range(4)
        )

        part3 = "".join(
            secrets.choice(alphabet)
            for _ in range(4)
        )

        code = f"WH40K-{part1}-{part2}-{part3}"

        existing_code = (
            db.query(Subscription)
            .filter(
                Subscription.subscription_code == code
            )
            .first()
        )

        if not existing_code:
            return code