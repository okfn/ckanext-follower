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

def _get_user_id():
    """
    Returns the user ID of the user that is currently
    logged in (user name set in REMOTE_USER environment var).
    """
    try:
        user_name = request.environ.get('REMOTE_USER')
        query = model.User.search(user_name)
        user = query.first()
        return str(user.id)

    except Exception as e:
        log.info("Error: " + str(e))
        return ""

def _get_user_full_name(id):
    """
    Returns the full name of the user with a given ID.
    """
    query = model.Session.query(model.User).filter(model.User.id == id)
    user = query.first()
    if user:
        return str(user.fullname)
    else:
        return "Unknown"


class FollowerPlugin(SingletonPlugin):
    """
    Allow users to follow packages.

    Inserts javascript/html into package pages and exposes the
    follower API.
    """
    implements(IConfigurable)
    implements(IRoutes, inherit=True)
    implements(IGenshiStreamFilter)

    def configure(self, config):
        """
        Called upon CKAN setup.

        Create follower table in the database and add the
        public folder to CKAN's list of public folders.
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
        Expose the follower API.

        Creates two endpoints:
        * /api/2/follower: allow users to follow/unfollow packages
        * /api/2/package/{id}: get a list of users following a given
          package
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

        Only applies to package controllers with the read action.
        Adds HTML to the document HEAD, the package heading and
        the bottom of the body to create the follow/unfollow button
        and the follower count button.
        """
        routes = request.environ.get('pylons.routes_dict')
        # if this is the read action of a package, show follower info
        if(routes.get('controller') == 'package' and
           routes.get('action') == 'read' and 
           context.pkg.id):
            # pass data to the javascript file that creates the
            # follower count and follow/unfollow buttons
            data = {'package_id': context.pkg.id,
                    'user_id': _get_user_id()}
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
    The CKANEXT-Follower API

    Creates two endpoints:
    * index: allow users to follow/unfollow packages
    * package/{id}: get a list of users following a given package
    """
    def _follow_package(self, user_id, table, package_id):
        """
        Update the database, setting user_id to follow
        package_id.
        """
        session = model.meta.Session()

        try:
            follower = model.Follower(unicode(user_id),
                                      unicode(table),
                                      unicode(package_id))
            session.add(follower)
            session.commit()
            return True

        except Exception as e:
            log.info("Error: " + str(e))
            session.rollback()
            return False

    @jsonify
    def index(self):
        """
        follow API endpoint.

        POST actions request that a user is marked as following a given package.
        Format: {user_id, object_type, object_id}
        """
        # if POST request, should be trying to add a follower
        if request.POST:
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
            if not object_type in model.VALID_OBJECT_TYPES:
                response.status_int = 400
                return {'error': "Invalid object type"}

            # check for a package ID
            if not 'package_id' in request.POST:
                response.status_int = 400
                return {'error': "No package ID specified"}
            package_id = request.POST['package_id']

            # update the database
            if self._follow_package(user_id, object_type, package_id):
                return {'status': "Success"}
            else:
                response.status_int = 500
                return {'error': "Could not update database"}
        
        # if not, just return a default message
        else:
            return {'doc': __doc__,
                    'doc_url': 'http://ckan.org/wiki/Extensions'}

    @jsonify
    def package(self, id):
        """
        package API endpoint.

        Returns a list of {id, name} pairs for each user that
        follow this package.
        """
        try:
            query = model.Session.query(model.Follower)\
                .filter(model.Follower.table == 'package')\
                .filter(model.Follower.object_id == id)

            users = []
            for follower in query:
                users.append({'id': follower.user_id,
                              'name': _get_user_full_name(follower.user_id)})
            return users

        except Exception as e:
            log.info("Error: " + str(e))
            response.status_int = 500
            return {'error': "Could not get package followers"}
