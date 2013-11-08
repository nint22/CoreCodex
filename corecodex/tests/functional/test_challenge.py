from corecodex.tests import *

class TestChallengeController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='challenge', action='index'))
        # Test response...
