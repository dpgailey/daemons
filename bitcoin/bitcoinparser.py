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



max_blocks_per_cycle = 100

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

  #Updates current block state
  #global last_block_hash
  #last_block_hash = hash

  #global blocks_stored_count
  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, totalBlocks, lastBlockHash) VALUES (%s, %s, %s)"
  data = (1, blocks_stored_count, last_block_hash)

  cur.execute(set_last_block_sql, data)
  conn.commit()
  #global blocks_to_check
  #blocks_to_check.remove(index)
  #print(str(len(blocks_to_check)) + " " + str(index))


def remove_select_block(block_hash, index):

  try:
    #Clears specific has from database
    delete_bitcoin_blocks_sql = "DELETE FROM bitcoin_blocks WHERE hash = %s"
    cur.execute(delete_bitcoin_blocks_sql, (block_hash,))
    delete_bitcoin_transactions_sql = "DELETE FROM bitcoin_transactions WHERE blockHash = %s"
    cur.execute(delete_bitcoin_transactions_sql, (block_hash,))
    delete_bitcoin_parser_states_sql = "DELETE FROM bitcoin_parser_states WHERE lastBlockHash = %s"
    cur.execute(delete_bitcoin_parser_states_sql, (block_hash,))
    print("Block " + str(index) + " removed from database at " + str(datetime.datetime.now()))
  except Exception as e:
    print("Error removing block: " + str(e))



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

  #block_index = block["index"]

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
    #global blocks_to_check
    #blocks_to_check.append(block_index)
    #print("GOT TO REMOVE " + str(len(block)))
    #print("BLOCK DATA " + str(block_index) + " " + str(block["hash"]))
    #print(block["hash"])

    #ADD BACK
    #remove_select_block(block["hash"], block_index)
    return -1


    #DELETE ALL RELATED BLOCK INFO
    #print("Issue committing block: " + str(blocks_stored_count))

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

    #print(range(blocks_stored_count, blocks_stored_count + (blocks_per_cycle - len(blocks_to_check))))

    for index in range(blocks_stored_count, blocks_stored_count + (blocks_per_cycle - len(blocks_to_check))):
      blocks_to_check.append(index)

    '''
    tryCount = 50
    while True:
      try:
        #Gets the current block for parsing from blockchain
        commands = [ [ "getblockhash", block_index] for block_index in blocks_to_check]
        block_hashes = rpc_connection.batch_(commands)
        blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
        print(range(len(blocks)))
        break
      except Exception as e:
        print("Error getting block hashes: " + str(e))
        tryCount -= 1
        if (tryCount <= 0):
          sys.exit(1)'''

    #print(str(len(blocks_to_check)) + " " + str(len(blocks)))

    #blocks_with_trans = list()

    #current_block_hash = rpc_connection.batch_([["getblockhash", 0]])
    #current_blocks = rpc_connection.batch_([["getblock", current_block_hash[0]]])
    #block = current_blocks[0]

    #print(str(len(blocks)) + " " + str(len(blocks_to_check)))

    #for index in range(len(blocks)):
    #  print(str(len(blocks)) + " " + str(index) + " " + str(type(blocks[index])) + " " + str(blocks_to_check[index]))
    #  blocks[index]['index'] = blocks_to_check[index]

    while (len(blocks_to_check) > 0):

      POOL_SIZE = mp.cpu_count() + 2

      if (POOL_SIZE > blocks_to_check):
        POOL_SIZE = len(blocks_to_check)

      with ProcessPool(POOL_SIZE) as pool:
        future = pool.map(parse_block_to_postgresql_database, blocks_to_check, timeout=1)

        try:
          for n in future.result():
              if (n >= 0):
                #print("Result: " + str(n))

                #for block_current in blocks:
                #  if (block_current["index"] == n[0]):
                #    blocks.remove(block_current)

                blocks_to_check.remove(n)
                blocks_stored_count += 1
                last_block_hash = n
                print("Blocks stored " + str(blocks_stored_count) + " update at " + str(datetime.datetime.now()))
                #print("Blocks to check: " + str(len(blocks_to_check)) + " Blocks left: " + str(len(blocks)) + " Block removed: " + str(n[0]))
        except TimeoutError:
          print("TimeoutError: aborting remaining computations")
          future.cancel()

    #pool = ProcessPoolExecutor(POOL_SIZE)

    #future = pool.submit(parse_block_to_postgresql_database, blocks)

    #print(future.done())
    #time.sleep(5)
    #print(future.done())

    #print(future.result())

    #print(blocks_to_remove)
    #NEEDS TO BE REMOVED
    #blocks_stored_count += len(blocks_to_check)
    #blocks_to_check = list()

    #for block in blocks:
    #  parse_block_to_postgresql_database(block)

    #with mp.Pool(POOL_SIZE) as pool:
    #  jobs = [pool.schedule(parse_block_to_postgresql_database, blocks[i], timeout=5) for i in range(len(blocks))]

    #POOL = mp.Pool(POOL_SIZE)
    #POOL.map(parse_block_to_postgresql_database, blocks).get(timeout = 1)
    #POOL.close()
    #POOL = ThreadPool(POOL_SIZE)
    #for block_index in range(len(blocks_to_check)):
    #  POOL.join(parse_block_to_postgresql_database, blocks[block_index], blocks_to_check[block_index])

    #POOL.join()
    #for result in parse_results:
    #  print("RESULT: " + result[0][0])
    #  commit_lastest_block(result[0][0])


    #nums = [0,1,2,3,4,5,6,7,8,9,10]

    #POOL.map(simpleTest, nums)
    print("Got through blocks")
    #POOL.close()


#Closes the database & program once complete
cur.close()
conn.close()
sys.exit(1)
