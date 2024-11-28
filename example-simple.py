from dotenv import load_dotenv
from openai import OpenAI

from anki_utils import process_markdown_to_anki, process_directory_to_anki  

# Load environment variables
load_dotenv()

# Initialize components
client = OpenAI()

# Process a single file
deck = process_markdown_to_anki(
    client=client,
    markdown_path="assets/essays/romantic-essay.md",
    output_path="assets/flashcards/romantic-flashcards.csv",
    deck_name="Romantic Period"
)

if deck:
    print("Successfully generated romantic flashcards!")

# Process entire directory
decks = process_directory_to_anki(
    client=client,
    input_dir="assets/essays",
    output_dir="assets/output_simple"
) 