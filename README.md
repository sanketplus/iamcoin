# IAMCOIN :D

The coin wanted to call itself `iamcoin` :D

Core component used here is `aiohttp` which provides HTTP api and WebSocket P2P connectivity. A block is mined every 10 minutes or when there are 10 transaction in pool (configurable). Reward for mining block is 100 coins.

## HTTP API

**Add peer**
```bash
curl localhost:5000/addpeer -X POST --data "peer=http://example.com:5000/ws"
```

**Get block count**
```bash
curl localhost:5000/blockcount
```

**List Peers**
```bash
curl localhost:5000/peers 
```

**List Transactions in Transaction pool**
```bash
curl localhost:5000/txpool
```

**Get Balance**
```bash
curl localhost:5000/balance 
```

**Send transaction in Transaction pool*
```bash
curl localhost:5000/sendtransaction --data '{"address":"8007305ba6672e4ce558d7502c904bce9b3a8263f2a66e3a79d6877b2c52c8a848601a43bd3f884b1b209cd3ca124daa","amount":30}' 
```

**mine block which will include all tx from pool**
```bash

```