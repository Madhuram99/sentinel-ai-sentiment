
# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch

class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('chat_api')

    # We mock the 'llm.invoke' call so we don't actually hit the Groq API during tests
    @patch('chatapp.views.llm.invoke')
    def test_sentiment_and_response_flow(self, mock_llm):
        # 1. Setup the Mock AI response
        mock_response_content = json.dumps({
            "response": "I understand your frustration.",
            "suggestions": ["Tell me more", "I want a refund"]
        })
        # The mock needs to return an object that has a .content attribute
        mock_llm.return_value.content = mock_response_content

        # 2. Simulate User Input (Negative Sentiment)
        data = {"message": "I am extremely angry with this service!"}
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")

        # 3. Verify the Response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Check VADER Analysis
        self.assertEqual(response_data['sentiment'], 'Negative')
        self.assertTrue(response_data['score'] < -0.05)

        # Check AI Logic
        self.assertEqual(response_data['bot_response'], "I understand your frustration.")
        self.assertEqual(len(response_data['suggestions']), 2)

    def test_empty_message(self):
        """Test how the API handles empty input"""
        response = self.client.post(self.url, json.dumps({"message": ""}), content_type="application/json")
        # Depending on your view logic, this might still start a session or return 200 with neutral
        self.assertEqual(response.status_code, 200)