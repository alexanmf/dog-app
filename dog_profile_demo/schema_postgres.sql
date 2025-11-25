-- Dogs table (PostgreSQL)
CREATE TABLE IF NOT EXISTS dogs (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER NOT NULL DEFAULT 0,
  size TEXT NOT NULL DEFAULT 'Medium',
  status TEXT NOT NULL DEFAULT 'Intake',
  kid_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  cat_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  dog_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  notes TEXT NOT NULL DEFAULT '',
  image_url TEXT
);

CREATE INDEX IF NOT EXISTS idx_dogs_name ON dogs (name);

-- Optional: shot documents (if/when you add them)
CREATE TABLE IF NOT EXISTS shot_documents (
  id SERIAL PRIMARY KEY,
  dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  file_url TEXT NOT NULL,
  content_type TEXT NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shot_docs_dog_id ON shot_documents (dog_id);
