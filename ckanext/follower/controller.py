"""
CKAN Follower Extension: Allow users to follow packages.

Follower is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = follower

This extension provides a new API: /api/follower
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons.decorators import jsonify
from pylons import request, tmpl_context as c
from ckan.lib.base import BaseController, response, render, abort
from ckanext.follower import model

def packages_followed_by(id):
    """
    Return a list of packages followed by user id.
    """
    query = model.Session.query(model.Follower)\
        .filter(model.Follower.table == 'package')\
        .filter(model.Follower.user_id == id)

    packages = []
    for package in query:
        packages.append(package.object_id)
    return packages

class FollowerController(BaseController):
    """
    The CKANEXT-Follower Controller.
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

    def _unfollow_package(self, user_id, table, package_id):
        """
        Update the database, removing user_id from package_id followers
        """
        session = model.meta.Session()

        try:
            query = model.Session.query(model.Follower)\
                .filter(model.Follower.user_id == user_id)\
                .filter(model.Follower.table == table)\
                .filter(model.Follower.object_id == package_id)

            follower = query.first()
            session.delete(follower)
            session.commit()
            return True

        except Exception as e:
            log.info("Error: " + str(e))
            session.rollback()
            return False

    def _validate_request(self):
        """
        Validates the current follow/unfollow request.

        Performs the following checks:
        * user_id field is present in request
        * user_id matches id of currently logged in user
        * object_type field is present in request
        * object_type is valid
        * package_id field is present in request

        returns: (http_status, json_response)
        """
        # get the user ID from the request
        if not request.params.get('user_id'):
            return (400, {'error': "No user ID specified"})
        user_id = request.params.get('user_id')

        # make sure this matches the user_id of the current user
        user_name = request.environ.get('REMOTE_USER')
        if not user_id == user_name:
            return (403, {'error': "You are not authorized to make this request"})

        # check for an object type - specifies the type of object to follow
        if not request.params.get('object_type'):
            return (400, {'error': "No object type specified"})
        object_type = request.params.get('object_type')
        
        # make sure that the object_type is valid
        if not object_type in model.VALID_OBJECT_TYPES:
            return (400, {'error': "Invalid object type"})

        # check for a package ID
        if not request.params.get('package_id'):
            return (400, {'error': "No package ID specified"})

        # valid request
        return (200, {'status': "OK" })

    def _get_followers(self, package_id):
        """
        Returns a list of {id: <user_id>} dicts for each user that
        follows this package.
        """
        query = model.Session.query(model.Follower)\
            .filter(model.Follower.table == 'package')\
            .filter(model.Follower.object_id == package_id)

        users = []
        for follower in query:
            users.append({'id': follower.user_id})
        return users

    @jsonify
    def index(self):
        """
        default follower API endpoint.
        """
        # just return a default message
        return {'doc': __doc__,
                'doc_url': 'http://ckan.org/wiki/Extensions'}

    @jsonify
    def follow(self):
        """
        follower API endpoint: Follow a given package.
        Format: {user_id, object_type, object_id, action}
        """
        status, result = self._validate_request()
        if status != 200:
            response.status_int = status
            return result

        # update the database
        user_id = request.params.get('user_id')
        object_type = request.params.get('object_type')
        package_id = request.params.get('package_id')
        if self._follow_package(user_id, object_type, package_id):
            return result
        else:
            response.status_int = 500
            return {'error': "Could not update database"}

    @jsonify
    def unfollow(self):
        """
        follower API endpoint: Unfollow a given package.
        Format: {user_id, object_type, object_id, action}
        """
        status, result = self._validate_request()
        if status != 200:
            response.status_int = status
            return result

        # update the database
        user_id = request.params.get('user_id')
        object_type = request.params.get('object_type')
        package_id = request.params.get('package_id')
        if self._unfollow_package(user_id, object_type, package_id):
            return result
        else:
            response.status_int = 500
            return {'error': "Could not update database"}

    @jsonify
    def package(self, id):
        """
        package API endpoint.

        Returns a list of {id: <user_id>} objects for each user that
        follows this package.
        """
        return self._get_followers(id)

    def package_followers_page(self, id):
        """
        Display a page containing all of the users that are following
        a given package.
        """
        c.pkg = model.Package.get(id)
        if not c.pkg:
            abort(404, _('Package not found'))

        c.followers = self._get_followers(id)
        return render("package_followers.html")
