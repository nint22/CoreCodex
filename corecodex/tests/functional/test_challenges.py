from corecodex.tests import *

class TestChallengesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='challenges', action='index'))
        # Test response...
