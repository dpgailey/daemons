CREATE TABLE ethereum_blocks (
  difficulty VARCHAR(255),
  difficulty_int BIGINT,

  extraData VARCHAR(255),
  extraData_str VARCHAR(255),

  gasLimit VARCHAR(255),
  gasLimit_int BIGINT,

  gasUsed VARCHAR(255),
  gasUsed_int BIGINT,

  logsBloom VARCHAR(255),
  miner VARCHAR(255),
  mixHash VARCHAR(255),
  nonce VARCHAR(255),
  number VARCHAR(255),
  number_int BIGINT,

  parentHash VARCHAR(255),
  receiptsRoot VARCHAR(255),

  sha3Uncles VARCHAR(255),

  size VARCHAR(255),
  size_int BIGINT,

  stateRoot VARCHAR(255),
  timestamp TIMESTAMP,

  totalDifficulty VARCHAR(255),
  totalDifficult_int BIGINT,

  transactionCount INT
);

CREATE TABLE ethereum_transactions (
  blockHash VARCHAR(255),
  blockNumber VARCHAR(255),
  blockNumber_int BIGINT,

  to_addr VARCHAR(255),
  from_addr VARCHAR(255),

  gas VARCHAR(255),
  gas_int BIGINT,

  gasPrice VARCHAR(255),
  gasPrice_int BIGINT,

  hash VARCHAR(255),

  input VARCHAR(255),
  input_str VARCHAR(255),

  nonce VARCHAR(255),

  transactionIndex VARCHAR(255),
  transactionIndex_int BIGINT,

  value VARCHAR(255),
  value_int BIGINT,
  value_eth DECIMAL(10,10)
);

CREATE TABLE ethereum_parser_states (
  last_block_number BIGINT
);
