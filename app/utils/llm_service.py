import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.models.config import LLMConfig
from app.models.gitlab import Change, CodeComment

class LLMService:
    """Service for interacting with LLM APIs"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.model = config.model_name
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
    
    def generate_code_review(self, changes: List[Change], guidelines: Dict[str, str] = None) -> List[CodeComment]:
        """Generate code review comments for the given changes"""
        all_comments = []
        
        for change in changes:
            # Skip files that are too large or deleted
            if not change.diff or change.deleted_file:
                continue
                
            # Determine language-specific guidelines
            language_guidelines = self._detect_language_guidelines(change.new_path, guidelines)
            
            # Create the prompt for the LLM
            prompt = self._create_code_review_prompt(change, language_guidelines)
            
            # Get the LLM response
            response = self._get_llm_response(prompt)
            
            # Process the response into comments
            comments = self._process_review_response(response, change)
            all_comments.extend(comments)
            
        return all_comments
    
    def _detect_language_guidelines(self, file_path: str, guidelines: Dict[str, str] = None) -> str:
        """Detect which language guidelines to use based on file extension"""
        if not guidelines:
            return ""
            
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        
        # Map common extensions to languages
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp"
        }
        
        language = language_map.get(ext.lower(), "")
        
        # Return the guidelines for this language if available
        return guidelines.get(language, "")
    
    def _create_code_review_prompt(self, change: Change, language_guidelines: str) -> str:
        """Create a prompt for the LLM to review code"""
        prompt = f"""You are a senior tech lead reviewing a merge request. 
        Please review the following code changes and provide constructive feedback, focusing on:
        
        1. Code quality issues
        2. Potential bugs or edge cases
        3. Performance concerns
        4. Security vulnerabilities
        5. Maintainability and readability
        6. Best practices and design patterns
        
        For each issue, specify the exact line number and provide a clear explanation of the issue and how to fix it.
        Format your response as a JSON array where each object has:
        - 'line': The line number in the new file (or null for general comments)
        - 'path': The file path
        - 'note': Your comment explaining the issue and suggested improvement
        
        File: {change.new_path}
        
        Diff:
        ```
        {change.diff}
        ```
        """
        
        # Add language-specific guidelines if available
        if language_guidelines:
            prompt += f"\nLanguage-specific guidelines:\n{language_guidelines}\n"
            
        return prompt
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code review assistant that focuses on providing constructive feedback on code changes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return "[]"
    
    def _process_review_response(self, response: str, change: Change) -> List[CodeComment]:
        """Process the LLM response into structured comments"""
        comments = []
        
        try:
            # Try to parse the response as JSON
            data = self._extract_json(response)
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'note' in item:
                        comment = CodeComment(
                            note=item.get('note'),
                            path=item.get('path', change.new_path),
                            line=item.get('line'),
                            line_type="new"  # Assuming comments are for the new version
                        )
                        comments.append(comment)
        except Exception as e:
            # If we can't parse the response, create a general comment
            print(f"Error processing LLM response: {e}")
        
        # If no comments were created, add a general error comment
        if not comments and not response.strip() == "[]":
            comment = CodeComment(
                note=f"Code review assistant was unable to process this file properly. Please review manually.",
                path=change.new_path
            )
            comments.append(comment)
            
        return comments
    
    def _extract_json(self, text: str) -> Any:
        """Extract JSON from a text that might contain other content"""
        # Find JSON array in the text
        import re
        json_match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If that didn't work, try to find any JSON object
        json_match = re.search(r'{.*}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If all else fails, return the whole text
        return []