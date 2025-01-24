import sys
import json
import pandas as pd
from urllib3 import PoolManager
from configparser import ConfigParser


class BuxferAPI:

    
    def __init__(self):
        self._getCredentials()
        self._http = PoolManager()
        self._base = 'https://www.buxfer.com/api'
        self._token = self._getToken()
        self._accountNames = None
        self._accountBalances = None
        self._tags = None
        self._transactions = None


    def _getCredentials(self):
        config = ConfigParser()
        config.read('config.ini')
        self._username = config['BUXFERAPI']['USERNAME']
        self._password = config['BUXFERAPI']['PASSWORD']


    def _getToken(self):
        url = self._base + '/login?userid=' + self._username + '&password=' + self._password
        req = self._http.request('POST', url)
        response = self._checkError(req.data)
        return response['token']
    

    def _checkError(self, response):
        result = json.loads(response.decode('utf-8'))
        response = result['response']
        if response['status'] != 'OK':
            print(f'An error occurred: {response['status'].replace('ERROR: ', '')}')
            sys.exit()
        return response


    def _fetchAccounts(self):
        url = self._base + '/accounts?token=' + self._token
        req = self._http.request('GET', url)
        response = self._checkError(req.data)
        return response
    

    def _fetchTags(self):
        url = f'{self._base}/tags?token={self._token}'
        req = self._http.request('GET', url)
        response = self._checkError(req.data)
        return response
    

    def _fetchTransactions(self, query):
        url = f'{self._base}/transactions?token={self._token}{query}'
        req = self._http.request('GET', url)
        response = self._checkError(req.data)
        return response
    

    @property
    def accountNames(self):
        if self._accountNames is None:
            response = self._fetchAccounts()
            self._accountNames = (pd.DataFrame(response['accounts'],
                                               columns=['name'])
                                               .sort_values('name')
                                               .reset_index(drop=True))
        return self._accountNames
    

    @property
    def accountBalances(self):
        if self._accountBalances is None:
            response = self._fetchAccounts()
            self._accountBalances = (pd.DataFrame(response['accounts'],
                                                  columns=['id', 'name', 'balance'])
                                                  .sort_values('name')
                                                  .reset_index(drop=True))
        return self._accountBalances


    @property
    def tags(self):
        if self._tags is None:
            response = self._fetchTags()
            self._tags = (pd.DataFrame(response['tags'],
                                       columns=['id', 'name', 'parentId'])
                                       .sort_values('name')
                                       .reset_index(drop=True))
        return self._tags
    

    def transactions_page(self, page=0):
    
        response = self._fetchTransactions(page)
        # self._transactions = (pd.DataFrame(response['transactions'][0],
        #                                    columns=['id', 'description', 'date', 'type', 'amount', 'accountId', 'tags'])
        #                                    .sort_values('id')
        #                                    .reset_index(drop=True))
        transactions = response['transactions']
        # for transaction in transactions:
        #     print(transaction)
        transactions = pd.json_normalize(transactions, max_level=0)
        if self._transactions is None:
            self._transactions = transactions
        else:
            self._transactions = pd.concat([self._transactions, transactions])
        # self._transactions = self._transactions[['id', 'description', 'date', 'type', 'amount', '']]
        return len(self._transactions)


    def transactions_account(self, account=None):
        response = self._fetchTransactions(account=account)
        transactions = response['transactions']
        # with open('cashplus.json', 'w') as file:
        #     json.dump(transactions, file)
        # return None
        transactions = pd.json_normalize(transactions, max_level=0)
        return transactions


    def transactions(self, **kwargs):
        query = self._query_builder(**kwargs)
        page = kwargs.get('page', 0)
        if page == 'all':
            transaction_count = 100
            page = 0
            while (transaction_count > 0):
                print(f'\rFetching page {page + 1}', end='')
                query += f'&page={page}'
                response = self._fetchTransactions(query)
                transactions_page = pd.json_normalize(response['transactions'], max_level=0)
                transaction_count = len(transactions_page)
                if page == 0:
                    transactions = transactions_page
                else:
                    transactions = pd.concat([transactions, transactions_page])
                page += 1
            print('\nDone.')
            return transactions
        else:
            query += f'&page={page}'
            response = self._fetchTransactions(query)
            return pd.json_normalize(response['transactions'], max_level=0)
            

    def _query_builder(self, **kwargs):
        query = []
        account = query.append(f'&accountName={kwargs['account']}') if 'account' in kwargs else None
        month = query.append(f'&month={kwargs['month']}') if 'month' in kwargs else None
        return ''.join(query)
    

def main():
    buxfer = BuxferAPI()
    print(buxfer.accountNames)
    # print(buxfer.accountBalances)
    # print(buxfer.tags)
    # buxfer.transactions.to_csv('transactions.csv')
    # buxfer.transactions_account('2A. Lloyds Main').to_csv('lloyds_main.csv', index=False)
    # buxfer.transactions_account('2A. Lloyds Main')
    # buxfer.transactions(page=0, account='Account')
    # buxfer.transactions(page='all').to_csv('test.csv', index=False)
    # buxfer.transactions(account='8A. Chloë Current').to_csv('cu.csv', index=False)
    buxfer.transactions(account='1A. Lloyds Main', page='all').to_csv('lloyds_main.csv', index=False)
    sys.exit(0)


if __name__ == '__main__':
    main()
