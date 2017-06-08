from sqlalchemy import Column, Integer, String
from database import Base

class Sign(Base):
    __tablename__ = 'signs'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    particle_id = Column(String(255), unique=True)

    def __init__(self, name=None, particle_id=None):
        self.name = name
        self.particle_id = particle_id

    def __repr__(self):
        return '<Sign %r>' % (self.name)