import json
import mysql.connector
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    """Établit la connexion à la base de données MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', '10.97.3.18'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'rootfig46'),
            database=os.getenv('MYSQL_DATABASE', 'pynocchio2')
        )
        print("✅ Connexion à la base de données réussie!")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Erreur de connexion: {err}")
        raise

def import_json_data(connection, json_files: List[str]):
    """Importe les données des fichiers JSON dans la base de données."""
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Créer la catégorie par défaut
        cursor.execute(
            "INSERT INTO categories (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
            ("général",)
        )
        category_id = cursor.lastrowid
        connection.commit()
        
        for json_file in json_files:
            print(f"\nImportation de {json_file}...")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                for greeting in data.get('greetings', []):
                    # Insérer les questions
                    for question_text in greeting['questions']:
                        cursor.execute(
                            "INSERT INTO questions (category_id, text) VALUES (%s, %s)",
                            (category_id, question_text)
                        )
                        question_id = cursor.lastrowid
                        
                        # Insérer les réponses et créer les mappings
                        for response_text in greeting['responses']:
                            cursor.execute(
                                "INSERT INTO responses (category_id, text) VALUES (%s, %s)",
                                (category_id, response_text)
                            )
                            response_id = cursor.lastrowid
                            
                            # Créer le mapping question-réponse
                            cursor.execute(
                                "INSERT INTO question_response_mapping (question_id, response_id) VALUES (%s, %s)",
                                (question_id, response_id)
                            )
                    
                    connection.commit()
                print(f"✅ Données de {json_file} importées avec succès!")
                    
            except FileNotFoundError:
                print(f"❌ Fichier {json_file} non trouvé.")
            except json.JSONDecodeError:
                print(f"❌ Erreur de format JSON dans {json_file}")
            except Exception as e:
                print(f"❌ Erreur lors de l'importation de {json_file}: {e}")
                connection.rollback()
    
    finally:
        cursor.close()

def main():
    json_files = [
        'data/greetings.json',
        'data/simple.json',
        'data/sillage.json',
        'data/personnel.json',
    ]
    
    try:
        connection = connect_to_db()
        import_json_data(connection, json_files)
        print("\n✅ Importation terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Une erreur est survenue: {e}")
    
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main()