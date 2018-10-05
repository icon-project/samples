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


    def test_token_balanceOf_eoa(self):
        call = CallBuilder().from_(self.tester_addr)\
                    .to(token_address)\
                    .method("balanceOf")\
                    .params({"_owner": self.tester_addr})\
                    .build()
        result = self.icon_service.call(call)
        self.assertTrue(int(result,16) >= 0)


    def test_token_balanceOf_ca(self):
        call = CallBuilder().from_(self.tester_addr)\
                    .to(token_address)\
                    .method("balanceOf")\
                    .params({"_owner": hello_world_address})\
                    .build()
        result = self.icon_service.call(call)
        self.assertTrue(int(result,16) >= 0)


    def test_icx_balance_eoa(self):
        result = self.icon_service.get_balance(self.tester_addr)
        self.assertTrue(int(result) >= 0)


    def test_icx_balance_ca(self):
        result = self.icon_service.get_balance(hello_world_address)
        self.assertTrue(int(result) >= 0)


    def test_send_token_to_ca(self):
        transaction = CallTransactionBuilder()\
            .from_(self.tester_addr)\
            .to(token_address)\
            .step_limit(2000000)\
            .nid(network_id)\
            .method("transfer")\
            .params({"_to":hello_world_address, "_value":"1"})\
            .build()

        signed_transaction = SignedTransaction(transaction, self.wallet)
        tx_hash = self.icon_service.send_transaction(signed_transaction)

        sleep(8)

        result = self.icon_service.get_transaction_result(tx_hash)
        self.assertEqual(result['status'], 1)
        self.assertFalse(result['eventLogs'] is None)


    def test_send_icx_to_ca(self):
        transaction = TransactionBuilder()\
            .from_(self.tester_addr)\
            .to(hello_world_address)\
            .value(1)\
            .step_limit(2000000)\
            .nid(network_id)\
            .build()

        signed_transaction = SignedTransaction(transaction, self.wallet)
        tx_hash = self.icon_service.send_transaction(signed_transaction)

        sleep(8)

        result = self.icon_service.get_transaction_result(tx_hash)
        self.assertEqual(result['status'], 1)
        self.assertFalse(result['eventLogs'] is None)



if __name__ == '__main__':
    unittest.main()
