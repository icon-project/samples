# Hello World

The simplest yet completely legitimate SCORE that returns "Hello" in the response message. 

```python
from iconservice import *

class HelloWorld(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        return "Hello"
```

 

We will add a little tweak to our HelloWorld.  

- Give it a name, "HelloWorld"
- Print logs. 
- Allow it to accept ICX and other tokens.

```python
from iconservice import *

TAG = 'HelloWorld'

class HelloWorld(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
    
    @external(readonly=True)
    def name(self) -> str:
        return "HelloWorld"

    @external(readonly=True)
    def hello(self) -> str:
        Logger.info(f'Hello, world!', TAG)
        return "Hello"

    @payable
    def fallback(self) -> None:
        Logger.info(f'fallback is called', TAG)
        pass

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        Logger.info(f'tokenFallabck is called', TAG)
        pass
```

`fallback` function is added to accept ICX. `fallback` function is executed when the contract receives a transaction request without `data` part. Not having `data` in the transaction request means no method name is specified. In such case, `fallback` function is invoked if the function is provided. If `fallback` function is not given, the transaction will fail. Only functions with `@payable` decorator are permitted to receive ICX coins, therefore, our `fallback` function should be also  `@payable`.  You don't need to implement anything in the fallback function to handle the ICX transfer. Having payable fallback function declares that the contract accepts ICX coin transfer. 

`tokenFallback` method is added to accept IRC2 tokens. The [IRC2](https://github.com/icon-project/IIPs/blob/master/IIPS/iip-2.md#token-fallback) standard mandates the `tokenFallback` method in the receiving SCORE.  Token contact will call the `tokenFallback` funtion whenever it transfers  token to a contract address.



## GitHub

Please refer to [Github](https://github.com/icon-project/samples/) for complete source code.

### Invoke a method from CLI

Below is the T-Bears CLI comand to invoke the SCORE's external read-only method. Before issuing the command, don't forget to change the "to" value in the JSON request with an actual SCORE address. 

```bash
root@07dfee84208e:/tbears# cat call.json 
{
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 1,
    "params": {
        "to": "cx3176b5d6cae66a1abbc3ca9070423a5c708834a9", 
        "dataType": "call",
        "data": {
            "method": "hello"
        }
    }
}
root@07dfee84208e:/tbears# tbears call call.json 
response : {
    "jsonrpc": "2.0",
    "result": "Hello",
    "id": 1
}
```

### Run test

- Testcase uses python sdk. You need to install python sdk to run the test.

```bash
$ pip3 install iconsdk
```

- Go to the `test` folder, open `test.py`, and change the variables.

```bash
$ ls hello_world
hello_world.py  __init__.py  package.json  README.md  test

$ cd hello_world/test
$ ls 
keystore_test1	test.py
```

Use the actual SCORE addresses. We need `standard_token` contract to test token transfer. If you test on T-Bears, use the default `node_uri`. If test on other network, change the `node_uri` and `network_id` accordingly. 


```python
node_uri = "http://localhost:9000/api/v3"
network_id = 3
hello_world_address = "cx3176b5d6cae66a1abbc3ca9070423a5c708834a9"
token_address = "cx9a4c4229ab2cbd61a5cc051fbbb6ee7e3e3adfac"
keystore_path = "./keystore_test1"
keystore_pw = "test1_Account"
```

- Run the test.

```bash
$ python3 test.py
........
----------------------------------------------------------------------
Ran 8 tests in 16.702s

OK
```