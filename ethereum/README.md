# Daemons::Ethereum
-

Useful links: 

* https://medium.com/@pipermerriam/the-python-ethereum-ecosystem-101bd9ba4de7

-

Schema
-
Notes: 

1. Practicially everything in the Ethereum blockchain is a HEX value
2. All fields have an \_int suffix for their integer representations where applicable
3. Blockchain block output: https://gist.github.com/dpgailey/bbbc388128d240f573328c9df1e72630
4. Ethereum Yellow paper detailing each piece: : https://ethereum.github.io/yellowpaper/paper.pdf

# Blocks

*  difficulty
*  extraData
*  gasLimit
*  gasUsed
*  hash
*  logsBloom
*  miner
*  mixHash
*  nonce
*  number
*  parentHash
*  receiptsRoot
*  sha3Uncles
*  size
*  stateRoot
*  timestamp
*  totalDifficult

# Transactions

*  blockHash
*  blockNumber
*  from
*  gas
*  gasPrice
*  hash
*  input
*  nonce
*  to
*  transactionIndex
*  value
*  v
*  r
*  s

-

# Ethereum Block


```javascript
{
    'jsonrpc': '2.0',
    'id': 1,
    'result': {
        'difficulty': '0x224ce0dbcfa57',
        'extraData': '0xd58301050b8650617269747986312e31352e31826c69',
        'gasLimit': '0x47d5de',
        'gasUsed': '0x27f81',
        'hash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
        'logsBloom': '0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        'miner': '0xa42af2c70d316684e57aefcc6e393fecb1c7e84e',
        'mixHash': '0xb56648c7ed3bdf9876cd5b6e08f480b1d9b9e382a61e0a8a4ed09f6d6c08229a',
        'nonce': '0x0761ee400e196275',
        'number': '0x3a4c54',
        'parentHash': '0xcc88be60059b8daf6e108c1f32335b5ff05f0a8857a50ba18ab8704f88c8266f',
        'receiptsRoot': '0x828ac69abffa08a9a16f7743e0824a8970b548c15825767ffb9ffd92566510ea',
        'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
        'size': '0x58b',
        'stateRoot': '0x00a4d4fad3b819ade03ad3d24cc353e499677e4a9804b9fe163bcb8bb724fbc6',
        'timestamp': '0x59346324',
        'totalDifficulty': '0x1140e6084bb27cfd5b',
        'transactions': [{
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x9dc52ed219fea338707c4047518a2ca6182f30d0',
            'gas': '0x186a0',
            'gasPrice': '0x174876e800',
            'hash': '0x22fcb1fac099d30cbdef9f40a5d47aff3a29a88a757233579a1c28531be81090',
            'input': '0x0f2c9329000000000000000000000000167a9333bf582556f35bd4d16a7e80e191aa6476000000000000000000000000571b7b69829ce2568b9bc3d32eaf7405dab76b21',
            'nonce': '0x2',
            'to': '0xabbb6bebfa05aa13e908eaa492bd7a8343760477',
            'transactionIndex': '0x0',
            'value': '0x6e36737083d8c00',
            'v': '0x26',
            'r': '0xeeb98ef35eaf3239916f5460872cdf14f875b1f301dd540969a4287fe12ef874',
            's': '0x2dfbc272b421918ab48471ece73ce3dc6be7edfe831a0c274706f8325c7895c'
        }, {
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x4a3828f90334038c37fe75746808ccb7cfd52bc0',
            'gas': '0x186a0',
            'gasPrice': '0x174876e800',
            'hash': '0xaa3e1ba90d787760ef2adfd4931c4fe63ddf6ba60e94bc0ca0ee721efd4a6723',
            'input': '0x0f2c9329000000000000000000000000167a9333bf582556f35bd4d16a7e80e191aa6476000000000000000000000000571b7b69829ce2568b9bc3d32eaf7405dab76b21',
            'nonce': '0xa',
            'to': '0xabbb6bebfa05aa13e908eaa492bd7a8343760477',
            'transactionIndex': '0x1',
            'value': '0xdd31c27d614c800',
            'v': '0x25',
            'r': '0xad8d90a03adf4005107b5f27cbd99a2463b16e4c7c5f3ad9d4f24e45e91a78fa',
            's': '0x4abc399681c1c7a6b3296a54aa677735911519e3e1d0c28d8865072bfc710b19'
        }, {
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x71386e2ae795377a27564b4585aa4e4241e58078',
            'gas': '0x186a0',
            'gasPrice': '0x174876e800',
            'hash': '0xad02ddd6c106af45f0824b59699d8552f3a43459865d1715fb425b82ae7eb1b0',
            'input': '0x0f2c9329000000000000000000000000167a9333bf582556f35bd4d16a7e80e191aa6476000000000000000000000000571b7b69829ce2568b9bc3d32eaf7405dab76b21',
            'nonce': '0x4',
            'to': '0xabbb6bebfa05aa13e908eaa492bd7a8343760477',
            'transactionIndex': '0x2',
            'value': '0x89b7bfcf11168000',
            'v': '0x25',
            'r': '0x212f8584e3a9325d7f03f99ea34d5a22f01333e841a46678f00f68ffd8b7b67a',
            's': '0x23eda4ccae5d5aac2759b620ae586814256c65a333ad4e20e97bd72878204bd3'
        }, {
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x24f21c22f0e641e2371f04a7bb8d713f89f53550',
            'gas': '0x5208',
            'gasPrice': '0xba43b7400',
            'hash': '0x509b9f5efaaf200aa587a09d1a9b288db389b98ecfc2714e1ca948ea939cd9a6',
            'input': '0x',
            'nonce': '0x27e6',
            'to': '0x7e2e523f1f2c0f381e4555750c9d4de55ba8d228',
            'transactionIndex': '0x3',
            'value': '0x6161ac5ab4c8400',
            'v': '0x26',
            'r': '0x214f48209fc9e432adc6a0565cd6b6bb81323c0f1622a4d12da9178fe352f46d',
            's': '0x4b5063ea6ebcd6b2ca62643f83cce93c562ed72ac0d169da74c22180f5fc2457'
        }, {
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x7ed1e469fcb3ee19c0366d829e291451be638e59',
            'gas': '0x5208',
            'gasPrice': '0x9502f9000',
            'hash': '0xb251416a3346443afd7e75b6e2300e2ce0c83ee47ab0e3764b89b2db55496e4b',
            'input': '0x',
            'nonce': '0xb2fb',
            'to': '0xa12187e492bc7e17487a64bdac98bd97dde275a2',
            'transactionIndex': '0x4',
            'value': '0x1f9e80ba804000',
            'v': '0x25',
            'r': '0x850fa556b60d8dcfc6c55a5bc4fe6f499ef5f7813a74c8670ed310ae76848107',
            's': '0x753fda77888f01f046ce3bbf8e77f2c78327a94200f4e5628eed65ced3bb429f'
        }, {
            'blockHash': '0xd902709da71aee42aa5432e28e8b7148d1316dae6ecbec7ca7a34041c3e32806',
            'blockNumber': '0x3a4c54',
            'from': '0x24f21c22f0e641e2371f04a7bb8d713f89f53550',
            'gas': '0x5208',
            'gasPrice': '0xba43b7400',
            'hash': '0xb68afc2b44f0e65d8561d602782c76d8f72bd900b073fc39adaa5afdacf1fe97',
            'input': '0x',
            'nonce': '0x27e7',
            'to': '0x105f18004b8f7be31bccb489776626e9b953f13f',
            'transactionIndex': '0x5',
            'value': '0x9fdf42f6e48000',
            'v': '0x26',
            'r': '0x506c8b0edfae001026b5929536fd91b571da7d30fb816f5986f1d32cc20b960a',
            's': '0x1ad10d0c6c6e44e34e939068ed44cc5264c9b16d6db08e8cea9a0233c4dba958'
        }],
        'transactionsRoot': '0x3e3c4e29f0274fe1c98a447da8aaf0a91bdc559b60f79d00b1afaead539187eb',
        'uncles': []
    }
}
```