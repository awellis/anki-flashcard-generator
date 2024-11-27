# Import required libraries
from dotenv import load_dotenv  # For loading environment variables
from openai import OpenAI 

# Load environment variables from .env file (likely contains OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client using API key from environment variables
client = OpenAI()

# Load and read the contents of the baroque essay markdown file
with open("assets/essays/baroque-essay.md", "r") as file:
    baroque = file.read()

#%%
# Print the contents of the baroque essay (for debugging/verification)
print(baroque)
# %%

#%%
def generate_response(text,
        model="gpt-4o", 
        temperature=1.0, 
        top_p=1.0, 
        max_tokens=2048,
        n = 1):
    """
    Generate flashcard content using OpenAI's API.
    
    Args:
        text (str): Input text to generate flashcards from
        model (str): OpenAI model to use
        temperature (float): Controls randomness (0-1)
        top_p (float): Controls diversity of responses (0-1)
        max_tokens (int): Maximum length of generated response
        n (int): Number of alternative responses to generate
    
    Returns:
        OpenAI API response object containing generated flashcards
    """
    # Define the system message that instructs GPT on how to create flashcards
    system_message = """You are an expert at creating Anki flashcards. Your task is to:
1. Read the provided text
2. Create 5 Anki flashcards that cover the main concepts
3. Format the output as a list of flashcard pairs, with each pair on a new line in the format:
   Question, Answer."""

    # Construct the user message with the input text
    user_message = f"Please create Anki flashcards for the following text: {text}"
    
    # Make API call to OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        n=n
    )
    
    return response

#%%
def parse_response(response):
    """
    Parse all responses from the OpenAI API response object.
    
    Args:
        response: OpenAI API response object
        
    Returns:
        list: List of response contents as strings
    """
    # Extract the content from each choice in the response
    return [choice.message.content for choice in response.choices]

#%%
# Generate multiple responses for the baroque text
responses = generate_response(baroque, n=2)

#%% 
# Parse the generated responses into a list of strings
parsed_responses = parse_response(responses)

#%%
# Print each response with an index number
for idx, content in enumerate(parsed_responses, 1):
    print(f"Response {idx}:\n{content}\n")

# %%
# Import Pydantic for data validation and typing
from pydantic import BaseModel, Field
from typing import List

#%%
class AnkiFlashcard(BaseModel):
    """
    Model representing a single Anki flashcard with question, answer, and tags.
    """
    # Define required fields with descriptions
    question: str = Field(..., description="The front side of the flashcard containing the question")
    answer: str = Field(..., description="The back side of the flashcard containing the answer")
    tags: List[str] = Field(..., description="List of tags associated with the flashcard")

class AnkiDeck(BaseModel):
    """
    Model representing a complete Anki deck containing multiple flashcards.
    """
    # Define required fields with descriptions
    cards: List[AnkiFlashcard] = Field(..., description="List of flashcards in the deck")
    deck_name: str = Field(..., description="Name of the Anki deck")

# %%
def generate_structured_flashcards(text: str, deck_name: str, num_cards: int = 5) -> AnkiDeck:
    """
    Generate structured flashcards using GPT-4 with enforced Pydantic model output.
    
    Args:
        text (str): The input text to generate flashcards from
        deck_name (str): Name for the Anki deck
        num_cards (int): Number of flashcards to generate (default: 5)
        
    Returns:
        AnkiDeck: A structured deck of flashcards with proper validation
        
    Raises:
        ValueError: If num_cards is less than 1
    """
    # Validate input
    if num_cards < 1:
        raise ValueError("Number of cards must be at least 1")
    
    # Make API call with structured output format
    completion = client.beta.chat.completions.parse(
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
    
    # Return the parsed response
    return completion.choices[0].message.parsed

#%%
# Generate a deck of flashcards for the baroque text
baroque_deck = generate_structured_flashcards(baroque, "Baroque Period")
# %%
# Display the entire deck
baroque_deck
#%%
# Display just the cards from the deck
baroque_deck.cards

# %%
# Print each card's details in a formatted way
for card in baroque_deck.cards:
    print(f"Question: {card.question}")
    print(f"Answer: {card.answer}")
    print(f"Tags: {', '.join(card.tags)}")
    print("-" * 20)

# %%
# Import libraries for file operations
import csv
import os
#%%
# Create directory for flashcard output if it doesn't exist
os.makedirs('assets/flashcards', exist_ok=True)

# Export flashcards to CSV file
with open('assets/flashcards/baroque-flashcards.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write header row
    writer.writerow(['Question', 'Answer', 'Tags'])
    # Write each flashcard as a row in the CSV
    for card in baroque_deck.cards:
        writer.writerow([card.question, card.answer, ', '.join(card.tags)])

# %%
def process_markdown_to_anki(markdown_path: str, output_path: str, deck_name: str, num_cards: int = 5) -> AnkiDeck:
    """
    Process a markdown file into Anki flashcards and save them as CSV.
    
    Args:
        markdown_path (str): Path to the input markdown file
        output_path (str): Path where the CSV file should be saved
        deck_name (str): Name for the Anki deck
        num_cards (int): Number of flashcards to generate (default: 5)
        
    Returns:
        AnkiDeck: The generated deck object
        
    Raises:
        FileNotFoundError: If markdown_path doesn't exist
        PermissionError: If output_path can't be written to
    """
    # Read the markdown file
    with open(markdown_path, "r", encoding='utf-8') as file:
        markdown_content = file.read()
    
    # Generate the Anki deck
    deck = generate_structured_flashcards(
        text=markdown_content, 
        deck_name=deck_name,
        num_cards=num_cards
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(['Question', 'Answer', 'Tags'])
        # Write each flashcard as a row
        for card in deck.cards:
            writer.writerow([card.question, card.answer, ', '.join(card.tags)])
    
    return deck

# Example usage:
modern_deck = process_markdown_to_anki(
    markdown_path="assets/essays/modern-essay.md",
    output_path="assets/flashcards/modern-flashcards.csv",
    deck_name="Modern Period"
)

# %%

def process_directory_to_anki(input_dir: str, output_dir: str, num_cards: int = 5) -> List[AnkiDeck]:
    """
    Process all markdown files in a directory into Anki flashcards and save them as CSV files.
    
    Args:
        input_dir (str): Directory containing markdown files
        output_dir (str): Directory where CSV files should be saved
        num_cards (int): Number of flashcards to generate per deck (default: 5)
        
    Returns:
        List[AnkiDeck]: List of all generated deck objects
        
    Raises:
        FileNotFoundError: If input_dir doesn't exist
        PermissionError: If output_dir can't be written to
    """
    # Ensure input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List to store all generated decks
    generated_decks = []
    
    # Process each markdown file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.md'):
            # Create paths
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.md', '-flashcards.csv')
            output_path = os.path.join(output_dir, output_filename)
            
            # Generate deck name from filename (remove extension and replace hyphens/underscores with spaces)
            deck_name = filename[:-3].replace('-', ' ').replace('_', ' ').title()
            
            try:
                # Process the file with specified number of cards
                deck = process_markdown_to_anki(
                    markdown_path=input_path,
                    output_path=output_path,
                    deck_name=deck_name,
                    num_cards=num_cards
                )
                generated_decks.append(deck)
                print(f"Successfully processed {filename} -> {output_filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Print summary
    print(f"\nProcessing complete!")
    print(f"Processed {len(generated_decks)} files")
    print(f"Output files can be found in: {output_dir}")
    
    return generated_decks

#%%
# Example usage:
decks = process_directory_to_anki(
    input_dir="assets/essays",
    output_dir="assets/flashcards"
)

# %%
