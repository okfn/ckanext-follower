"""
CKAN Follower Extension Data Model
"""
import sqlalchemy as sa
from ckan import model
from ckan.model import meta, User, Package, Session
from ckan.model.types import make_uuid
from datetime import datetime

follower_table = meta.Table('follower', meta.metadata,
    meta.Column('id', meta.types.UnicodeText, primary_key=True, 
                default=make_uuid),
    meta.Column('user_id', meta.types.UnicodeText, 
                meta.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'),
                nullable=False),
    meta.Column('package_id', meta.types.UnicodeText, 
                meta.ForeignKey('package.id', onupdate='CASCADE', ondelete='CASCADE'),
                nullable=False),
    meta.Column('created', meta.DateTime, default=datetime.now),
    sa.UniqueConstraint('user_id', 'package_id'))

class Follower(object):
    def __init__(self, user_id, package_id):
        self.user_id = user_id
        self.package_id = package_id
        self.created = None
    
    def __repr__(self):
        return "<Follower('%s', '%s')>" % (self.user_id, self.package_id)

meta.mapper(Follower, follower_table)
