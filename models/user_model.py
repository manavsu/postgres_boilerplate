from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
import logging

from models import DB_Base

log = logging.getLogger(__name__)

class User(DB_Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), nullable=False)
    username = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    
    def __repr__(self):
        return f'<User id:{self.id} email:{self.email}>'
    