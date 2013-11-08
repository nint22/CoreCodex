from corecodex.tests import *

class TestSubmitController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='submit', action='index'))
        # Test response...
