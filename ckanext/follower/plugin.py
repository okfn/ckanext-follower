"""
CKAN Follower Extension: Allow users to follow packages.

Follower is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = follower
"""
from genshi.core import TEXT
from genshi.input import HTML
from genshi.filters import Transformer

from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurable, IGenshiStreamFilter
from ckan.lib.helpers import url_for 

from logging import getLogger
log = getLogger(__name__)

class FollowerPlugin(SingletonPlugin):
    """
    Allow users to follow packages.
    Inserts javascript/html into package pages.
    """
    implements(IConfigurable)
    implements(IGenshiStreamFilter)

    def configure(self, config):
        """
        Called upon CKAN setup, will pass current configuration dict to the
        plugin to read custom options.
        """
        from ckan.model.meta import (metadata, Table, Column, types, DateTime)
        from ckan.model.types import make_uuid
        from datetime import datetime

        follower_table = Table('follower', metadata,
                Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                Column('user_id', types.UnicodeText),
                Column('table', types.UnicodeText),
                Column('object_id', types.UnicodeText),
                Column('created', DateTime, default=datetime.now),
                )
        # follower_table.create(checkfirst=True)
        follower_table.drop(checkfirst=True)

        # for t in metadata.sorted_tables:
            # log.info(t.name)

    def filter(self, stream):
        """
        Required to implement IGenshiStreamFilter; will apply some HTML 
        transformations to the page currently rendered. 
        """
        from pylons import request
        routes = request.environ.get('pylons.routes_dict')
        
        # if routes.get('controller') == 'package' and \
        #     routes.get('action') == 'comments' and c.pkg.id:
        #     url = url_for(controller='package', action='read', 
        #                   id=c.pkg.name, qualified=True)
        #     data = {'name': self.disqus_name, 
        #             'url': url,
        #             'identifier': 'pkg-' + c.pkg.id}
        #     stream = stream | Transformer('body')\
        #         .append(HTML(html.BOTTOM_CODE % data))
        #     stream = stream | Transformer('body//div[@id="comments"]')\
        #         .append(HTML(html.COMMENT_CODE % data))
        
        # if routes.get('controller') == 'home' and \
        #     routes.get('action') == 'index':
        #     data = {'name': self.disqus_name}
        #     stream = stream | Transformer('body//\
        #         div[@id="main"]//ul[@class="xoxo"]')\
        #         .append(HTML(html.LATEST_CODE % data))
        
        return stream
