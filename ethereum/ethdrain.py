#!/usr/bin/python3
import asyncio
import json
import logging
import multiprocessing as mp
import argparse
import requests
import aiohttp
import sys
import time

from termcolor import colored, cprint

#from elasticsearch import exceptions as es_exceptions
#from elasticdatastore import ElasticDatastore

from postgresdatastore import PostgresDatastore

logging.basicConfig(filename='error_blocks.log', level=logging.ERROR)

class Ethdrain:

    # Holds the list of datastore classes
    data_store_classes = ()

    eth_url = "http://localhost:8545"
    sem_size = 256

    def __init__(self, block_range):
        self.block_range = block_range
        self.data_stores = list()

    @classmethod
    def load_datastore_classes(cls, *data_store_classes):
        cls.data_store_classes = data_store_classes

    @classmethod
    def launch(cls, block_range):
        """
        This class method will instanciate Ethdrain classes (one per process)
        and then instanciate and attach every datastore available to each on them
        """
        inst = cls(block_range)
        for data_class in cls.data_store_classes:
            inst.data_stores.append(data_class())
        inst.setup_process()


    def setup_process(self):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.run(self.block_range))
        loop.run_until_complete(future)

        # Now that everything has been "extracted", perform the "save" action
        for data_store in self.data_stores:
            msg = data_store.save()
            cprint("Save action results {}: {}".format(data_store.__class__.__name__, msg), 'cyan')


    async def fetch(self, session, block_nb):
        try:
            async with session.post(self.__class__.eth_url,
                                    data=Ethdrain.make_request(block_nb),
                                    headers={"content-type": "application/json"}) as response:
                for data_store in self.data_stores:
                    data_store.extract(await response.json())
        except (aiohttp.ClientError, asyncio.TimeoutError) as exception:
            logging.error("block: " + str(block_nb))
            cprint("Issue with block {}:\n{}\n".format(block_nb, exception), 'black', 'on_red')


    async def sema_fetch(self, sem, session, block_nb):
        async with sem:
            await self.fetch(session, block_nb)


    async def run(self, block_range):
        tasks = []
        sem = asyncio.Semaphore(self.__class__.sem_size)

        # Create client session that will ensure we dont open new connection
        # per each request.
        async with aiohttp.ClientSession() as session:
            for block_nb in block_range:
                # pass Semaphore and session to every POST request
                task = asyncio.ensure_future(self.sema_fetch(sem, session, block_nb))
                tasks.append(task)

            await asyncio.gather(*tasks)


    @staticmethod
    def make_request(block_nb, use_hex=True):
        return json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [hex(block_nb) if use_hex else block_nb, True],
            "id": 1
        })


