import unittest
from unittest.mock import patch, MagicMock
from app.utils.llm_service import LLMService
from app.models.config import LLMConfig
from app.models.gitlab import Change

class TestLLMService(unittest.TestCase):
    def setUp(self):
        # Create a test configuration
        self.config = LLMConfig(
            api_key="test_api_key",
            model_name="gpt-4",
            max_tokens=2000,
            temperature=0.1
        )
        
        self.llm_service = LLMService(self.config)
    
    def test_detect_language_guidelines(self):
        # Test with Python file
        guidelines = {
            "python": "Use PEP8",
            "javascript": "Use ES6"
        }
        
        result = self.llm_service._detect_language_guidelines("app/main.py", guidelines)
        self.assertEqual(result, "Use PEP8")
        
        # Test with JavaScript file
        result = self.llm_service._detect_language_guidelines("src/component.js", guidelines)
        self.assertEqual(result, "Use ES6")
        
        # Test with unknown extension
        result = self.llm_service._detect_language_guidelines("README.md", guidelines)
        self.assertEqual(result, "")
        
        # Test with no guidelines
        result = self.llm_service._detect_language_guidelines("app/main.py", None)
        self.assertEqual(result, "")
    
    def test_create_code_review_prompt(self):
        # Create a test change
        change = Change(
            old_path="app/main.py",
            new_path="app/main.py",
            diff="@@ -1,1 +1,2 @@\n-old line\n+new line\n+another line"
        )
        
        # Test with no language guidelines
        prompt = self.llm_service._create_code_review_prompt(change, "")
        
        # Verify prompt contains the diff
        self.assertIn(change.diff, prompt)
        self.assertIn(change.new_path, prompt)
        
        # Test with language guidelines
        prompt = self.llm_service._create_code_review_prompt(change, "Use PEP8")
        
        # Verify prompt contains the guidelines
        self.assertIn("Use PEP8", prompt)
    
    @patch('openai.ChatCompletion.create')
    def test_get_llm_response(self, mock_create):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_create.return_value = mock_response
        
        # Call the method
        result = self.llm_service._get_llm_response("Test prompt")
        
        # Verify the result
        self.assertEqual(result, "Test response")
        
        # Verify OpenAI was called with the correct parameters
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs['model'], "gpt-4")
        self.assertEqual(kwargs['temperature'], 0.1)
        self.assertEqual(kwargs['max_tokens'], 2000)
        
        # Test handling of exceptions
        mock_create.side_effect = Exception("API error")
        result = self.llm_service._get_llm_response("Test prompt")
        self.assertEqual(result, "[]")
    
    def test_extract_json(self):
        # Test with valid JSON array
        text = "Some text before [\n  {\"key\": \"value\"}\n] and text after"
        result = self.llm_service._extract_json(text)
        self.assertEqual(result, [{"key": "value"}])
        
        # Test with valid JSON object
        text = "Some text before {\"key\": \"value\"} and text after"
        result = self.llm_service._extract_json(text)
        self.assertEqual(result, {"key": "value"})
        
        # Test with invalid JSON
        text = "No JSON here"
        result = self.llm_service._extract_json(text)
        self.assertEqual(result, [])
    
    def test_process_review_response(self):
        # Create a test change
        change = Change(
            old_path="app/main.py",
            new_path="app/main.py",
            diff="@@ -1,1 +1,2 @@\n-old line\n+new line\n+another line"
        )
        
        # Test with valid JSON response
        response = "[{\"line\": 10, \"path\": \"app/main.py\", \"note\": \"Test comment\"}]"
        comments = self.llm_service._process_review_response(response, change)
        
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].line, 10)
        self.assertEqual(comments[0].path, "app/main.py")
        self.assertEqual(comments[0].note, "Test comment")
        
        # Test with path defaulting to change.new_path
        response = "[{\"line\": 10, \"note\": \"Test comment\"}]"
        comments = self.llm_service._process_review_response(response, change)
        
        self.assertEqual(comments[0].path, "app/main.py")
        
        # Test with invalid JSON
        response = "Not JSON"
        comments = self.llm_service._process_review_response(response, change)
        
        self.assertEqual(len(comments), 1)
        self.assertIn("unable to process", comments[0].note)

if __name__ == '__main__':
    unittest.main()