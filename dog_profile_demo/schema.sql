DROP TABLE IF EXISTS dogs;

CREATE TABLE dogs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  age INTEGER DEFAULT 0,
  size TEXT CHECK (size IN ('Small','Medium','Large')) NOT NULL DEFAULT 'Medium',
  status TEXT CHECK (status IN ('Intake','Fostered','Hold','Adopted','Transferred')) NOT NULL DEFAULT 'Intake',
  kid_friendly INTEGER NOT NULL DEFAULT 0,
  cat_friendly INTEGER NOT NULL DEFAULT 0,
  dog_friendly INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);