import openai
import csv

def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_questions(content, taxonomy_level, api_key, num_questions=5):
    openai.api_key = api_key
    
    prompt = f"""
    Based on this content, generate {num_questions} questions and answers at the {taxonomy_level} level 
    of Bloom's taxonomy. Format as JSON: [{{"question": "text", "answer": "text"}}]
    
    Content:
    {content}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return eval(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
        return []

def create_anki_csv(qa_pairs, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["front", "back"])
        for qa in qa_pairs:
            writer.writerow([qa['question'], qa['answer']])

def main():
    api_key = "your-api-key-here"
    input_file = "input.md"
    output_file = "anki_cards.csv"
    
    content = read_markdown(input_file)
    qa_pairs = generate_questions(content, "analysis", api_key)
    create_anki_csv(qa_pairs, output_file)
    print(f"Generated {len(qa_pairs)} flashcards")

if __name__ == "__main__":
    main()