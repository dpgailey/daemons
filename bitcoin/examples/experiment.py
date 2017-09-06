import psycopg2
import sys
from blockchain_parser.blockchain import Blockchain

# Instantiate the Blockchain by giving the path to the directory
# containing the .blk files created by bitcoind

def insertTransaction(transactionInfo):
  sql = "INSERT INTO bitcoin_transactions (hash, inputs, outputs, versions, locktime, n_inputs, n_outputs) VALUES (%s, %s, %s, %s, %s, %s, %s)"
  data = (transactionInfo[0],transactionInfo[1],transactionInfo[2],transactionInfo[3],transactionInfo[4],transactionInfo[5],transactionInfo[6])
  cur.execute(sql, data)
  print("Added Trans: " + str(transactionInfo[0]))

conn = psycopg2.connect("dbname=bitcoin_blockchain user=jamie")
cur = conn.cursor()
cur.execute("SELECT * FROM bitcoin_transactions")

blockchain = Blockchain(sys.argv[1])
for block in blockchain.get_unordered_blocks():
  for tx in block.transactions:
    for no, output in enumerate(tx.outputs):
      transactionInfo = [tx.hash, str(tx.inputs), str(tx.outputs), tx._version, tx._locktime, tx.n_inputs, tx.n_outputs]
      insertTransaction(transactionInfo)



cunn.commit()
cur.close()
conn.close()
sys.exit(1)
