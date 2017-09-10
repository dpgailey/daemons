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

DROP TABLE bitcoin_parser_states;

CREATE TABLE bitcoin_blocks (

  hash TEXT NOT NULL,

  merkleRoot TEXT,

  nonce TEXT,

  previousBlockHash TEXT,

  version TEXT,

  weight TEXT,

  chainWork TEXT,

  medianTime TEXT,

  height TEXT,

  difficulty TEXT,

  confirmations TEXT,

  creationTime TEXT,

  versionHex TEXT,

  strippedSize TEXT

);

CREATE TABLE bitcoin_transactions (

  hash TEXT NOT NULL,

  blockHash TEXT,
  
  txid TEXT,

  blockTime TEXT,

  version TEXT,

  confirmations TEXT,

  creationTime TEXT,

  locktime TEXT,

  vsize TEXT,

  size TEXT,

  coinbase TEXT,

  squence TEXT
);

CREATE TABLE bitcoin_parser_states (
  id INT NOT NULL,
  totalBlocks NUMERIC,
  lastBlockHash TEXT
);

INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) values (1, 0, 0);
