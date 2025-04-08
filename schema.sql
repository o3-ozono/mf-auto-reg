DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
  id TEXT PRIMARY KEY,                          
  source_email_id TEXT NOT NULL UNIQUE,         
  parsed_data TEXT NOT NULL,                   
  mf_status TEXT NOT NULL CHECK (mf_status IN ('pending', 'registered', 'error')), 
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  
);
