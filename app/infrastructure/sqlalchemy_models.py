from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
    BigInteger,
    DateTime,
    func,
    DECIMAL,
    Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.custom_enum import CurrencyEnum, OperationTypeEnum
from app.domain.rules import UserRules, WalletRules, WalletOperationRules
from app.infrastructure.sqlalchemy_db import Base


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(UserRules.user_name_max_length),
        nullable=False,
        unique=True,
        index=True
    )
    password: Mapped[str] = mapped_column(String(UserRules.password_max_length), nullable=False)
    wallets: Mapped[list["WalletORM"]] = relationship(back_populates="user", passive_deletes=True)


class WalletORM(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(WalletRules.name_max_length), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(WalletRules.balance_length, WalletRules.balance_length_after_point),
        nullable=False,
        default=WalletRules.balance_min
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        SQLEnum(CurrencyEnum, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False
    )
    user: Mapped[UserORM] = relationship(back_populates="wallets")
    operations: Mapped["OperationWalletORM"] = relationship(back_populates="wallet", passive_deletes=True)

    __table_args__ = (
        CheckConstraint(f"balance >= {WalletRules.balance_min}", name="wallet_balance"),
        UniqueConstraint("name", "user_id", name="unique_wallet_user_id"),
    )


class OperationWalletORM(Base):
    __tablename__ = "operation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id", ondelete="CASCADE"))
    type: Mapped[OperationTypeEnum] = mapped_column(
        SQLEnum(OperationTypeEnum, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(WalletOperationRules.amount_length, WalletOperationRules.amount_length_after_point),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        String(WalletOperationRules.description_max_length),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    wallet: Mapped[WalletORM] = relationship(back_populates="operations")

    __table_args__ = (
        CheckConstraint(f"amount >= {WalletOperationRules.amount_min}", name="operation_amount"),
    )
