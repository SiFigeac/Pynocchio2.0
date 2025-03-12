import mysql.connector
import random
from difflib import get_close_matches
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class FrenchQAModel:
    def __init__(self):
        """Initialize the model with MySQL connection."""
        self.connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', '10.97.3.18'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'rootfig46'),
            database=os.getenv('MYSQL_DATABASE', 'pynocchio2')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        tables = """
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS question_response_mapping (
            question_id INT,
            response_id INT,
            PRIMARY KEY (question_id, response_id),
            FOREIGN KEY (question_id) REFERENCES questions(id),
            FOREIGN KEY (response_id) REFERENCES responses(id)
        );
        """
        for statement in tables.split(';'):
            if statement.strip():
                self.cursor.execute(statement)
        self.connection.commit()

    def find_best_match(self, user_input: str) -> str:
        """Find the best matching question and return appropriate response."""
        try:
            # Récupérer toutes les questions
            self.cursor.execute("SELECT id, text FROM questions")
            questions = self.cursor.fetchall()
            all_questions = [(q['id'], q['text'].lower()) for q in questions]
            
            # Trouver la meilleure correspondance
            question_texts = [q[1] for q in all_questions]
            matches = get_close_matches(user_input.lower(), question_texts, n=1, cutoff=0.6)
            
            if matches:
                # Trouver l'ID de la question correspondante
                matched_question = next(q for q in all_questions if q[1] == matches[0])
                question_id = matched_question[0]
                
                # Récupérer les réponses possibles pour cette question
                self.cursor.execute("""
                    SELECT r.text 
                    FROM responses r
                    JOIN question_response_mapping qrm ON r.id = qrm.response_id
                    WHERE qrm.question_id = %s
                """, (question_id,))
                
                responses = self.cursor.fetchall()
                if responses:
                    return random.choice([r['text'] for r in responses])
            
            return "Désolé, je ne comprends pas votre question."
            
        except Exception as e:
            print(f"Erreur lors de la recherche de réponse: {e}")
            return "Désolé, une erreur s'est produite."

    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

def main():
    model = FrenchQAModel()
    
    print("Pynocchio: Bonjour! (Tapez 'quit' pour quitter)")
    
    while True:
        user_input = input("Vous: ").strip()
        
        if user_input.lower() == 'quit':
            print("Pynocchio: Au revoir! À bientôt!")
            break
            
        response = model.find_best_match(user_input)
        print(f"Pynocchio: {response}")

if __name__ == "__main__":
    main()