# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind
import datetime
import psycopg2
import sys
import requests, json
import multiprocessing as mp
import time

from blockchain_parser.blockchain import Blockchain
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from multiprocessing.pool import ThreadPool

rpc_user = "jamie"
rpc_password = "gabpam24"
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))

POOL_SIZE = mp.cpu_count() + 2

max_blocks_per_cycle = 50

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

def get_string_formatter(length):
  data_values = ""
  for index in range(length):
    if (index <= length-2):
      data_values += "%s, "
    else:
      data_values += "%s"

  return data_values

#Saves block & stores information about the last block into bitcoin_parser_states table
def commit_latest_block(hash, index):
  clear_bitcoin_parser_states_sql = "DELETE FROM bitcoin_parser_states"
  cur.execute(clear_bitcoin_parser_states_sql)

  #Updates current block state
  global last_block_hash
  last_block_hash = hash

  global blocks_stored_count
  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) VALUES (%s, %s, %s)"
  data = (1, blocks_stored_count, last_block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()
  blocks_stored_count += 1
  print("Block " + str(blocks_stored_count) + " commited to database at " + str(datetime.datetime.now()))

#Inserts block data into bitcoin_blocks table
def insert_block(block_info):
  cur.execute("INSERT INTO bitcoin_blocks VALUES (" + get_string_formatter(len(block_info)) + ")", block_info)
  print("Added Block: " + str(block_info[0]))

#Inserts transaction data into bitcoin_transactions table
def insert_transaction(trans_info):
  cur.execute("INSERT INTO bitcoin_transactions VALUES (" + get_string_formatter(len(trans_info)) + ")", trans_info)
  print("Added Trans: " + str(trans_info[0]))

def current_blockchain_length():
  return rpc_connection.batch_([["getblockcount"]])[0]

def parse_block_to_postgresql_database(block_data):

  block = block_data[0]
  block_index = block_data[1]

  try:
    block_info = list()

    median_time = block["mediantime"]
    median_time_timestamp = datetime.datetime.fromtimestamp(median_time)

    creation_time = block["time"]
    creation_time_timestamp = datetime.datetime.fromtimestamp(creation_time)

    block_info.append(block["hash"])
    block_info.append(block["merkleroot"])
    block_info.append(block["nonce"])
    block_info.append(block["nonce"])

    if (blocks_stored_count == 0):
      block_info.append("NULL")
    else:
      block_info.append(block["previousblockhash"])

    block_info.append(block["version"])
    block_info.append(block["weight"])
    block_info.append(block["weight"])
    block_info.append(block["chainwork"])
    block_info.append(median_time_timestamp)
    block_info.append(median_time)
    block_info.append(block["height"])
    block_info.append(block["height"])
    block_info.append(block["difficulty"])
    block_info.append(block["difficulty"])
    block_info.append(block["confirmations"])
    block_info.append(creation_time_timestamp)
    block_info.append(creation_time)
    block_info.append(block["versionHex"])
    block_info.append(block["strippedsize"])
    block_info.append(block["strippedsize"])

    print("Adding block: " + str(block_index))

    #length = len(block_info)

    #data_values = ""
    #for index in range(length):
    #  if (index <= length-2):
    #    data_values += "%s, "
    #  else:
    #    data_values += "%s"

    #parsed_info = list()

    #parsed_info.append(block_info)

    #cur.execute("INSERT INTO bitcoin_blocks VALUES (" + data_values + ")", block_info)

    #print("Added Block: " + str(block_info[0]))

    insert_block(block_info)

    if (blocks_stored_count >= 1):
      #Loops through transactions, compiles data for storage
      for txid in block["tx"]:
        raw_trans = rpc_connection.batch_([["getrawtransaction", txid, 1]])
        for transaction in raw_trans:

          trans_block_time = transaction["blocktime"]
          trans_block_time_timestamp = datetime.datetime.fromtimestamp(trans_block_time)

          trans_creation_time = transaction["time"]
          trans_creation_time_timestamp = datetime.datetime.fromtimestamp(trans_creation_time)

          trans_info = list()
          trans_info.append(transaction["hash"])
          trans_info.append(transaction["blockhash"])
          trans_info.append(transaction["hex"])
          trans_info.append(transaction["txid"])
          trans_info.append(trans_block_time_timestamp)
          trans_info.append(trans_block_time)
          trans_info.append(transaction["version"])
          trans_info.append(transaction["confirmations"])
          trans_info.append(trans_creation_time_timestamp)
          trans_info.append(trans_creation_time)
          trans_info.append(transaction["locktime"])
          trans_info.append(transaction["vsize"])
          trans_info.append(transaction["vsize"])
          trans_info.append(transaction["size"])
          trans_info.append(transaction["size"])

          trans_vin = transaction["vin"][0]

          try:
            trans_info.append(trans_vin["coinbase"])
          except:
            trans_info.append("NULL")

          trans_info.append(trans_vin["sequence"])

          #trans_info_list.append(trans_info)
          insert_transaction(trans_info)

    #Commits changes
    commit_latest_block(block_info[0], block_index)
  except Exception as e:
    print(e)
    global blocks_to_check
    blocks_to_check.append(block_index)

    #DELETE ALL RELATED BLOCK INFO
    #print("Issue committing block: " + str(blocks_stored_count))

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

#Initiates block state
last_block_hash = None
blocks_stored_count = 0
get_last_block_state()

blocks_to_check = list()

if __name__ == "__main__":

  full_chain_length = current_blockchain_length()

  print("Parsing from block: " + str(blocks_stored_count) + " to " + str(full_chain_length))

  #Loops through bitcoin_blockchain extracting block & transaction info
  while (full_chain_length - blocks_stored_count > 0):



    #Makes sure it doesn't try to parse more blocks than there are
    if ((full_chain_length - blocks_stored_count) < max_blocks_per_cycle):
      blocks_per_cycle = full_chain_length - blocks_stored_count
    else:
      blocks_per_cycle = max_blocks_per_cycle

    for index in range(blocks_stored_count, blocks_stored_count + (blocks_per_cycle - len(blocks_to_check))):
      blocks_to_check.append(index)

    tryCount = 50
    while tryCount > 0:
      try:
        #Gets the current block for parsing from blockchain
        commands = [ [ "getblockhash", block_index] for block_index in blocks_to_check]
        block_hashes = rpc_connection.batch_(commands)
        blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
        break
      except Exception as e:
        print(e)
        tryCount -= 1


    #blocks_with_trans = list()

    #current_block_hash = rpc_connection.batch_([["getblockhash", 0]])
    #current_blocks = rpc_connection.batch_([["getblock", current_block_hash[0]]])
    #block = current_blocks[0]

    print(len(blocks_to_check))

    #for index in range(len(blocks_to_check)):
    #  parse_block_to_postgresql_database(blocks[index], blocks_to_check[index])

    #for block in blocks:
    #  parse_block_to_postgresql_database(block)

    #manager = Manager()

    POOL = mp.Pool(POOL_SIZE)
    #POOL = ThreadPool(POOL_SIZE)
    #for block_index in range(len(blocks_to_check)):
    #  POOL.join(parse_block_to_postgresql_database, blocks[block_index], blocks_to_check[block_index])
    POOL.map(parse_block_to_postgresql_database, (blocks, blocks_to_check))
    POOL.close()
    #POOL.join()
    #for result in parse_results:
    #  print("RESULT: " + result[0][0])
    #  commit_latest_block(result[0][0])


    #nums = [0,1,2,3,4,5,6,7,8,9,10]

    #POOL.map(simpleTest, nums)
    print("TEST")
    #POOL.close()


#Closes the database & program once complete
cur.close()
conn.close()
sys.exit(1)
