from datetime import datetime, timezone
from typing import AbstractSet

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Base class for all models in the application.
    
    This class provides a common interface for all models, including
    the ability to define a table name and a primary key.
    """
    
    # By default, we'll use Integer primary keys
    # Specific models can override this if needed
    id = Column(Integer, primary_key=True, index=True)
    __name__: str


    
@declared_attr
def __tablename__(cls) -> str:
    """
    Generate a table name based on the class name.
    
    Returns:
        str: The table name.
    """
    return cls.__name__.lower()


created_at: Column[DateTime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
updated_at: Column[DateTime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
