import unittest
from unittest.mock import patch, MagicMock
from app.utils.gitlab_client import GitLabClient
from app.models.config import GitLabConfig
from app.models.gitlab import CodeComment

class TestGitLabClient(unittest.TestCase):
    def setUp(self):
        # Create a test configuration
        self.config = GitLabConfig(
            api_url="https://gitlab.example.com/api/v4",
            access_token="test_token",
            webhook_secret="test_secret"
        )
        
        self.client = GitLabClient(self.config)
    
    def test_init(self):
        # Test initialization sets the correct properties
        self.assertEqual(self.client.api_url, "https://gitlab.example.com/api/v4")
        self.assertEqual(self.client.headers['PRIVATE-TOKEN'], "test_token")
    
    def test_validate_webhook_signature(self):
        # Test valid signature
        self.assertTrue(self.client.validate_webhook_signature("test_secret", "test_secret"))
        
        # Test invalid signature
        self.assertFalse(self.client.validate_webhook_signature("test_secret", "wrong_secret"))
        
        # Test when no webhook secret is configured
        client_no_secret = GitLabClient(GitLabConfig(
            api_url="https://gitlab.example.com/api/v4",
            access_token="test_token"
        ))
        self.assertTrue(client_no_secret.validate_webhook_signature("any_secret", "any_token"))
    
    @patch('requests.get')
    def test_get_merge_request(self, mock_get):
        # Mock response for successful request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 123,
            'iid': 456,
            'project_id': 789,
            'title': 'Test MR',
            'description': 'Test description',
            'state': 'opened',
            'created_at': '2023-01-01T12:00:00Z',
            'updated_at': '2023-01-02T12:00:00Z',
            'source_branch': 'feature-branch',
            'target_branch': 'main',
            'author': {
                'id': 1,
                'name': 'Test User',
                'username': 'testuser',
                'avatar_url': 'https://example.com/avatar.png'
            },
            'web_url': 'https://gitlab.example.com/project/merge_requests/456'
        }
        mock_get.return_value = mock_response
        
        # Call the method
        mr = self.client.get_merge_request(789, 456)
        
        # Verify the result
        self.assertIsNotNone(mr)
        self.assertEqual(mr.id, 123)
        self.assertEqual(mr.iid, 456)
        self.assertEqual(mr.title, 'Test MR')
        self.assertEqual(mr.author.name, 'Test User')
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://gitlab.example.com/api/v4/projects/789/merge_requests/456",
            headers=self.client.headers
        )
        
        # Test handling of failed request
        mock_response.status_code = 404
        mr = self.client.get_merge_request(789, 456)
        self.assertIsNone(mr)
    
    @patch('requests.post')
    def test_add_comment(self, mock_post):
        # Mock response for successful request
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Create a test comment
        comment = CodeComment(
            note="Test comment",
            path="app/main.py",
            line=10,
            line_type="new"
        )
        
        # Call the method
        result = self.client.add_comment(789, 456, comment)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['url'], "https://gitlab.example.com/api/v4/projects/789/merge_requests/456/notes")
        self.assertEqual(kwargs['headers'], self.client.headers)
        
        # Payload should include position data
        payload = kwargs['json']
        self.assertEqual(payload['body'], "Test comment")
        self.assertIn('position', payload)
        self.assertEqual(payload['position']['new_line'], 10)
        
        # Test general comment (no line)
        mock_post.reset_mock()
        general_comment = CodeComment(
            note="General comment",
            path="app/main.py"
        )
        
        self.client.add_comment(789, 456, general_comment)
        
        # Verify payload doesn't include position data
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['body'], "General comment")
        self.assertNotIn('position', payload)
        
        # Test failed request
        mock_response.status_code = 400
        result = self.client.add_comment(789, 456, comment)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()