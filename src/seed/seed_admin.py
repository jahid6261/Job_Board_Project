from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import UserModel, UserRole
from src.utils.security import hash_password
from src.utils.settings import settings


async def create_admin(db: AsyncSession):
    try:
        result = await db.execute(
            select(UserModel).where(
                UserModel.email == settings.ADMIN_EMAIL
            )
        )

        existing_admin = result.scalar_one_or_none()

        # Admin already exists
        if existing_admin:

            # Same email but different role
            if existing_admin.role != UserRole.admin:
                raise ValueError(
                    "ADMIN_EMAIL belongs to a non-admin user."
                )

            # Activate admin if inactive
            if not existing_admin.is_active:
                existing_admin.is_active = True

                await db.commit()
                await db.refresh(existing_admin)

                print("Admin activated successfully!")
                return

            print("Admin already exists. Skipping creation...")
            return

        # Create new admin
        admin = UserModel(
            first_name="Super",
            last_name="Admin",
            email=settings.ADMIN_EMAIL,
            password=hash_password(settings.ADMIN_PASSWORD),
            number="0000000000",
            address="Admin",
            role=UserRole.admin,
            is_active=True,
        )

        db.add(admin)

        await db.commit()
        await db.refresh(admin)

        print("Super Admin created successfully!")

    except Exception as e:
        await db.rollback()

        print(f"Error during admin seeding: {e}")
        raise