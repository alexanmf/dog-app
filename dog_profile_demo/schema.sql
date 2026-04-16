DROP TABLE IF EXISTS dog_messages;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS dogs;

-- =========================
-- USERS
-- =========================
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'staff',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- DOGS
-- =========================
CREATE TABLE dogs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  breed TEXT,
  age TEXT,
  size TEXT,
  friendliness TEXT,
  status TEXT NOT NULL DEFAULT 'Available',
  image_url TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- DOCUMENTS
-- =========================
CREATE TABLE documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dog_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  file_url TEXT NOT NULL,
  document_type TEXT,
  notes TEXT,
  uploaded_by INTEGER,
  uploaded_by_name TEXT,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (dog_id) REFERENCES dogs(id) ON DELETE CASCADE,
  FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- =========================
-- DOG MESSAGES (CHAT)
-- =========================
CREATE TABLE dog_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dog_id INTEGER NOT NULL,
  user_id INTEGER,
  sender_name TEXT,
  sender_role TEXT,
  message TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (dog_id) REFERENCES dogs(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
