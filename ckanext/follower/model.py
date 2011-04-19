"""
CKAN Follower Extension Data Model
"""
import sqlalchemy as sa
from ckan import model
from ckan.model import meta, User, Session
from ckan.model.types import make_uuid
from datetime import datetime

VALID_OBJECT_TYPES = ['package']

follower_table = meta.Table('follower', meta.metadata,
    meta.Column('id', meta.types.UnicodeText, primary_key=True, 
                default=make_uuid),
    meta.Column('user_id', meta.types.UnicodeText, 
                meta.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'),
                nullable=False),
    meta.Column('table', meta.types.UnicodeText, nullable=False),
    meta.Column('object_id', meta.types.UnicodeText, nullable=False),
    meta.Column('created', meta.DateTime, default=datetime.now),
    sa.UniqueConstraint('user_id', 'table', 'object_id')
    )

class Follower(object):
    def __init__(self, user_id, table, object_id):
        self.user_id = user_id
        self.table = table
        self.object_id = object_id
        self.created = None
    
    def __repr__(self):
        return "<Follower('%s', '%s', '%s')>" % (self.user_id, 
                                                 self.table, 
                                                 self.object_id)

meta.mapper(Follower, follower_table)


if __name__ == "__main__":
    # TODO: for testing only, remove
    engine = sa.create_engine('postgresql://ckantest:pass@localhost/ckantest')
    model.init_model(engine)

    follower_table.drop(checkfirst=True)
    follower_table.create(checkfirst=True)

    # follower_1 = Follower(u'1', u'expenses', u'1')
    # print follower_1
    # session = meta.Session()
    # session.add(follower_1)
    # session.commit()
    # print follower_1.id
