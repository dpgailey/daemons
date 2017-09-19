# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind
import datetime
import psycopg2
import sys
import requests, json
import multiprocessing as mp
import time
import itertools

from pebble import ProcessPool
from pebble.common import ProcessExpired
from concurrent.futures import TimeoutError
from concurrent.futures import ProcessPoolExecutor
from blockchain_parser.blockchain import Blockchain
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from multiprocessing.pool import ThreadPool


rpc_user = "jamie"
rpc_password = "gabpam24"
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))


max_blocks_per_cycle = 1000

#Loads up the last block state it was on
def get_last_block_state():
  get_last_block_hash_sql = "SELECT * FROM bitcoin_parser_states"
  cur.execute(get_last_block_hash_sql)
  last_block_row = cur.fetchall()

  #Sets up last block state reference
  blocks_stored_count = last_block_row[0][1]
  last_block_hash = last_block_row[0][2]

  print("Succesfully restored block state at block: " + str(last_block_row[0][1]))

  return [blocks_stored_count, last_block_hash]

#Loads up the last block state it was on
def get_failed_blocks():
  try:
    get_failed_blocks_sql = "SELECT * FROM bitcoin_failed_blocks"
    cur.execute(get_failed_blocks_sql)
    failed_block_rows = cur.fetchall()

    loaded_error_blocks = list()
    highest_block = 0

    for row in failed_block_rows:
      loaded_error_blocks.append(row[1])
      if (row[1] > highest_block):
        highest_block = row[1]

    return loaded_error_blocks
  except Exception as e:
    return list()


def get_string_formatter(length):
  data_values = ""
  for index in range(length):
    if (index <= length-2):
      data_values += "%s, "
    else:
      data_values += "%s"

  return data_values

#Saves block & stores information about the last block into bitcoin_parser_states table
def commit_lastest_block(hash, index):

  try:
    delete_failed_block_sql = "DELETE FROM bitcoin_failed_blocks WHERE failedBlockHash = %s"
    cur.execute(delete_failed_block_sql, (hash,))
  except:
    raise

  clear_bitcoin_parser_states_sql = "DELETE FROM bitcoin_parser_states"
  cur.execute(clear_bitcoin_parser_states_sql)

  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) VALUES (%s, %s, %s)"
  data = (1, blocks_stored_count, last_block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()


def commit_failed_block(block_hash, index):

  set_last_block_sql = "INSERT INTO bitcoin_failed_blocks (id, blockNum, failedBlockHash) VALUES (%s, %s, %s)"
  data = (1, index, block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()

#Inserts block data into bitcoin_blocks table
def insert_block(block_info, block_index):
  cur.execute("INSERT INTO bitcoin_blocks VALUES (" + get_string_formatter(len(block_info)) + ")", block_info)
  print("Added Block: " + str(block_info[0]))

#Inserts transaction data into bitcoin_transactions table
def insert_transaction(trans_info):
  cur.execute("INSERT INTO bitcoin_transactions VALUES (" + get_string_formatter(len(trans_info)) + ")", trans_info)
  print("Added Trans: " + str(trans_info[0]))

def current_blockchain_length():
  return rpc_connection.batch_([["getblockcount"]])[0]

def parse_block_to_postgresql_database(block_index):

  try:

    commands = [ [ "getblockhash", block_index] ]
    block_hashes = rpc_connection.batch_(commands)
    blocks = rpc_connection.batch_([ [ "getblock", block_hashes[0] ]])
    block = blocks[0]

    block_info = list()

    median_time = block["mediantime"]
    median_time_timestamp = datetime.datetime.fromtimestamp(median_time)

    creation_time = block["time"]
    creation_time_timestamp = datetime.datetime.fromtimestamp(creation_time)

    block_info.append(block["hash"])
    block_info.append(block["merkleroot"])
    block_info.append(block["nonce"])
    block_info.append(block["nonce"])

    if (block_index == 0):
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



    if (block_index >= 1):
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
    insert_block(block_info, block_index)
    commit_lastest_block(block["hash"], block_index)
    return block_index
  except Exception as e:
    print("Error parsing block "+str(block_index)+" : " + str(e))

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

#Initiates block state
block_state = get_last_block_state()
blocks_stored_count = block_state[0]
last_block_hash = block_state[1]
blocks_to_check = get_failed_blocks()

for error_block_num in blocks_to_check:
  if (error_block_num > blocks_stored_count):
    blocks_stored_count = error_block_num

if __name__ == "__main__":

  tryCount = 50
  while True:
    try:
      full_chain_length = current_blockchain_length()
      break
    except Exception as e:
      print("Error getting length: " + str(e))
      tryCount -= 1
      if (tryCount <= 0):
        sys.exit(1)

  commands = [ [ "getblockhash", 0] ]
  block_hashes = rpc_connection.batch_(commands)
  blocks = rpc_connection.batch_([ [ "getblock", block_hashes[0] ]])
  print(blocks[0])

  print("Parsing from block: " + str(blocks_stored_count) + " to " + str(full_chain_length))

  #Loops through bitcoin_blockchain extracting block & transaction info
  while (full_chain_length - blocks_stored_count > 0):

    #Makes sure it doesn't try to parse more blocks than there are
    if ((full_chain_length - blocks_stored_count) < max_blocks_per_cycle):
      blocks_per_cycle = full_chain_length - blocks_stored_count
    else:
      blocks_per_cycle = max_blocks_per_cycle

    print("Blocks to check length: " + str(len(blocks_to_check)))

    for index in range(blocks_stored_count, blocks_stored_count + (blocks_per_cycle - len(blocks_to_check))):
      blocks_to_check.append(index)

    POOL_SIZE = mp.cpu_count() + 2

    while (len(blocks_to_check) > POOL_SIZE):
      with ProcessPool(POOL_SIZE) as pool:
        future = pool.map(parse_block_to_postgresql_database, blocks_to_check, timeout=1)

        try:
          for n in future.result():
              if (n >= 0):
                blocks_to_check.remove(n)
                blocks_stored_count += 1
                print("Blocks stored " + str(blocks_stored_count) + " update at " + str(datetime.datetime.now()))
        except TimeoutError:
          print("TimeoutError: aborting remaining computations")
          future.cancel()

    print("Got through blocks")


#Closes the database & program once complete
cur.close()
conn.close()
sys.exit(1)
