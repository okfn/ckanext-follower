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
from ckan.model import User
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurable, IRoutes, IGenshiStreamFilter

from ckanext.follower import model
from ckanext.follower import html

def _get_user_id():
    """
    """
    user_name = request.environ.get('REMOTE_USER')
    query = User.search(user_name)
    users = query.all()
    if users:
        return str(users[0].id)
    else:
        return ""

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
            # pass data to the javascript file that creates the
            # follower count and follow/unfollow buttons
            #
            # the location variable specifies the ID of the
            # HTML tag that the buttons will be appended to
            data = {'package_id': context.pkg.id,
                    'user_id': _get_user_id(),
                    'location': '#follower'}
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
    VALID_OBJECT_TYPES = ['package']

    @jsonify
    def index(self, user_id=None):
        """
        """
        # get the user ID from the request
        if not 'user_id' in request.POST:
            response.status_int = 400
            return {'error': "No user ID specified"}
        user_id = request.POST['user_id']

        # make sure this matches the user_id of the current user
        if not user_id == _get_user_id():
            response.status_int = 403
            return {'error': "You are not authorized to make this request"}

        # check for an object type 
        # this specifies the type of object to follow, currently accepts
        # only 'package'
        if not 'object_type' in request.POST:
            response.status_int = 400
            return {'error': "No object type specified"}
        object_type = request.POST['object_type']

        # make sure that the object_type is valid
        if not object_type in self.VALID_OBJECT_TYPES:
            response.status_int = 400
            return {'error': "Invalid object type"}

        # check for a package ID
        if not 'package_id' in request.POST:
            response.status_int = 400
            return {'error': "No package ID specified"}
        package_id = request.POST['package_id']

        return {'status': package_id}
        # return {'status': "Success"}

    @jsonify
    def package(self, id):
        """
        """
        users = []
        users.append({'username': 'testuser'})
        return users
