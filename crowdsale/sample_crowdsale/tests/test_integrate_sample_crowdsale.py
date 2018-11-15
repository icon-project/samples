import os

from iconsdk.builder.transaction_builder import (
    CallTransactionBuilder,
    DeployTransactionBuilder,
    TransactionBuilder,
)
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestSampleCrowdsale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    TOKEN_SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../../../irc2_token/sample_token'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install sample token SCORE
        self.token_initial_supply = 1
        self.decimals = 6
        params = {
            '_initialSupply': self.token_initial_supply,
            '_decimals': self.decimals
        }
        tx_result = self._deploy_score(score_path=self.TOKEN_SCORE_PROJECT, params=params)
        self._token_score_address = tx_result['scoreAddress']

        # install sample crowdsale SCORE
        self.fundingGoalInIcx = (self.token_initial_supply * 10 ** self.decimals)
        self.durationInBlocks = 5
        params = {
            '_fundingGoalInIcx': self.fundingGoalInIcx,
            '_tokenScore': self._token_score_address,
            '_durationInBlocks': self.durationInBlocks,
        }
        tx_result = self._deploy_score(self.SCORE_PROJECT, params=params)
        self._score_address = tx_result['scoreAddress']

    def _deploy_score(self, score_path: str, to: str = SCORE_INSTALL_ADDRESS, params: dict = None) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(score_path)) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def _transaction_call(self, from_: KeyWallet, to_: str, method: str, params: dict = None) -> dict:
        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to_) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method(method) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)

        # Sends the transaction to the network
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return tx_result

    def _icx_call(self, from_: str, to_: str, method: str, params: dict = None):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(from_) \
            .to(to_) \
            .method(method) \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        return response

    def _token_balance(self, owner: str, score_address: str):
        # Make params of balanceOf method
        params = {
            # token owner
            '_owner': owner
        }
        return self._icx_call(self._test1.get_address(), score_address, 'balanceOf', params)

    def _transfer_icx(self, from_: KeyWallet, to_:str, value: int) -> dict:
        # Generates an instance of transaction for calling method in SCORE.
        transaction = TransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to_) \
            .value(value) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)

        # Sends the transaction to the network
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(score_path=self.TOKEN_SCORE_PROJECT, to=self._score_address)

        self.assertEqual(tx_result['scoreAddress'], self._score_address)

    def test_transfer_token_to_crowdsale(self):
        """
        Test tokenFallback method
        """
        # Make params of transfer method
        params = {
            "_to": self._score_address,
            "_value": self.fundingGoalInIcx

        }
        # Send all tokens to crowdsale SCORE
        self._transaction_call(self._test1, self._token_score_address, 'transfer', params)

        # Check token balance of crowdsale SCORE
        response = self._token_balance(owner=self._score_address, score_address=self._token_score_address)
        self.assertEqual(hex(self.fundingGoalInIcx), response)

    def test_fund_to_crowdsale(self):
        # prepare crowdsale
        self.test_transfer_token_to_crowdsale()

        contributor_count = 4
        contribute_value = self.fundingGoalInIcx // contributor_count
        for i in range(contributor_count):
            # Initialize balance of contributor
            self._transfer_icx(self._test1,
                               self._wallet_array[i].get_address(),
                               contribute_value)

            # fund to crowdsale
            self._transfer_icx(self._wallet_array[i], self._score_address, contribute_value)

            # check token balance of contributor
            response = self._token_balance(self._wallet_array[i].get_address(), self._token_score_address)
            self.assertEqual(hex(contribute_value), response)

        # check crowdsale joiner count
        response = self._icx_call(self._test1.get_address(), self._score_address, 'totalJoinerCount')
        self.assertEqual(hex(contributor_count), response)

        # send checkGoalReached transaction
        response = self._transaction_call(self._test1, self._score_address, 'checkGoalReached')
        # check event log
        event_logs = response['eventLogs']
        for event_log in event_logs:
            if event_log['scoreAddress'] == self._score_address:
                indexed = event_log['indexed']
                self.assertEqual('GoalReached(Address,int)', indexed[0])
                self.assertEqual(self._test1.get_address(), indexed[1])
                self.assertEqual(hex(self.fundingGoalInIcx), indexed[2])

    def test_safe_withdrawal(self):
        # prepare and end crowdsale
        self.test_fund_to_crowdsale()

        # send safeWithdrawal transaction
        response = self._transaction_call(self._test1, self._score_address, 'safeWithdrawal')
        # check event log
        event_logs = response['eventLogs']
        for event_log in event_logs:
            indexed = event_log['indexed']
            if event_log['scoreAddress'] == self._score_address:
                if indexed[0] == 'FundTransfer(Address,int,bool)':
                    indexed = event_log['indexed']
                    self.assertEqual(self._test1.get_address(), indexed[1])
                    self.assertEqual(hex(self.fundingGoalInIcx), indexed[2])
                    self.assertEqual(hex(False), indexed[3])

