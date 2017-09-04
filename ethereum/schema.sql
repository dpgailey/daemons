/* Probably should have used this in retrospect: https://github.com/almindor/etherdb/blob/master/sql/tables.sql */

/*
{
  'blockHash': '0x72d328af4835d1c087c39326317b5b98c70124760c3788ae1b1dd87736f19bd4', 
  'blockNumber': '0x3bc50f', 
  'from': '0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5', 
  'gas': '0xc350', 
  'gasPrice': '0x12a05f200', 
  'hash': '0xdc256d0fb22cad4c09bbb39b04a6d698fb3b4a2f48007b6b72c2914c4e49e133', 
  'input': '0x', 
  'nonce': '0x20b3c5', 
  'to': '0x58e4dd01bdaae3b04d7f725ad7b39520b8c91df2', 
  'transactionIndex': '0x51', 
  'value': '0x2d1cf2b663599e0', 
  'v': '0x26', 
  'r': '0x1d4fccde10ef2f2603da8dce43057913308ae6bf8a00f82103f8ea23f70cda1', 
  's': '0x7a05d093abc46f947389bfb8f43e66967dc5c1a238624fd9f52e5360a5e66e84', 
  'blockNumber_int': 3917071,
  'blockTimestamp_int': datetime.datetime(2017, 6, 23, 1, 18, 52),
  'value_eth': 0.20317124351371516,
  'value_int': 203171243513715168,
  'gasPrice_int': 5000000000,
  'gas_int': 50000,
  'input_str': '0x', 
  'transactionIndex_int': 81}],
  'transactionsRoot': '0x7e24ebe62f1f913d4e92fcab7475c4e67751fea8041e1314a4216855ff42ce2f', 
  'uncles': [],
  'number_int': 3917071,
  'difficulty_int': 871047975820878,
  'extraData_str': '0x706f6f6c2e65746866616e732e6f726720284d4e313129', 
  'timestamp_int': datetime.datetime(2017, 6, 23, 1, 18, 52),
  'gasLimit_int': 4712394,
  'gasUsed_int': 4681615,
  'size_int': 15323,
  'transactionCount': 82,
  'txValueSum_int': 275011870412826043342,
  'totalDifficulty_int': 387548973672392071386}
*/

CREATE TABLE ethereum_blocks (
  difficulty TEXT,
  difficulty_int NUMERIC,

  extraData TEXT,
  extraData_str TEXT,

  gasLimit TEXT,
  gasLimit_int NUMERIC,

  gasUsed TEXT,
  gasUsed_int NUMERIC,

  blockhash TEXT NOT NULL,

  logsBloom TEXT,
  miner TEXT,
  mixHash TEXT,

  nonce TEXT,
  "number" TEXT NOT NULL,
  number_int NUMERIC,

  parentHash TEXT,
  receiptsRoot TEXT NOT NULL,

  sha3Uncles TEXT NOT NULL,

  size TEXT NOT NULL,
  size_int NUMERIC,

  stateRoot TEXT NOT NULL,
  "timestamp" TIMESTAMP,
  timestamp_int TIMESTAMP,

  totalDifficulty TEXT NOT NULL,
  totalDifficulty_int NUMERIC,

  transactionsRoot TEXT NOT NULL,
  uncles TEXT,

  txvaluesum_int NUMERIC,

  transactionCount NUMERIC

);

CREATE TABLE ethereum_transactions (
  blockHash TEXT NOT NULL,
  blockNumber TEXT NOT NULL,
  blockNumber_int NUMERIC,

  blockTimestamp TIMESTAMP,
  blockTimestamp_int TIMESTAMP,

  "to" TEXT,
  "from" TEXT,

  gas TEXT NOT NULL,
  gas_int NUMERIC,

  gasPrice TEXT NOT NULL,
  gasPrice_int NUMERIC,

  txhash TEXT NOT NULL,

  "input" TEXT,
  input_str TEXT,

  nonce TEXT,

  transactionIndex TEXT NOT NULL,
  transactionIndex_int NUMERIC,

  "value" TEXT,
  value_int NUMERIC,
  value_eth DECIMAL,

  v TEXT,
  r TEXT,
  s TEXT
);

CREATE TABLE ethereum_parser_states (
  id INT,
  last_block_number NUMERIC,
  total_blocks NUMERIC,
  highest_block_number NUMERIC
);

INSERT INTO ethereum_parser_states (id, last_block_number, total_blocks) values (1, 0, 0);
