# IAMCOIN :D

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

**Mine first block with coinbase transaction**
```bash
curl -H "Content-type:application/json" http://localhost:5000/mineblock --data '{"data":[{"txins":[{"signature":"","txout_id":"","txout_index":1}],"txouts":[{"address":"04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a","amount":100}],"id":"e957edadfe2e987843650a4ee98fa721c97e29148cdccc28bda7f33c26c3dd09"}]}'
```