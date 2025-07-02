#!/usr/bin/env python3
"""
Wordbook - Notion連携単語帳アプリケーション
"""

import os
from dotenv import load_dotenv
from notion_client import Client

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン関数"""
    print("Wordbook - Notion連携単語帳アプリケーション")

    # Notion APIキーの確認
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        print("エラー: NOTION_TOKENが設定されていません")
        print("1. Notion Developerページでintegrationを作成してください")
        print("2. .envファイルにNOTION_TOKEN=your_token_hereを設定してください")
        return

    # Notionクライアントを初期化
    try:
        notion = Client(auth=notion_token)
        print("Notion APIに正常に接続しました")

        # 簡単な接続テスト
        users = notion.users.list()
        print(f"ユーザー数: {len(users['results'])}")

        # データベース一覧を取得
        print("\n=== データベース一覧 ===")
        search_results = notion.search(
            filter={"property": "object", "value": "database"}
        )

        if search_results['results']:
            for i, db in enumerate(search_results['results'], 1):
                db_title = "無題"
                if db.get('title') and len(db['title']) > 0:
                    db_title = db['title'][0]['plain_text']

                print(f"{i}. {db_title}")
                print(f"   ID: {db['id']}")
                db_url = f"https://www.notion.so/{db['id'].replace('-', '')}"
                print(f"   URL: {db_url}")

                # プロパティ情報も表示
                if 'properties' in db:
                    print("   プロパティ:")
                    for prop_name, prop_info in db['properties'].items():
                        prop_type = prop_info.get('type', 'unknown')
                        print(f"     - {prop_name} ({prop_type})")
                print()
        else:
            print("データベースが見つかりませんでした")

        # ページ一覧も取得（最初の10件）
        print("=== ページ一覧（最初の10件）===")
        pages_results = notion.search(
            filter={"property": "object", "value": "page"},
            page_size=10
        )

        if pages_results['results']:
            for i, page in enumerate(pages_results['results'], 1):
                page_title = "無題"
                if page.get('properties'):
                    # データベースページの場合
                    title_prop = None
                    for prop_name, prop_value in page['properties'].items():
                        if prop_value.get('type') == 'title':
                            title_prop = prop_value
                            break

                    if (title_prop and title_prop.get('title') and
                            len(title_prop['title']) > 0):
                        page_title = title_prop['title'][0]['plain_text']
                elif (page.get('properties') and
                      page['properties'].get('title')):
                    # 通常のページの場合
                    title_data = page['properties']['title']
                    if (title_data.get('title') and
                            len(title_data['title']) > 0):
                        page_title = title_data['title'][0]['plain_text']

                print(f"{i}. {page_title}")
                print(f"   ID: {page['id']}")
                if (page.get('parent') and
                        page['parent'].get('type') == 'database_id'):
                    print("   データベース内のページ")
                print()
        else:
            print("ページが見つかりませんでした")

    except Exception as e:
        print(f"Notion API接続エラー: {e}")
        return


if __name__ == "__main__":
    main()
