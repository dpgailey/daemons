import datetime
import logging
import psycopg2
import sys
import copy
import codecs
import string

from datastore import Datastore

from termcolor import colored, cprint

class PostgresDatastore(Datastore):

    TX_TABLE_NAME = "ethereum_transactions"
    BLK_TABLE_NAME = "ethereum_blocks"

    def __init__(self):
        super().__init__()
        self.db_conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password=self.dbpass)
        self.db_cursor = self.db_conn.cursor()
        #self.update_end_block()

    def update_end_block(self):
        sql = "update ethereum_parser_states set total_blocks = %s where id=1;"
        try:
          self.db_cursor.execute(sql, (self.end_block,))
          print(self.db_cursor.query)
          print(self.db_cursor)
          print("Setting end block to: %s" % self.end_block)
        except Exception as exception:
          print(exception)


    @classmethod
    def config(self, dbuser, dbpass, dbname, dbport, dbhost, start_block, end_block):
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
        self.dbport = dbport
        self.dbhost = dbhost
        self.start_block = start_block
        self.end_block = end_block
        cprint("Connecting to db using dbuser: %s, dbpass: %s, dbname: %s, dbport: %s, dbhost: %s" % (dbuser, dbpass, dbname, dbport, dbhost), 'magenta')

    def extract(self, rpc_block):

      block = rpc_block["result"]
      if block:
        transactions = block["transactions"]
        cprint("Transactions for this block: %s" % (len(transactions),), 'cyan')
        tx_value_sum = 0

        block_number_int = int(block["number"], 0)

        block_timestamp_datetime = datetime.datetime.fromtimestamp(int(block["timestamp"], 0))

        for tx in transactions:
          tx["blockNumber_int"] = block_number_int
          tx["blockTimestamp"] = block_timestamp_datetime
          tx["blockTimestamp_int"] = block_timestamp_datetime
          # Convert wei into ether
          tx["value_eth"] = int(tx["value"], 0) / self.WEI_ETH_FACTOR
          tx["value_int"] = int(tx["value"], 0)
          tx["gasPrice_int"] = int(tx["gasPrice"], 0)
          tx["gas_int"] = int(tx["gas"], 0)
          tx["input_str"] = self.hex_to_ascii(tx["input"])
          tx["transactionIndex_int"] = int(tx["transactionIndex"], 0)
          tx["txhash"] = tx["hash"]
          tx.pop('hash', 0)
          tx_value_sum += int(tx["value"], 0)

        block["transactions"] = transactions
        block["number_int"] = block_number_int
        block["difficulty_int"] = int(block["difficulty"], 0)
        block["extraData_str"] = self.hex_to_ascii(block["extraData"])
        block["timestamp"] = block_timestamp_datetime
        block["timestamp_int"] = block_timestamp_datetime
        block["gasLimit_int"] = int(block["gasLimit"], 0)
        block["gasUsed_int"] = int(block["gasUsed"], 0)
        block["size_int"] = int(block["size"], 0)
        block["transactionCount"] = len(transactions)
        block["txValueSum_int"] = tx_value_sum # going to keep this in Wei
        block["totalDifficulty_int"] = int(block["totalDifficulty"], 0)
        block["blockhash"] = block["hash"]
        block.pop('hash', 0)

        block["uncles"] = ''

        self.blocks.append(block)
      else:
        cprint("Block doesn't exist, problem: %s" % rpc_block, 'black', 'on_red')

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
                block_check_sql = 'select blockhash from ethereum_blocks where blockhash = %s'
                dbcurs.execute(block_check_sql, (block['blockhash'],))
                if dbcurs.fetchone() == None:

                  block_insert = 'insert into ethereum_blocks (%s) values %s'
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
                  tx_check_sql = 'select txhash from ethereum_transactions where txhash = %s and blockHash = %s;'
                  dbcurs.execute(tx_check_sql, (tx['txhash'], tx['blockHash'],))

                  if dbcurs.fetchone() == None:
                    tx_insert = 'insert into ethereum_transactions (%s) values %s'
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

              old_sql = "select highest_block_number from ethereum_parser_states where id=1"
              dbcurs.execute(old_sql)
              res = dbcurs.fetchone()

              cprint("Current block: %s" % block['number_int'], 'green')

              if( block['number_int'] > res[0]):
                update_sql = "update ethereum_parser_states set highest_block_number = %s"
                dbcurs.execute(update_sql, (block['number_int'], ))

                cprint("Updated Highest block number w/: %s" % dbcurs.statusmessage, 'green')
                update_sql = "update ethereum_parser_states set last_block_number = %s where id = 1"
                dbcurs.execute(update_sql, (block['number_int'],))
              else:
                cprint("Current block less than highest block, not updating states.", 'yellow')


      #except Exception as exception:
      #  for block in self.blocks:
      #      logging.error("block: " + str(block["number"]))

    def hex_to_ascii(self, hex):
      if hex == "0x":
        return ''
      else:
        # not sure if this should be UTF-8
        return codecs.encode(codecs.decode(codecs.decode(str.replace(hex, '0x', ''), "hex"), "ascii", "ignore"), "ascii", "ignore")

    @staticmethod
    def request(url, **kwargs):
        return Elasticsearch([url]).search(**kwargs)
