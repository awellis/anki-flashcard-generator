from pydantic import BaseModel, Field
from typing import List, Optional
import csv
import os
from openai import OpenAI
from pathlib import Path

class AnkiFlashcard(BaseModel):
    """Model representing a single Anki flashcard with question, answer, and tags."""
    question: str = Field(..., description="The front side of the flashcard containing the question")
    answer: str = Field(..., description="The back side of the flashcard containing the answer")
    tags: List[str] = Field(..., description="List of tags associated with the flashcard")

class AnkiDeck(BaseModel):
    """Model representing a complete Anki deck containing multiple flashcards."""
    cards: List[AnkiFlashcard] = Field(..., description="List of flashcards in the deck")
    deck_name: str = Field(..., description="Name of the Anki deck")

class FlashcardGenerator:
    def __init__(self, client: OpenAI):
        self.client = client

    def generate_deck(self, text: str, deck_name: str, num_cards: int = 5) -> Optional[AnkiDeck]:
        """Generate structured flashcards using GPT-4 with enforced Pydantic model output."""
        if num_cards < 1:
            raise ValueError("Number of cards must be at least 1")
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert at creating Anki flashcards. Your task is to:
1. Read the provided text
2. Create {num_cards} Anki flashcards that cover the main concepts
3. Add relevant tags to each flashcard
4. Structure the output as an Anki deck with the name "{deck_name}"."""
                    },
                    {
                        "role": "user",
                        "content": f"Please create Anki flashcards for the following text: {text}"
                    }
                ],
                response_format=AnkiDeck,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return None

class DeckWriter:
    @staticmethod
    def write_to_csv(deck: AnkiDeck, output_path: str) -> bool:
        """Write an AnkiDeck to a CSV file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Question', 'Answer', 'Tags'])
                for card in deck.cards:
                    writer.writerow([card.question, card.answer, ', '.join(card.tags)])
            return True
        except Exception as e:
            print(f"Error writing deck to CSV: {str(e)}")
            return False

class MarkdownProcessor:
    def __init__(self, generator: FlashcardGenerator, writer: DeckWriter):
        self.generator = generator
        self.writer = writer

    def process_file(
        self,
        markdown_path: str, 
        output_path: str, 
        deck_name: str, 
        num_cards: int = 5
    ) -> Optional[AnkiDeck]:
        """Process a markdown file into Anki flashcards and save them as CSV."""
        try:
            with open(markdown_path, "r", encoding='utf-8') as file:
                markdown_content = file.read()
            
            deck = self.generator.generate_deck(
                text=markdown_content, 
                deck_name=deck_name,
                num_cards=num_cards
            )
            
            if deck and self.writer.write_to_csv(deck, output_path):
                return deck
            return None
            
        except Exception as e:
            print(f"Error processing markdown to Anki: {str(e)}")
            return None

    def process_directory(
        self,
        input_dir: str, 
        output_dir: str, 
        num_cards: int = 5
    ) -> List[AnkiDeck]:
        """Process all markdown files in a directory into Anki flashcards."""
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        generated_decks = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.md'):
                input_path = os.path.join(input_dir, filename)
                output_filename = filename.replace('.md', '-flashcards.csv')
                output_path = os.path.join(output_dir, output_filename)
                deck_name = filename[:-3].replace('-', ' ').replace('_', ' ').title()
                
                try:
                    deck = self.process_file(
                        markdown_path=input_path,
                        output_path=output_path,
                        deck_name=deck_name,
                        num_cards=num_cards
                    )
                    if deck:
                        generated_decks.append(deck)
                        print(f"Successfully processed {filename} -> {output_filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        print(f"\nProcessing complete!")
        print(f"Processed {len(generated_decks)} files")
        print(f"Output files can be found in: {output_dir}")
        
        return generated_decks 