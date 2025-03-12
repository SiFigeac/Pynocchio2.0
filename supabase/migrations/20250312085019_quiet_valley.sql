/*
  # Configuration des tables pour le modèle Q&A

  1. Nouvelles Tables
    - `categories` : Stocke les différentes catégories de Q&A (greetings, sillage, simple)
    - `questions` : Stocke toutes les questions possibles
    - `responses` : Stocke toutes les réponses possibles
    - `question_response_mapping` : Table de liaison entre questions et réponses

  2. Sécurité
    - RLS activé sur toutes les tables
    - Politiques de lecture publique
*/

-- Création de la table des catégories
CREATE TABLE IF NOT EXISTS categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  created_at timestamptz DEFAULT now()
);

-- Création de la table des questions
CREATE TABLE IF NOT EXISTS questions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id uuid REFERENCES categories(id),
  text text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Création de la table des réponses
CREATE TABLE IF NOT EXISTS responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id uuid REFERENCES categories(id),
  text text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Table de liaison questions-réponses
CREATE TABLE IF NOT EXISTS question_response_mapping (
  question_id uuid REFERENCES questions(id),
  response_id uuid REFERENCES responses(id),
  PRIMARY KEY (question_id, response_id)
);

-- Activation de RLS
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_response_mapping ENABLE ROW LEVEL SECURITY;

-- Politiques de lecture publique
CREATE POLICY "Allow public read access" ON categories FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Allow public read access" ON questions FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Allow public read access" ON responses FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Allow public read access" ON question_response_mapping FOR SELECT TO PUBLIC USING (true);