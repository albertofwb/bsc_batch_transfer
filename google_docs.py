import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class AirdropItem:
    def __init__(self, wallet_address, v2ex_username, github_username):
        self.wallet_address = wallet_address
        self.v2ex_username = v2ex_username
        self.github_username = github_username

    def __repr__(self):
        return f'''
AirdropItem

wallet_address={self.wallet_address}
v2ex_username={self.v2ex_username}
github_username={self.github_username}
'''

def init_airdrop_from_list(item_list: list) -> AirdropItem:
    return AirdropItem(*item_list)


def download_google_sheet(auth_file: str, sheet_url: str):
    # 设置凭据
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(auth_file, scope)
    client = gspread.authorize(creds)

    # 从URL打开工作表
    sheet = client.open_by_url(sheet_url).sheet1

    # 获取所有值
    values = sheet.get_all_values()

    # 提取前三列
    data = [row[:3] for row in values]

    return data


def get_airdrop_members_from_google_excel() -> [AirdropItem]:
    sheet_url = "https://docs.google.com/spreadsheets/d/1Rbf3bQLpLyrSOuOUBOCtXbVG04Rou9fTW5tWsmAdOro/edit?gid=0#gid=0"
    auth_file = os.path.expanduser("~/Dropbox/dev/google-drive-key.json")
    result = download_google_sheet(auth_file, sheet_url)
    members = []
    for row in result[1:]:
        s = init_airdrop_from_list(row)
        members.append(s)
    print(members)
    return members


if __name__ == '__main__':
    get_airdrop_members_from_google_excel()
