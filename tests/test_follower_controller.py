import json
from paste.deploy import appconfig
import paste.fixture
from ckan.config.middleware import make_app
from ckan.tests import conf_dir, url_for, CreateTestData, TestController

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
