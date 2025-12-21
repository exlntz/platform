from sqlalchemy.orm import Mapped,mapped_column
from app.database import Model

class UserModel(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    username: Mapped[str] = mapped_column(unique=True,index=True)
    email: Mapped[str] = mapped_column(unique=True,index=True)
    hashed_password: Mapped[str]
    rating: Mapped[float] = mapped_column(default=1000.0)
