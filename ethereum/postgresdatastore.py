import datetime
import logging
import psycopg2
import sys
import copy

from datastore import Datastore


class PostgresDatastore(Datastore):

    TX_TABLE_NAME = "ethereum-transaction"
    BLK_TABLE_NAME = "ethereum-block"

    def __init__(self):
        super().__init__()
        self.db_conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password=self.dbpass)
        self.db_cursor = self.db_conn.cursor()

    @classmethod
    def config(self, dbuser, dbpass, dbname, dbport, dbhost):
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
        self.dbport = dbport
        self.dbhost = dbhost

    def extract(self, rpc_block):

      block = rpc_block["result"]

      transactions = block["transactions"]
      tx_value_sum = 0

      block_number_int = int(block["number"], 0)

      block_timestamp_int = datetime.datetime.fromtimestamp(int(block["timestamp"], 0))

      for tx in transactions:
        tx["blockNumber_int"] = block_number_int
        tx["blockTimestamp_int"] = block_timestamp_int
        # Convert wei into ether
        tx["value_eth"] = int(tx["value"], 0) / self.WEI_ETH_FACTOR
        tx["value_int"] = int(tx["value"], 0)
        tx["gasPrice_int"] = int(tx["gasPrice"], 0)
        tx["gas_int"] = int(tx["gas"], 0)
        tx["input_str"] = str(tx["input"])
        tx["transactionIndex_int"] = int(tx["transactionIndex"], 0)
        tx_value_sum += int(tx["value"], 0)

      block["transactions"] = transactions
      block["number_int"] = block_number_int
      block["difficulty_int"] = int(block["difficulty"], 0)
      block["extraData_str"] = str(block["extraData"])
      block["timestamp_int"] = block_timestamp_int
      block["gasLimit_int"] = int(block["gasLimit"], 0)
      block["gasUsed_int"] = int(block["gasUsed"], 0)
      block["size_int"] = int(block["size"], 0)
      block["transactionCount"] = len(transactions)
      block["txValueSum_int"] = tx_value_sum # going to keep this in Wei
      block["totalDifficulty_int"] = int(block["totalDifficulty"], 0)

      self.blocks.append(block)


    def save(self):

      if self.blocks:
        try:
          for block in self.blocks:
            just_block = copy.deepcopy(block)
            del just_block["transactions"]
            transactions = block["transactions"]

            with self.db_conn:
              with self.db_conn.cursor() as dbcurs:
                # if block present skip

                block_check_sql = 'select hash from ethereum_blocks where hash = %s'
                dbcurs.execute(block_check_sql, (block['hash'],))
                if dbcurs.fetchone() == None:

                  block_insert = 'insert into ethereum_blocks (%s) values %s'
                  l = [(c, v) for c, v in just_block.items()]
                  block_columns = ','.join([t[0] for t in l])
                  block_values = tuple([t[1] for t in l])

                  block_sql = self.db_cursor.mogrify(block_insert, ([psycopg2.extensions.AsIs(block_columns)] + [block_values]))

                  dbcurs.execute(block_sql)

                for tx in transactions:
                  # check to see if TX exists
                  tx_check_sql = 'select hash from ethereum_transactions where hash = %s and blockHash = %s;'
                  dbcurs.execute(tx_check_sql, (tx['hash'], tx['blockHash'],))

                  if dbcurs.fetchone() == None:
                    tx_insert = 'insert into ethereum_transactions (%s) values %s'
                    l = [(c, v) for c, v in transaction.items()]
                    tx_columns = ','.join([t[0] for t in l])
                    tx_values = tuple([t[1] for t in l])

                    tx_sql = self.db_cursor.mogrify(tx_insert, ([psycopg2.extensions.AsIs(tx_columns)] + [tx_values]))
                    dbcurs.execute(tx_sql)
                # Update state
                update_sql = "update ethereum_parser_state where id=1 set (last_blockNumber) values (%s)"
                dbcurs.execute(update_sql, (block['blockNumber_int'],))

          #return "{} blocks and {} transactions indexed".format(
          #)

        except Exception as exception:
          print("Issue with {} blocks:\n{}\n".format(self.blocks, exception))
          for block in self.blocks:
              logging.error("block: " + str(block["number"]))


    @staticmethod
    def request(url, **kwargs):
        return Elasticsearch([url]).search(**kwargs)
