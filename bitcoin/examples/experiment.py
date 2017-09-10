# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind
import datetime
import psycopg2
import sys
import requests, json

from blockchain_parser.blockchain import Blockchain

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = "jamie"
rpc_password = "gabpam24"
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))

blockchain_length = rpc_connection.batch_([["getblockcount"]])

#Loads up the last block state it was on
def get_last_block_state():
  try:
    get_last_block_hash_sql = "SELECT * FROM bitcoin_parser_states"
    cur.execute(get_last_block_hash_sql)
    last_block_row = cur.fetchall()


    #Sets up last block state reference
    global blocks_stored_count
    blocks_stored_count = last_block_row[0][1]
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
  global last_block_hash
  last_block_hash = hash

  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) VALUES (%s, %s, %s)"
  data = (1, blocks_stored_count, last_block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()
  print("Block " + str(blocks_stored_count) + " commited to database at " + str(datetime.datetime.now()))

#Inserts block data into bitcoin_blocks table
def insert_block(block_info):
  sql = "INSERT INTO bitcoin_blocks (hash, merkleRoot, nonce, previousBlockHash, version, weight, chainWork, medianTime, height, difficulty, confirmations, creationTime, versionHex, strippedSize) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

  data = (block_info[0],block_info[1],block_info[2],block_info[3],block_info[4],block_info[5],block_info[6],block_info[7],block_info[8],block_info[9],block_info[10],block_info[11],block_info[12],block_info[13])
  cur.execute(sql, data)
  print("Added Block: " + str(block_info[0]))

#Inserts transaction data into bitcoin_transactions table
def insert_transaction(trans_info):
  sql = "INSERT INTO bitcoin_transactions (hash, blockHash, txid, blockTime, version, confirmations, creationTime, locktime, vsize, size, coinbase, squence) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  data = (trans_info[0],trans_info[1],trans_info[2],trans_info[3],trans_info[4],trans_info[5],trans_info[6],trans_info[7],trans_info[8],trans_info[9],trans_info[10],trans_info[11])
  cur.execute(sql, data)
  print("Added Trans: " + str(trans_info[0]))

last_block_hash = None
blocks_stored_count = 0

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

get_last_block_state()

print("Parsing from block: " + str(blocks_stored_count) + " to " + str(blockchain_length[0]))
#Loops through bitcoin_blockchain extracting block & transaction info
for blocks_stored_count in range(blocks_stored_count, blockchain_length[0]):

    #Gets the current block for parsing from blockchain
    current_block_hash = rpc_connection.batch_([["getblockhash", blocks_stored_count]])
    current_blocks = rpc_connection.batch_([["getblock", current_block_hash[0]]])
    block = current_blocks[0]

    block_info = list()
    block_info.append(block["hash"])
    block_info.append(block["merkleroot"])
    block_info.append(block["nonce"])

    if (blocks_stored_count == 0):
      block_info.append("NULL")
    else:
      block_info.append(block["previousblockhash"])

    block_info.append(block["version"])
    block_info.append(block["weight"])
    block_info.append(block["chainwork"])
    block_info.append(block["mediantime"])
    block_info.append(block["height"])
    block_info.append(block["difficulty"])
    block_info.append(block["confirmations"])
    block_info.append(block["time"])
    block_info.append(block["versionHex"])
    block_info.append(block["strippedsize"])

    print("Adding block: " + str(blocks_stored_count))

    insert_block(block_info)

    if (blocks_stored_count >= 1):
      #Loops through transactions, compiles data for storage
      for txid in block["tx"]:
        raw_trans = rpc_connection.batch_([["getrawtransaction", txid, 1]])
        for transaction in raw_trans:

          trans_info = list()
          trans_info.append(transaction["hash"])
          trans_info.append(transaction["blockhash"])
          trans_info.append(transaction["hex"])
          trans_info.append(transaction["txid"])
          trans_info.append(transaction["blocktime"])
          trans_info.append(transaction["version"])
          trans_info.append(transaction["confirmations"])
          trans_info.append(transaction["time"])
          trans_info.append(transaction["locktime"])
          trans_info.append(transaction["vsize"])
          trans_info.append(transaction["size"])

          trans_vin = transaction["vin"][0]

          try:
            trans_info.append(trans_vin["coinbase"])
          except:
            trans_info.append("NULL")

          trans_info.append(trans_vin["sequence"])

          insert_transaction(trans_info)

    #Commits changes
    commit_latest_block(block_info[0])


#Closes the database & program
cur.close()
conn.close()
sys.exit(1)
