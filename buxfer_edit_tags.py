from buxfer_api import BuxferAPI
import pandas as pd


class EditTags(BuxferAPI):

    def __init__(self):
        super().__init__()


    def update_tag(self, id, tag):
        url = f'{self._base}/transaction_edit?token={self._token}&id={id}&tags={tag}'
        print(url)
        req = self._http.request('POST', url)
        # response = self._checkError(req.data)
        return f'Updated ID={id} with tag={tag}'
        


def main():
    api = EditTags()
    df = pd.read_csv('/Users/stephenusher/Library/CloudStorage/OneDrive-Personal/Documents/Personal/Finance/Accounts Scratch/update_tags.csv')
    print(df)
    for row in df.itertuples():
        print(row)
        api.update_tag(str(row.ID), row.Tag)


if __name__ == '__main__':
    main()