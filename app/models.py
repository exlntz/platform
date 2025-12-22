from sqlalchemy.orm import Mapped,mapped_column
from app.database import Model
from sqlalchemy import Text

class UserModel(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    username: Mapped[str] = mapped_column(unique=True,index=True)
    email: Mapped[str] = mapped_column(unique=True,index=True)
    hashed_password: Mapped[str]
    rating: Mapped[float] = mapped_column(default=1000.0)


class TaskModel(Model):
    __tablename__='tasks'
    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(index=True)
    theme: Mapped[str] = mapped_column(index=True)
    difficulty: Mapped[str] = mapped_column(index=True)
    correct_answer: Mapped[str]