from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import TransactionBuilder, CallTransactionBuilder
from iconsdk.signed_transaction import SignedTransaction
from time import sleep
import unittest

node_uri = "http://localhost:9000/api/v3"
network_id = 3
hello_world_address = "cx3176b5d6cae66a1abbc3ca9070423a5c708834a9"
token_address = "cx9a4c4229ab2cbd61a5cc051fbbb6ee7e3e3adfac"
keystore_path = "./keystore_test1"
keystore_pw = "test1_Account"


class TestGetterMethods(unittest.TestCase):

    def setUp(self):
        self.wallet = KeyWallet.load(keystore_path, keystore_pw)
        self.tester_addr = self.wallet.get_address()
        self.icon_service = IconService(HTTPProvider(node_uri))
 
    def tearDown(self):
        pass 


    def test_name(self):
        call = CallBuilder().from_(self.tester_addr)\
                    .to(hello_world_address)\
                    .method("name")\
                    .build()
        result = self.icon_service.call(call)
        self.assertEqual(result, 'HelloWorld')


    def test_hello(self):
        call = CallBuilder().from_(self.tester_addr)\
                    .to(hello_world_address)\
                    .method("hello")\
                    .build()
        result = self.icon_service.call(call)
        self.assertEqual(result, 'Hello')


    def test_send_token_to_ca(self):
        call = CallBuilder().from_(self.tester_addr)\
                    .to(token_address)\
                    .method("balanceOf")\
                    .params({"_owner": hello_world_address})\
                    .build()
        balance_before = self.icon_service.call(call)
        token_value = "0x1"
        
        transaction = CallTransactionBuilder()\
            .from_(self.tester_addr)\
            .to(token_address)\
            .step_limit(2000000)\
            .nid(network_id)\
            .method("transfer")\
            .params({"_to":hello_world_address, "_value":token_value})\
            .build()

        signed_transaction = SignedTransaction(transaction, self.wallet)
        tx_hash = self.icon_service.send_transaction(signed_transaction)

        sleep(10)

        result = self.icon_service.get_transaction_result(tx_hash)
        self.assertEqual(result['status'], 1)
        self.assertFalse(result['eventLogs'] is None)

        balance_after = self.icon_service.call(call)
        self.assertEqual(int(balance_before,0)+int(token_value,0), int(balance_after,0))


    def test_send_icx_to_ca(self):
        balance_before = self.icon_service.get_balance(hello_world_address)
        icx_value = 1

        transaction = TransactionBuilder()\
            .from_(self.tester_addr)\
            .to(hello_world_address)\
            .value(icx_value)\
            .step_limit(2000000)\
            .nid(network_id)\
            .build()

        signed_transaction = SignedTransaction(transaction, self.wallet)
        tx_hash = self.icon_service.send_transaction(signed_transaction)

        sleep(10)

        result = self.icon_service.get_transaction_result(tx_hash)
        self.assertEqual(result['status'], 1)
        self.assertFalse(result['eventLogs'] is None)

        balance_after = self.icon_service.get_balance(hello_world_address)
        self.assertEqual(balance_before+icx_value, balance_after)


if __name__ == '__main__':
    unittest.main()
