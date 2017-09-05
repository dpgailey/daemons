import psycopg2
import sys
from blockchain_parser.blockchain import Blockchain

# Instantiate the Blockchain by giving the path to the directory 
# containing the .blk files created by bitcoind

def insertRow(transactionInfo):
  sql = "INSERT INTO bitcoin_transactions (id, hex) VALUES (%s, %s)"
  data = (transactionInfo[0],transactionInfo[1])
  cur.execute(sql, data)
  print("Added Trans: " + str(transactionInfo[0]) + " " + transactionInfo[1])

conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()
cur.execute("CREATE TABLE bitcoin_transactions (id serial PRIMARY KEY, hex varchar)")

index = 0

blockchain = Blockchain(sys.argv[1])
for block in blockchain.get_unordered_blocks():
  for tx in block.transactions:
    for no, output in enumerate(tx.outputs):
      blockInfo = [index, tx.hash]
      insertRow(blockInfo)
      index+=1


  
cunn.commit()
cur.close()
conn.close()
sys.exit(1)
