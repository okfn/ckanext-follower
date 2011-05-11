import json
from paste.deploy import appconfig
import paste.fixture
from ckan.config.middleware import make_app
from ckan.tests import conf_dir, url_for, CreateTestData, TestController
from ckanext.follower.controller import get_user_id

class TestFollowerController(TestController):
    @classmethod
    def setup_class(cls):
        config = appconfig('config:test.ini', relative_to=conf_dir)
        config.local_conf['ckan.plugins'] = 'follower'
        wsgiapp = make_app(config.global_conf, **config.local_conf)
        cls.app = paste.fixture.TestApp(wsgiapp)
        CreateTestData.create()

    @classmethod
    def teardown_class(self):
        CreateTestData.delete()

    def test_index(self):
        """
        Tests that the index action for follower returns application/json
        as the content type, returns a correctly formatted JSON response,
        and the the JSON response consists of two objects with the keys
        'doc' and 'doc_url'.
        """
        response = self.app.get(url_for('follower'))
        # make sure that the response content type is JSON
        assert response.header('Content-Type') == "application/json" ,\
            "controller not returning a JSON object"
        # parse the JSON response and check the values
        json_response = json.loads(response.body)
        assert len(json_response) == 2, "response does not contain 2 keys"
        assert 'doc' in json_response, \
            "response does not contain a 'doc' key"
        assert 'doc_url' in json_response, \
            "response does not contain a 'doc_url' key"

    def test_follow_get(self):
        """
        Tests to ensure that get requests to the follow action returns
        the same content as index action.
        """
        f = self.app.get(url_for('follow'))
        i = self.app.get(url_for('follower'))
        # compare content-type headers
        assert f.header('Content-Type') == i.header('Content-Type')
        f_js = json.loads(f.body)
        i_js = json.loads(i.body)
        # make sure json responses are same length
        assert len(f_js) == len(i_js)
        # make sure json response key/values are equal
        for key in f_js:
            assert key in i_js
            assert f_js[key] == i_js[key]

    def test_follow_post_invalid_request(self):
        """
        Tests to ensure that invalid post requests to the follow action
        return the appropriate error code.
        Invalid requests:
        - not containing a field called 'action', which is set to 'follow' 
        (results in error 404)
        - no user_id supplied (results in error 400)
        - given user_id matches that of the currently logged in user
        - no package_id supplied (results in error 400)
        - package_id not found in database (results in error 404)
        """
        # no action
        self.app.post(url_for('follow'), status = 404)
        # no user_id
        self.app.post(url_for('follow'), 
                      params = {'action': 'follow'}, 
                      status = 400)
        # not logged in:
        self.app.post(url_for('follow'), 
                      params = {'action': 'follow', 'user_id': 'invalid_user'}, 
                      status = 403)
        # logged in but giving a different user_id:
        environ = {'REMOTE_USER': 'tester'}
        user_id = get_user_id('invalid_user')
        self.app.post(url_for('follow'), 
                      extra_environ = environ,
                      params = {'action': 'follow', 'user_id': user_id}, 
                      status = 403)
        environ = {'REMOTE_USER': 'invalid_user'}
        user_id = get_user_id('tester')
        self.app.post(url_for('follow'), 
                      extra_environ = environ,
                      params = {'action': 'follow', 'user_id': user_id}, 
                      status = 403)
        # valid user_id, no package_id
        environ = {'REMOTE_USER': 'tester'}
        self.app.post(url_for('follow'), 
                      extra_environ = environ,
                      params = {'action': 'follow', 'user_id': user_id}, 
                      status = 400)
        # package_id not found
        self.app.post(url_for('follow'), 
                      extra_environ = environ,
                      params = {'action': 'follow', 
                                'user_id': user_id,
                                'package_id': 'invalid_package_id'}, 
                      status = 404)