if __name__ == "__main__":

    def http_post_request(url, request):
        return requests.post(url, data=request, headers={"content-type": "application/json"}).json()


    def chunks(lst, nb_chunks=250):
        for i in range(0, len(lst), nb_chunks):
            yield lst[i:i + nb_chunks]


    # Elasticsearch maximum number of connections
    ES_MAXSIZE = 25
    # Database default url
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASS = "postgres"
    DB_NAME = "postgres"

    # Ethereum (geth) RPC endpoint
    # initialized with: `geth --rpc`
    # for more info see: https://github.com/ethereum/wiki/wiki/JSON-RPC
    ETH_URL = "http://localhost:8545"

    # Size of multiprocessing Pool processing the chunks
    POOL_SIZE = mp.cpu_count() + 2

    # Guessing this is wait time in seconds to recv response from RPC server
    BLOCK_WAIT = 10

    # Time to wait between checks for new blocks
    TIME_TO_WAIT = 0


    # SKVL
    with open("skvl.txt", "r") as your_file:
      skvl = your_file.read()
    cprint(skvl, 'green')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', dest='start_block', type=int,
                        help='What block to start indexing. If nothing is provided, the latest block indexed will be used.')
    parser.add_argument('-e', '--end', dest='end_block', type=int,
                        help='What block to finish indexing. If nothing is provided, the latest one will be used.')
    parser.add_argument('-f', '--file', default=None,
                        help='Use an input file, each block number on a new line.')

    parser.add_argument('-m', '--esmaxsize', default=ES_MAXSIZE,
                        help='The elasticsearch max chunk size.')

    parser.add_argument('-r', '--ethrpcurl', default=ETH_URL,
                        help='The Ethereum RPC node url and port.')

    parser.add_argument('--continuous', action="store_true",
                        help='Continue to run in foreground, waiting for new blocks.')

    parser.add_argument('--last', action="store_true",
                        help='Prints the last block number and exits.')

    # Adds for postgres

    parser.add_argument('-u', '--dbuser', default=DB_USER,
                        help='The database user.')

    parser.add_argument('-p', '--dbpass', default=DB_PASS,
                        help='The database password.')

    parser.add_argument('-d', '--dbname', default=DB_NAME,
                        help='The database name.')

    parser.add_argument('-o', '--dbport', default=DB_PORT,
                        help='The database port.')

    parser.add_argument('-l', '--dbhost', default=DB_HOST,
                        help='The database host')

    parser.add_argument('-b', '--blockfill', action="store_true",
                        help='Start checking and filling blocks')

    args = parser.parse_args()

    # Setup all datastores
    PostgresDatastore.config(args.dbuser, args.dbpass, args.dbname, args.dbport, args.dbhost, args.start_block, args.end_block)
    db = PostgresDatastore()

    Ethdrain.eth_url = args.ethrpcurl
    Ethdrain.load_datastore_classes(PostgresDatastore)


    # This checks for contiguous blocks
    if args.blockfill:
      # start fill from a particular point
      cprint("Beginning Block Fill!", 'magenta')
      start_block = args.start_block
      while True:
        db.db_cursor.execute('select number_int from ethereum_blocks where number_int = %s', (start_block,))
        res = db.db_cursor.fetchone()
        if res == None:
          cprint("Missing block, fetching: %s" % (start_block,), 'black', 'on_magenta')
          BLOCK_LIST = [[start_block,],]
          POOL = mp.Pool(POOL_SIZE)
          POOL.map(Ethdrain.launch, BLOCK_LIST)
          POOL.close()

          db.db_cursor.execute('update ethereum_parser_states set last_block_checked=%s where id=1', (start_block,))
        else:
          cprint("Block found, skipping: %s" % res[0], 'green')
          start_block = start_block + 1
      cprint("Finishing checking! All set!", 'green')
      sys.exit(1)


    #if args.transaction_check:

    # Determine start block number if needed
    if not args.start_block:
      cprint("No start block found. Using highest_last_block", 'yellow')
      db.db_cursor.execute('select highest_block_number from ethereum_parser_states where id=1')
      res = db.db_cursor.fetchone()
      try:
        args.start_block = res[0] #ElasticDatastore.request(args.esurl, index=ElasticDatastore.B_INDEX_NAME, size=1, sort="number:desc")["hits"]["hits"][0]["_source"]["number"]
      except (es_exceptions.NotFoundError, es_exceptions.RequestError):
        args.start_block = 0
      cprint("Start block automatically set to: {}".format(args.start_block), 'cyan')

    # Determine last block number if needed
    if not args.end_block:
        args.end_block = int(http_post_request(ETH_URL,
                                               Ethdrain.make_request("latest", False))["result"]["number"], 0) - BLOCK_WAIT
        cprint("Last block automatically set to: {}".format(args.end_block), 'cyan')

    # Only print out last block and exit
    if args.last:
      sys.exit(1)

    if not args.continuous:
      if args.file:
          with open(args.file) as f:
              CONTENT = f.readlines()
              BLOCK_LIST = [int(x) for x in CONTENT if x.strip() and len(x.strip()) <= 8]
      else:
          BLOCK_LIST = list(range(int(args.start_block), int(args.end_block)))

      CHUNKS_ARR = list(chunks(BLOCK_LIST))

      cprint("Processing {} blocks split into {} chunks on {} processes:".format(
          len(BLOCK_LIST), len(CHUNKS_ARR), POOL_SIZE
      ), 'cyan')

      POOL = mp.Pool(POOL_SIZE)
      POOL.map(Ethdrain.launch, CHUNKS_ARR)

    else:
      start_block = int(args.start_block)
      while True:
        BLOCK_LIST = [[start_block,],]
        CHUNKS_ARR = list(BLOCK_LIST)

        cprint("Processing {} blocks split into {} chunks on {} processes:".format(
            len(BLOCK_LIST), len(CHUNKS_ARR), 1
        ), 'cyan')
        POOL = mp.Pool(POOL_SIZE)
        POOL.map(Ethdrain.launch, BLOCK_LIST)
        POOL.close()

        start_block = start_block + 1
        cprint("Next block automatically set to: {}".format(start_block), 'cyan')

        db.db_cursor.execute('select last_block_number, highest_block_number from ethereum_parser_states where id=1')
        res = db.db_cursor.fetchone()
        # Time between checks
        latest_block = int(http_post_request(ETH_URL,
                                             Ethdrain.make_request("latest", False))["result"]["number"], 0) - BLOCK_WAIT
        if latest_block < start_block:
          start_block = start_block - 1
          cprint("Ran out of blocks to parse. Sleeping for a little bit.", 'yellow')
          time.sleep(60*1)
        else:
          time.sleep(TIME_TO_WAIT)
