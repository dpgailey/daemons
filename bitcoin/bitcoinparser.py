import datetime
import psycopg2
import sys
import requests, json
import multiprocessing as mp
import argparse
import time

from pebble import ProcessPool
from concurrent.futures import TimeoutError
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

#Authentication required to download blockchain
rpc_user = "jamie"
rpc_password = "gabpam24"
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))

#How many blocks we want to parse at once
max_blocks_per_cycle = 1000

#Maximum amount of threads to use based on CPU
max_pool_size = mp.cpu_count() + 2

#Provides a description for the argument system
parser = argparse.ArgumentParser(description='Set up parser to read through blocks on the blockchain')

#Error input for argument system
parser.add_argument("-errors", "--showerrors", dest='show_errors', action="store_true",
                    help="Show erros that occur during parsing.")

#Continious input for argument system
parser.add_argument("-c", "--continuous", dest='continual_parsing', action="store_true",
                    help="Continue to run in foreground, waiting for new blocks.")

#Start block input for argument system
parser.add_argument("-s", "--start", dest='start_block', type=int,
                    help="What block to start indexing. If nothing is provided, the latest block indexed will be used.")

#End block input for argumeent system
parser.add_argument("-e", "--end", dest="end_block", type=int,
                    help="What block to finish indexing. If nothing is provided, the latest one will be used.")

#Sets variables based on arguments provided
args = parser.parse_args()
show_errors = args.show_errors
parse_multiple_blocks = args.continual_parsing
start_block = args.start_block
end_block = args.end_block

#Makes sure it's set to parse multiple blocks when there's no other option
if (start_block is None):
  parse_multiple_blocks = True
if (start_block is not None and end_block is not None):
  parse_multiple_blocks = True

#Loads up the last block state it was on
def get_last_block_state():
  get_last_block_hash_sql = "SELECT * FROM bitcoin_parser_states"
  cur.execute(get_last_block_hash_sql)
  last_block_row = cur.fetchall()

  #Sets up last block state reference
  block_current = last_block_row[0][1]

  print("Succesfully restored block state at block: " + str(last_block_row[0][1]))

  return block_current

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

#Returns a formatted string of %s, %s, %s based on length
def get_string_formatter(length):
  data_values = ""
  for index in range(length):
    if (index <= length-2):
      data_values += "%s, "
    else:
      data_values += "%s"

  return data_values

#Saves block & stores information about the last block into bitcoin_parser_states table
def insert_block_state(hash, index):

  #Deletes failed blocks from bitcoin_failed_blocks
  if (parse_multiple_blocks):
    try:
      delete_failed_block_sql = "DELETE FROM bitcoin_failed_blocks WHERE blockNum = %s"
      cur.execute(delete_failed_block_sql, (index,))
    except:
      raise

  #Deletes bitcoin_parser_states table
  clear_bitcoin_parser_states_sql = "DELETE FROM bitcoin_parser_states"
  cur.execute(clear_bitcoin_parser_states_sql)

  #Inserts parser state into bitcoin_parser_states
  set_last_block_sql = "INSERT INTO bitcoin_parser_states (id, totalBlocks) VALUES (%s, %s)"
  data = (1, block_current)
  cur.execute(set_last_block_sql, data)



#Inserts failed block data into bitcoin_failed_blocks table
def commit_failed_block(index):

  set_last_block_sql = "INSERT INTO bitcoin_failed_blocks (id, blockNum) VALUES (%s, %s)"
  data = (1, index)

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

#Gets the current full blockchain length
def current_blockchain_length():

  block_count = 0

  #Continually attempts to get the full chain length
  tryCount = 50
  while True:
    try:
      block_count = rpc_connection.batch_([["getblockcount"]])[0]
      break
    except Exception as e:
      if (show_errors):
        print("Error getting length: " + str(e))
      tryCount -= 1
      if (tryCount <= 0):
        sys.exit(1)

  return block_count

