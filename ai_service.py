import os
import anthropic
from typing import List, Dict, Optional

class AIWritingAssistant:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
    
    def get_suggestions(self, title: str, current_text: str, document_context: str = "") -> List[Dict]:
        """
        Generate AI writing suggestions based on title, current text, and optional document context
        
        Args:
            title: The writing title/topic
            current_text: Current text being written
            document_context: Optional context from uploaded documents
            
        Returns:
            List of suggestion dictionaries
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(title, current_text, document_context)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response into suggestions
            suggestions = self._parse_suggestions(response.content[0].text)
            return suggestions
            
        except Exception as e:
            print(f"Error getting AI suggestions: {str(e)}")
            return [
                {
                    "type": "error",
                    "text": "Unable to generate suggestions at the moment. Please try again."
                }
            ]
    
    def _build_prompt(self, title: str, current_text: str, document_context: str = "") -> str:
        """Build the prompt for Claude API"""
        
        prompt = f"""You are a helpful writing assistant. Help the user continue their writing.

Title/Topic: "{title}"

"""
        
        if document_context:
            # Use much more context - up to 8000 characters instead of 1000
            context_limit = 8000
            if len(document_context) > context_limit:
                truncated_context = document_context[:context_limit] + "..."
            else:
                truncated_context = document_context
            prompt += f"Reference Context (from uploaded documents):\n{truncated_context}\n\n"
        
        prompt += f"""Current Text:
{current_text}

Please provide 3 helpful writing suggestions. Each suggestion should be one of these types:
1. CONTINUATION - How to continue writing the next sentence/paragraph
2. IMPROVEMENT - How to improve existing text
3. STRUCTURE - Suggestions about organization or flow

Format your response as:
1. [TYPE]: Suggestion text here
2. [TYPE]: Suggestion text here  
3. [TYPE]: Suggestion text here

Keep suggestions concise and actionable."""

        return prompt
    
    def _parse_suggestions(self, response_text: str) -> List[Dict]:
        """Parse Claude's response into structured suggestions"""
        suggestions = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                # Extract type and text
                if '[CONTINUATION]' in line:
                    suggestion_type = 'continuation'
                    text = line.split('[CONTINUATION]:')[1].strip()
                elif '[IMPROVEMENT]' in line:
                    suggestion_type = 'improvement'
                    text = line.split('[IMPROVEMENT]:')[1].strip()
                elif '[STRUCTURE]' in line:
                    suggestion_type = 'structure'
                    text = line.split('[STRUCTURE]:')[1].strip()
                else:
                    # Fallback - extract text after number
                    suggestion_type = 'general'
                    text = line.split('.', 1)[1].strip() if '.' in line else line
                
                suggestions.append({
                    'type': suggestion_type,
                    'text': text
                })
        
        # Ensure we always return at least one suggestion
        if not suggestions:
            suggestions.append({
                'type': 'general',
                'text': 'Continue writing by expanding on your current ideas.'
            })
        
        return suggestions[:3]  # Limit to 3 suggestions

# Global instance
ai_assistant = AIWritingAssistant()