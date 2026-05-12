from sqlalchemy import String, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.sqlalchemy_db import Base


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    wallets: Mapped[list["WalletORM"]] = relationship(back_populates="user", passive_deletes=True)


class WalletORM(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped[UserORM] = relationship(back_populates="wallets")

    __table_args__ = (
        CheckConstraint(f"balance >= 0", name="wallet_balance"),
    )
