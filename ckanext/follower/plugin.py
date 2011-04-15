"""
CKAN Follower Extension: Allow users to follow packages.

Follower is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = follower

This extension provides a new API: /api/follower
"""
import os
from logging import getLogger
log = getLogger(__name__)

from genshi.input import HTML
from genshi.filters import Transformer
from pylons.decorators import jsonify
from pylons import request, tmpl_context as context
from ckan.lib.base import BaseController, response
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
        Called upon CKAN setup.
        """
        # create the follower table if it doesn't already exist
        model.follower_table.create(checkfirst=True)
        
        # add our public folder to the CKAN's list of public folders
        here = os.path.dirname(__file__)
        public_dir = os.path.join(here, 'public')
        if config.get('extra_public_paths'):
            config['extra_public_paths'] += ',' + public_dir
        else:
            config['extra_public_paths'] = public_dir

    def before_map(self, map):
        """
        """
        map.connect('follower', '/api/2/follower',
            controller='ckanext.follower.plugin:FollowerAPIController',
            action='index')
        map.connect('follower_package', '/api/2/follower/package/{id}',
            controller='ckanext.follower.plugin:FollowerAPIController',
            action='package')
        return map

    def filter(self, stream):
        """
        Required to implement IGenshiStreamFilter.
        """
        routes = request.environ.get('pylons.routes_dict')

        # if this is the read action of a package, show follower info
        if(routes.get('controller') == 'package' and
           routes.get('action') == 'read' and 
           context.pkg.id):
            # the id of the current package will be passed
            # to the javascript file that creates the follower count
            # and buttons
            data = {'package_id': context.pkg.id,
                    'follower_node': '#follower'}
            # add CSS styles for follower HTML
            stream = stream | Transformer('head').append(HTML(html.HEAD_CODE))
            # add jquery and follower.js links
            stream = stream | Transformer('body')\
                .append(HTML(html.BODY_CODE % data))
            # add the follower DIV to the package title, after the
            # RSS 'subscribe' link
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

    @jsonify
    def package(self, id):
        """
        """
        users = []
        users.append({'username': 'testuser'})
        return users