#Takes in a block based on the index provided
def parse_block_to_postgresql_database(block_index):

  try:

    #Retrieves block from blockchain based on index
    commands = [ [ "getblockhash", block_index] ]
    block_hashes = rpc_connection.batch_(commands)
    blocks = rpc_connection.batch_([ [ "getblock", block_hashes[0] ]])
    block = blocks[0]

    print("Adding block: " + str(block_index))

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

          #Insert transaction info into database
          insert_transaction(trans_info)

    #Commits changes
    insert_block(block_info, block_index)

    if parse_multiple_blocks:
      insert_block_state(block["hash"], block_index)
    return block_index
  except Exception as e:
    if (show_errors):
      print("Error parsing block "+str(block_index)+" : " + str(e))

#Returns how many blocks it's meant to parse
def blocks_to_parse_in_cycle(continual, desired_start, desired_end, block_at, block_chain_length, desired_blocks_per_cycle):
  blocks_to_parse = desired_blocks_per_cycle

  if (desired_end != None):
    blocks_to_parse = desired_end - block_at

  if (desired_start != None and desired_end != None):
    if (blocks_to_parse > (desired_end - block_at)):
      blocks_to_parse = (desired_end - block_at)

  if (block_at > block_chain_length):
    blocks_to_parse = 0

  if ((full_chain_length - block_current) < desired_blocks_per_cycle):
    blocks_to_parse = full_chain_length - block_current

  if (blocks_to_parse > desired_blocks_per_cycle):
    blocks_to_parse = desired_blocks_per_cycle

  if (continual == False and blocks_to_parse > 1):
    blocks_to_parse = 1

  return blocks_to_parse

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

#Initiates block state
if (start_block is not None):
  block_current = start_block
  blocks_to_check = list()
else:
  block_current = get_last_block_state()
  blocks_to_check = get_failed_blocks()


#Sets current block based on the current error blocks
for error_block_num in blocks_to_check:
  if (error_block_num > block_current):
    block_current = error_block_num



#Main method
if __name__ == "__main__":

  #Gets the full chain length
  full_chain_length = current_blockchain_length()

  #Loops through bitcoin_blockchain extracting block & transaction info
  while (blocks_to_parse_in_cycle(parse_multiple_blocks, start_block, end_block, block_current, full_chain_length, max_blocks_per_cycle) > 0):

    #Sets the amount of blocks to parse per cycle
    blocks_per_cycle = blocks_to_parse_in_cycle(parse_multiple_blocks, start_block, end_block, block_current, full_chain_length, max_blocks_per_cycle)
    print ("Block at: " + str(block_current) + " Blocks to parse: " + str(blocks_per_cycle))

    #Adds on the the required block indexes
    for index in range(block_current, block_current + (blocks_per_cycle - len(blocks_to_check))):
      blocks_to_check.append(index)

      #Adds blocks to database for reference incase the program is stopped early
      if parse_multiple_blocks:
        commit_failed_block(index)

    #Loops through the blocks requested for the cycle
    while (len(blocks_to_check) > max_pool_size or (blocks_per_cycle <= max_pool_size and len(blocks_to_check) > 0)):

      if (len(blocks_to_check) < max_blocks_per_cycle):
        pool_size = 1

      with ProcessPool(pool_size) as pool:
        #Adds blocks to multithreading process pool
        future = pool.map(parse_block_to_postgresql_database, blocks_to_check, timeout=1)
        try:
          for n in future.result():
              if (n >= 0):
                blocks_to_check.remove(n)
                print("Blocks stored " + str(block_current) + " update at " + str(datetime.datetime.now()))
                block_current += 1
        except TimeoutError:
          if (show_errors):
            print("TimeoutError: aborting remaining computations")
          future.cancel()


    #Commits changes to Database
    print("Got through parsing cycle")
    conn.commit()

    #Ends cycling if only 1 block was paresed
    if (blocks_per_cycle <= 1):
      break

#Closes the database & program once complete
cur.close()
conn.close()
sys.exit(1)
