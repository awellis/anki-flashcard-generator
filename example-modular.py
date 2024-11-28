from openai import OpenAI
from modular_anki_utils import FlashcardGenerator, DeckWriter, MarkdownProcessor
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
        
    # Initialize components
    client = OpenAI()
    generator = FlashcardGenerator(client)
    writer = DeckWriter()
    processor = MarkdownProcessor(generator, writer)

    # Process a single file
    deck = processor.process_file(
        markdown_path="assets/essays/romantic-essay.md",
        output_path="assets/flashcards/romantic-flashcards.csv",
        deck_name="Romantic Period"
    )

    if deck:
        print("Successfully generated romantic flashcards!")

    # Process an entire directory
    decks = processor.process_directory(
        input_dir="assets/essays",
        output_dir="assets/test-decks"
    )

if __name__ == "__main__":
    main() 