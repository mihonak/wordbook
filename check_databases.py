#!/usr/bin/env python3
"""
データベース詳細確認
"""

import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()


def check_databases():
    """データベースの詳細を確認"""
    notion_token = os.getenv("NOTION_TOKEN")
    notion = Client(auth=notion_token)

    # 発見されたデータベースID
    database_ids = [
        "2230dc53-a13b-8007-91d2-c3ed98f8dc95",
        "2230dc53-a13b-8055-9c36-cbe6162846ef"
    ]

    for i, db_id in enumerate(database_ids, 1):
        print(f"=== データベース {i} ===")
        print(f"ID: {db_id}")

        try:
            # データベース詳細を取得
            database = notion.databases.retrieve(database_id=db_id)

            # タイトル
            title = "無題"
            if database.get('title') and len(database['title']) > 0:
                title = database['title'][0]['plain_text']
            print(f"タイトル: {title}")

            # URL
            url = f"https://www.notion.so/{db_id.replace('-', '')}"
            print(f"URL: {url}")

            # プロパティ
            print("プロパティ:")
            for prop_name, prop_info in database['properties'].items():
                prop_type = prop_info.get('type', 'unknown')
                print(f"  - {prop_name}: {prop_type}")

            # データベース内のページ数を取得
            query_result = notion.databases.query(
                database_id=db_id, page_size=5)
            page_count = len(query_result['results'])
            print(f"ページ数（最初の5件）: {page_count}")

            # サンプルデータを表示
            if query_result['results']:
                print("サンプルデータ:")
                for j, page in enumerate(query_result['results'][:3], 1):
                    print(f"  {j}. ", end="")
                    # タイトルプロパティを探す
                    for prop_name, prop_value in page['properties'].items():
                        if prop_value.get('type') == 'title':
                            if prop_value.get('title') and len(prop_value['title']) > 0:
                                title_text = prop_value['title'][0]['plain_text']
                                print(f"{title_text}")
                                break
                    else:
                        print("タイトルなし")

        except Exception as e:
            print(f"エラー: {e}")

        print()


if __name__ == "__main__":
    check_databases()
