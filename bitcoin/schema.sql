/*
{
Block:

* _hash
* hex
* size
* height
* _version
* _previous_block_hash
* _merkle_root
* _timestamp
* _bits
* _nonce
* _difficulty

Transactions:

* _hash
* inputs
* outputs
* _versions
* _locktime
* n_inputs
* n_outputs

*/

DROP TABLE bitcoin_blocks;

DROP TABLE bitcoin_transactions;

CREATE TABLE bitcoin_blocks (

  hash TEXT NOT NULL,

  hex TEXT,

  size TEXT,

  height TEXT,

  version TEXT,

  previous_block_hash TEXT,

  merkle_root TEXT,

  creation_time TIMESTAMP,

  bits TEXT,

  nonce TEXT,

  difficulty TEXT

);

CREATE TABLE bitcoin_transactions (

  hash TEXT NOT NULL,

  inputs TEXT,

  outputs TEXT,

  versions TEXT,

  locktime TEXT,

  n_inputs TEXT,

  n_outputs TEXT
);

CREATE TABLE bitcoin_parser_states (
  id INT,
  total_blocks NUMERIC,
  last_block_checked NUMERIC
);

INSERT INTO bitcoin_parser_states (id, total_blocks, last_block_checked) values (1, 0, 0);
