import os
import openai
import pandas as pd
import csv
from typing import List, Dict

class AnkiCardGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
        
    def read_markdown_file(self, file_path: str) -> str:
        """Read content from markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
            
    def generate_questions(self, content: str, taxonomy_level: str, num_questions: int = 5) -> List[Dict]:
        """Generate questions and answers using OpenAI API."""
        prompt = f"""
        Based on the following content, generate {num_questions} questions and answers at the {taxonomy_level} level 
        of Bloom's taxonomy. Format your response as JSON with the following structure:
        [{{"question": "question text", "answer": "answer text"}}]
        
        Content:
        {content}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Extract and parse JSON response
            qa_pairs = eval(response.choices[0].message.content)
            return qa_pairs
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
            
    def create_anki_csv(self, qa_pairs: List[Dict], output_file: str):
        """Create Anki-compatible CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header (required by Anki)
            writer.writerow(["front", "back"])
            
            # Write question-answer pairs
            for qa in qa_pairs:
                writer.writerow([qa['question'], qa['answer']])

def main():
    # Configure API key (should be stored securely in practice)
    api_key = "your-api-key-here"
    
    # Initialize generator
    generator = AnkiCardGenerator(api_key)
    
    # Specify input and output files
    input_file = "input.md"
    output_file = "anki_cards.csv"
    
    # Read content
    content = generator.read_markdown_file(input_file)
    
    # Generate questions (example using "analysis" level)
    qa_pairs = generator.generate_questions(content, "analysis")
    
    # Create CSV file
    generator.create_anki_csv(qa_pairs, output_file)
    
    print(f"Generated {len(qa_pairs)} flashcards and saved to {output_file}")

if __name__ == "__main__":
    main()
