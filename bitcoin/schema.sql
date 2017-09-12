/*
Block:

  'hash': '0000000097e8325b37343ea6e7004b8b088602a68065cd7ada89aef6da0a3abe'
  'merkleRoot': 'a21f53c4457aacf4a3403e8e8dc97745379970148ac1448c15cb8cac8006af4e'
  'nonce': '3987125286'
  'previousBlockHash': '00000000d5ab597214e9a7d2f83e0a21696d5ebf4910c2d7d283794d68129aac'
  'version': '1'
  'weight': '864'
  'chainWork': '000000000000000000000000000000000000000000000000000002fc02fc02fc'
  'medianTime': '1232157221'
  'height': '763'
  'difficulty': '1'
  'confirmations': '467622'
  'creationTime': '1232161744'
  'versionHex': '00000001'
  'strippedSize': '216'

Transactions:

  'hash': '439aee1e1aa6923ad61c1990459f88de1faa3e18b4ee125f99b94b82e1e0af5f'
  'blockHash': '000000002978eecde8d020f7f057083bc990002fff495121d7dc1c26d00c00f8'
  'hex': '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0704ffff001d011effffffff0100f2052a01000000434104c9eb99d7bbbd9acfab695c8aa8b931beb43292f2fecdc19d7e687b524d2e2c8a9d167f9be930634adae005424b441a9de8e8c15d8b2462661eb78418a8aba662ac00000000'
  'txid': '439aee1e1aa6923ad61c1990459f88de1faa3e18b4ee125f99b94b82e1e0af5f'
  'blockTime': '1231610361'
  'version': '1'
  'confirmations': '481769'
  'creationTime': '1231610361'
  'locktime': '0'
  'vsize': '134'
  'size': '134'
  'coinbase': '04ffff001d011e'
  'squence': '4294967295'

*/

DROP TABLE bitcoin_blocks;

DROP TABLE bitcoin_transactions;

DROP TABLE bitcoin_parser_states;

CREATE TABLE bitcoin_blocks (

  hash TEXT NOT NULL,

  merkleRoot TEXT,

  nonce TEXT,
  nonce_int NUMERIC,

  previousBlockHash TEXT,

  version TEXT,

  weight TEXT,
  weight_int NUMERIC,

  chainWork TEXT,

  medianTime TEXT,
  medianTime_int NUMERIC,

  height TEXT,
  height_int NUMERIC,

  difficulty TEXT,
  difficulty_int NUMERIC,

  confirmations TEXT,

  creationTime TIMESTAMP,
  creationTime_int NUMERIC,

  versionHex TEXT,

  strippedSize TEXT,
  strippedSize_int NUMERIC

);

CREATE TABLE bitcoin_transactions (

  hash TEXT NOT NULL,

  blockHash TEXT,

  hex TEXT,

  txid TEXT,

  blockTime TIMESTAMP,
  blockTime_str TEXT,

  version TEXT,

  confirmations TEXT,

  creationTime TIMESTAMP,
  creationTime_str TEXT,

  locktime TEXT, /*Not actualy time based*/

  vsize TEXT,
  vsize_int NUMERIC,

  size TEXT,
  size_int NUMERIC,

  coinbase TEXT,

  squence TEXT
);

CREATE TABLE bitcoin_parser_states (
  id INT NOT NULL,
  totalBlocks NUMERIC,
  lastBlockHash TEXT
);

INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) values (1, 0, 0);

/* INDEXES */

CREATE INDEX bitcoin_block_hash ON bitcoin_blocks (hash);
CREATE INDEX bitcoin_block_merkle_root ON bitcoin_blocks (merkleRoot);
CREATE INDEX bitcoin_tx_and_hash ON bitcoin_transactions (txid, hash);
CREATE INDEX bitcoin_tx_hash ON bitcoin_transactions (hash);
