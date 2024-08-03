from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    String,
    Float,
    DateTime,
    Enum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.core import Base, engine
import enum


class Role(str, enum.Enum):
    User = "User"
    Admin = "Admin"


class BaseMessage:
    content: Mapped[str] = mapped_column(String(100))
    date_created: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class BaseReport:
    phone_number: Mapped[str] = mapped_column(String(20))
    date_created: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    success: Mapped[bool] = mapped_column(Boolean)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    role: Mapped[enum.Enum] = mapped_column(Enum(Role), default=Role.User.value)

    psy_messages: Mapped[list["PsyMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    clinic_messages: Mapped[list["ClinicMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PsyMessage(Base, BaseMessage):
    __tablename__ = "psy_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="psy_messages")

    reports: Mapped[list["PsyReport"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )


class PsyReport(Base, BaseReport):
    __tablename__ = "psy_message_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=True)

    message: Mapped["PsyMessage"] = relationship(
        back_populates="reports", lazy="selectin"
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey("psy_messages.id", ondelete="CASCADE")
    )

    @property
    async def message_content(self):
        return self.message.content


class ClinicMessage(Base, BaseMessage):
    __tablename__ = "clinic_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(1000))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="clinic_messages")

    reports: Mapped[list["ClinicReport"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )


class ClinicReport(Base, BaseReport):
    __tablename__ = "clinic_message_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal: Mapped[str] = mapped_column(String(100))

    message: Mapped["ClinicMessage"] = relationship(
        back_populates="reports", lazy="selectin"
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey("clinic_messages.id", ondelete="CASCADE")
    )

    @property
    async def message_content(self):
        return self.message.content


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
