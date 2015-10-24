from django.test import TestCase, Client
from django.core.urlresolvers import reverse

class TestMiddleware(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_middleware(self):
        response = self.client.get(reverse("main"))
        self.assertEqual(response.content.decode("utf-8"), "middleware_called")
            

       
 
