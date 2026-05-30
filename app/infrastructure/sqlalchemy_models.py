from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
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
from app.infrastructure.sqlalchemy_db import Base


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    wallets: Mapped[list["WalletORM"]] = relationship(back_populates="user", passive_deletes=True)


class WalletORM(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False, default=Decimal("0.00"))
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
        CheckConstraint(f"balance >= 0.00", name="wallet_balance"),
    )


class OperationWalletORM(Base):
    __tablename__ = "operation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id", ondelete="CASCADE"))
    type: Mapped[OperationTypeEnum] = mapped_column(
        SQLEnum(OperationTypeEnum, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    wallet: Mapped[WalletORM] = relationship(back_populates="operations")

    __table_args__ = (
        CheckConstraint(f"amount >= 0.00", name="operation_amount"),
    )
