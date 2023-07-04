from sqlalchemy import Column, BIGINT, Integer, String, Boolean, Date, Float, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    id = Column(BIGINT, primary_key=True)
    username = Column(String(30), default=None, nullable=True)
    is_admin = Column(Boolean, default=False)
    sub = Column(Date, default=None, nullable=True)
    req_num = Column(Integer, default=0)
    status = Column(Boolean, default=False)
    percent = Column(Float, CheckConstraint('percent IS NULL OR percent >= 0'), default=None, nullable=True)

    __tablename__ = 'users'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
