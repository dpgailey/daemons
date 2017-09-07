# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind

import datetime
import psycopg2
import sys

from blockchain_parser.blockchain import Blockchain

from datastore import Datastore

#Inserts block data into bitcoin_blocks table
def insertBlock(blockInfo):
  sql = "INSERT INTO bitcoin_blocks (hash, hex, size, height, version, previous_block_hash, merkle_root, creation_time, bits, nonce, difficulty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  data = (blockInfo[0],blockInfo[1],blockInfo[2],blockInfo[3],blockInfo[4],blockInfo[5],blockInfo[6],blockInfo[7],blockInfo[8],blockInfo[9],blockInfo[10])
  cur.execute(sql, data)
  print("Added Block: " + str(blockInfo[0]))

#Inserts transaction data into bitcoin_transactions table
def insertTransaction(transactionInfo):
  sql = "INSERT INTO bitcoin_transactions (hash, inputs, outputs, versions, locktime, n_inputs, n_outputs) VALUES (%s, %s, %s, %s, %s, %s, %s)"
  data = (transactionInfo[0],transactionInfo[1],transactionInfo[2],transactionInfo[3],transactionInfo[4],transactionInfo[5],transactionInfo[6])
  cur.execute(sql, data)
  print("Added Trans: " + str(transactionInfo[0]))

#Saves block & stores information about the last block into bitcoin_parser_states table
def save(self):
  if not self.blocks:
    cprint("No blocks found!", 'black', 'on_red')
    return True
  else:
    for block in self.blocks:
      just_block = copy.deepcopy(block)
      del just_block["transactions"]
      transactions = block["transactions"]

      with self.db_conn:
        with self.db_conn.cursor() as dbcurs:
          # if block present skip
          try:
            block_check_sql = 'select blockhash from bitcoin_blocks where blockhash = %s'
            dbcurs.execute(block_check_sql, (block['blockhash'],))
            if dbcurs.fetchone() == None:

              block_insert = 'insert into bitcoin_blocks (%s) values %s'
              l = [(c, v) for c, v in just_block.items()]
              block_columns = ','.join([t[0] for t in l]).split(",")
              block_columns = ', '.join(['"{}"'.format(value) for value in block_columns]).lower()

              block_values = tuple([t[1] for t in l])

              block_sql = self.db_cursor.mogrify(block_insert, ([psycopg2.extensions.AsIs(block_columns)] + [block_values]))
              cprint("Write block %s" % block['number_int'], 'green')

              dbcurs.execute(block_sql)
            else:
              cprint("Block already present. Skipping block: %s" % block['blockhash'], 'yellow')
          except Exception as exception:
            cprint("Block Exception", 'black', 'on_red')
            cprint(exception, 'black', 'on_red')

          for tx in transactions:
            # check to see if TX exists
            try:
              tx_check_sql = 'select txhash from bitcoin_transactions where txhash = %s and blockHash = %s;'
              dbcurs.execute(tx_check_sql, (tx['txhash'], tx['blockHash'],))

              if dbcurs.fetchone() == None:
                tx_insert = 'insert into bitcoin_transactions (%s) values %s'
                l = [(c, v) for c, v in tx.items()]
                tx_columns = ','.join([t[0] for t in l]).split(",")

                tx_columns = ', '.join(['"{}"'.format(value) for value in tx_columns]).lower()
                tx_values = tuple([t[1] for t in l])

                tx_sql = self.db_cursor.mogrify(tx_insert, ([psycopg2.extensions.AsIs(tx_columns)] + [tx_values]))
                dbcurs.execute(tx_sql)
                cprint("- Write tx %s" % tx['txhash'], 'green')
              else:
                cprint("Transaction already present. Skipping tx: %s" % tx['txhash'], 'yellow')
            except Exception as exception:
              cprint("Transaction Exception", 'black', 'on_red')
              cprint(exception, 'black', 'on_red')

          old_sql = "select highest_block_number from bitcoin_parser_states where id=1"
          dbcurs.execute(old_sql)
          res = dbcurs.fetchone()

          cprint("Current block: %s" % block['number_int'], 'green')

#Connects to the database
conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()

#Creates blockchain from blocks folder submited in argument
blockchain = Blockchain(sys.argv[1])

#Loops through bitcoin_blockchain extracting block & transaction info
for block in blockchain.get_unordered_blocks():

  print("Block's origional creation time: " + header.timestamp)

  #Compiles block & header data for storage
  header = block.header
  blockInfo = [block.hash, str(header.from_hex), block.size, block.height,
  header.version, header.previous_block_hash, header.merkle_root,
  header.timestamp, header.bits, header.nonce, header.difficulty]
  insertBlock(blockInfo)

  #Loops through transactions, compiles data for storage
  for tx in block.transactions:
    for no, output in enumerate(tx.outputs):
      transactionInfo = [tx.hash, str(tx.inputs), str(tx.outputs),
      tx._version, tx._locktime, tx.n_inputs, tx.n_outputs]
      insertTransaction(transactionInfo)


#Commits changes and closes the database & program
cunn.commit()
cur.close()
conn.close()
sys.exit(1)
