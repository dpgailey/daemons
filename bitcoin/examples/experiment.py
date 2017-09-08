# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind
import datetime
import psycopg2
import sys
import requests, json

from blockchain_parser.blockchain import Blockchain


#Loads up the last block state it was on
def get_last_block_state():
  try:
    get_last_block_hash_sql = "SELECT * FROM bitcoin_parser_states"
    cur.execute(get_last_block_hash_sql)
    last_block_row = cur.fetchall()

    #Sets up last block state reference
    global total_blocks
    total_blocks = last_block_row[0][1]
    global last_block_hash
    last_block_hash = last_block_row[0][2]

    print("Succesfully restored block state at block: " + str(last_block_row[0][1]))
  except ValueError:
    print("Unable to get last block state error: " + ValueError)

#Saves block & stores information about the last block into bitcoin_parser_states table
def commit_latest_block(hash):
  clear_bitcoin_parser_states_sql = "DELETE FROM bitcoin_parser_states"
  cur.execute(clear_bitcoin_parser_states_sql)

  #Updates current block state
  global total_blocks
  total_blocks += 1
  global last_block_hash
  last_block_hash = hash

  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, total_blocks, last_block_hash) VALUES (%s, %s, %s)"
  data = (1, total_blocks, last_block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()
  print("Block " + str(total_blocks) + " commited to database at " + str(datetime.datetime.now()))

#Inserts block data into bitcoin_blocks table
def insert_block(block_info):
  sql = "INSERT INTO bitcoin_blocks (hash, hex, size, height, version, previous_block_hash, merkle_root, creation_time, bits, nonce, difficulty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  data = (block_info[0],block_info[1],block_info[2],block_info[3],block_info[4],block_info[5],block_info[6],block_info[7],block_info[8],block_info[9],block_info[10])
  cur.execute(sql, data)
  print("Added Block: " + str(block_info[0]))

#Inserts transaction data into bitcoin_transactions table
def insert_transaction(transaction_info):
  sql = "INSERT INTO bitcoin_transactions (hash, inputs, outputs, versions, locktime, n_inputs, n_outputs) VALUES (%s, %s, %s, %s, %s, %s, %s)"
  data = (transaction_info[0],transactionInfo[1],transactionInfo[2],transactionInfo[3],transactionInfo[4],transactionInfo[5],transactionInfo[6])
  cur.execute(sql, data)
  print("Added Trans: " + str(transactionInfo[0]))

last_block_hash = None
total_blocks = 0

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

#Creates blockchain from blocks folder submited in argument
blockchain = Blockchain(sys.argv[1])

get_last_block_state()
matching_hash = False

#Loops through bitcoin_blockchain extracting block & transaction info
for block in blockchain.get_unordered_blocks():

  if (last_block_hash == None or matching_hash == True):
    header = block.header

    print("Block " + str(total_blocks + 1) + " origional creation time: " + str(header.timestamp))

    #Compiles block & header data for storage
    block_info = [block.hash, str(header.from_hex), block.size, block.height,
    header.version, header.previous_block_hash, header.merkle_root,
    header.timestamp, header.bits, header.nonce, header.difficulty]
    insert_block(block_info)

    #Loops through transactions, compiles data for storage
    for tx in block.transactions:
      for no, output in enumerate(tx.outputs):
        transactionInfo = [tx.hash, str(tx.inputs), str(tx.outputs),
        tx._version, tx._locktime, tx.n_inputs, tx.n_outputs]
        insert_transaction(transactionInfo)

    #Commits changes
    commit_latest_block(block.hash)
  else:
    matching_hash = (last_block_hash == block.hash)


#Closes the database & program
cur.close()
conn.close()
sys.exit(1)
