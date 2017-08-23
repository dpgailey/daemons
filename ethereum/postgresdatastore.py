import datetime
import logging
import psycopg2
import sys

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
            tx_value_sum += int(tx["value"], 0)

        block["transactions"] = transactions
        block["number_int"] = block_number_int
        block["timestamp_int"] = block_timestamp_int
        block["gasLimit_int"] = int(block["gasLimit"], 0)
        block["gasUsed_int"] = int(block["gasUsed"], 0)
        block["size_int"] = int(block["size"], 0)
        block["transactionCount"] = len(transactions)
        block["txValueSum_int"] = tx_value_sum # going to keep this in Wei

        self.blocks.append(block)


    def save(self):
        print(self.blocks)
        sys.exit(0)

        if self.blocks:
            try:
                helpers.bulk(self.d, self.actions)
                return "{} blocks and {} transactions indexed".format(
                    nb_blocks, nb_txs
                )

            except helpers.BulkIndexError as exception:
                print("Issue with {} blocks:\n{}\n".format(blocks, exception))
                for block in blocks:
                    logging.error("block: " + str(block["number"]))


    @staticmethod
    def request(url, **kwargs):
        return Elasticsearch([url]).search(**kwargs)
