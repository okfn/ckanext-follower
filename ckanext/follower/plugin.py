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
from pylons import request, tmpl_context as c
from webob import Request
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurable, IRoutes, IGenshiStreamFilter

from ckanext.follower import model
from ckanext.follower import controller
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

def _is_follow_request(environ, result):
    """
    Used to determine if a POST request to /follower
    is a request to follow or unfollow a package.

    Returns true if the 'action' request parameter
    is set to 'follow'
    """
    r = Request(environ)
    if r.params.get("action") == "follow":
        return True
    else:
        return False

def _is_unfollow_request(environ, result):
    """
    Used to determine if a POST request to /follower
    is a request to follow or unfollow a package.

    Returns true if the 'action' request parameter
    is set to 'unfollow'
    """
    r = Request(environ)
    if r.params.get("action") == "unfollow":
        return True
    else:
        return False


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
        
        # add follower public folder to the CKAN's list of public folders
        here = os.path.dirname(__file__)
        public_dir = os.path.join(here, 'public')
        if config.get('extra_public_paths'):
            config['extra_public_paths'] += ',' + public_dir
        else:
            config['extra_public_paths'] = public_dir

        # add follower template folder to the CKAN's list of template folders
        template_dir = os.path.join(here, 'templates')
        if config.get('extra_template_paths'):
            config['extra_template_paths'] += ',' + template_dir
        else:
            config['extra_template_paths'] = template_dir

    def before_map(self, map):
        """
        Expose the follower API.

        Creates two endpoints:
        * /api/2/follower: allow users to follow/unfollow packages
        * /api/2/package/{id}: get a list of users following a given
          package
        """
        map.connect('follow', '/api/2/follower',
            controller='ckanext.follower.controller:FollowerController',
            action='follow', 
            conditions=dict(method=['POST'], function=_is_follow_request))
        map.connect('unfollow', '/api/2/follower',
            controller='ckanext.follower.controller:FollowerController',
            action='unfollow', 
            conditions=dict(method=['POST'], function=_is_unfollow_request))
        map.connect('follower', '/api/2/follower',
            controller='ckanext.follower.controller:FollowerController',
            action='index', conditions=dict(method=['GET']))
        map.connect('package_followers', '/api/2/follower/package/{id}',
            controller='ckanext.follower.controller:FollowerController',
            action='package')
        map.connect('package_followers_page', '/package/followers/{id}',
            controller='ckanext.follower.controller:FollowerController',
            action='package_followers_page')
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
           c.pkg.id):
            # pass data to the javascript file that creates the
            # follower count and follow/unfollow buttons
            data = {'package_id': c.pkg.id,
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
