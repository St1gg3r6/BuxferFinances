from buxfer_api import BuxferAPI
import pandas as pd


class Fetch(BuxferAPI):

    def __init__(self):
        super().__init__()
        self._accountNames = None


    def _fetchAccounts(self):
        url = self._base + '/accounts?token=' + self._token
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
    

def main():
    api = Fetch()
    print(api.accountNames)


if __name__ == '__main__':
    main()
