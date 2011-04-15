"""
CKAN Follower Extension: Allow users to follow packages.

Follower is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = follower

This extension provides a new API: /api/follower
"""
from logging import getLogger
log = getLogger(__name__)

from genshi.input import HTML
from genshi.filters import Transformer
from pylons.decorators import jsonify
from pylons import request, tmpl_context as context
from ckan.lib.base import BaseController
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurable, IRoutes, IGenshiStreamFilter

from ckanext.follower import model
from ckanext.follower import html


class FollowerPlugin(SingletonPlugin):
    """
    Allow users to follow packages.
    Inserts javascript/html into package pages.
    """
    implements(IConfigurable)
    implements(IRoutes, inherit=True)
    implements(IGenshiStreamFilter)

    def configure(self, config):
        """
        Called upon CKAN setup, will pass current configuration dict to the
        plugin to read custom options.
        """
        # create the follower table if it doesn't already exist
        model.follower_table.create(checkfirst=True)

    def before_map(self, map):
        """
        """
        map.connect('follower', '/api/2/follower',
            controller='ckanext.follower.plugin:FollowerAPIController',
            action='index')
        # map.connect('dataapi_resource', '/api/data/{id}',
            # controller='ckanext.dataapi:DataAPIController',
            # action='resource')
        return map

    def filter(self, stream):
        """
        Required to implement IGenshiStreamFilter; will apply some HTML 
        transformations to the page currently rendered. 
        """
        routes = request.environ.get('pylons.routes_dict')

        # if this is the read action of a package, show follower info
        if(routes.get('controller') == 'package' and
           routes.get('action') == 'read' and 
           context.pkg.id):
            # url = url_for(controller='package', action='read', 
                          # id=c.pkg.name, qualified=True)
            # data = {'name': self.disqus_name, 
                    # 'url': url,
                    # 'identifier': 'pkg-' + c.pkg.id}
            stream = stream | Transformer('head').append(HTML(html.HEAD_CODE))
            stream = stream | Transformer('body//div[@id="package"]//h2[@class="head"]')\
                .append(HTML(html.FOLLOWER_CODE))
        return stream


class FollowerAPIController(BaseController):
    """
    """
    @jsonify
    def index(self):
        """
        """
        return {
            'doc': __doc__,
            'doc_url': 'http://ckan.org/wiki/Extensions'
            }
