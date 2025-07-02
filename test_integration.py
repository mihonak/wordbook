#!/usr/bin/env python3
"""
Integration接続テスト
"""

import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()


def test_integration():
    """Integration接続をテスト"""
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        print("NOTION_TOKENが設定されていません")
        return

    try:
        notion = Client(auth=notion_token)

        # 現在のIntegrationの情報を取得
        print("=== Integration情報 ===")

        # ユーザー情報（Integration自体も含む）
        users = notion.users.list()
        print(f"アクセス可能なユーザー数: {len(users['results'])}")

        for user in users['results']:
            user_type = user.get('type', 'unknown')
            name = user.get('name', 'Unknown')
            print(f"- {name} ({user_type})")

        # 検索可能なすべてのオブジェクト
        print("\n=== 検索可能なオブジェクト ===")
        all_results = notion.search()
        print(f"アクセス可能なオブジェクト数: {len(all_results['results'])}")

        if not all_results['results']:
            print("❌ アクセス可能なページやデータベースがありません")
            print("📝 解決方法:")
            print("1. Notionでページまたはデータベースを作成")
            print("2. そのページの「Share」からIntegrationを招待")
            print("3. Integration名は大文字小文字を正確に入力")
        else:
            print("✅ 以下のオブジェクトにアクセス可能:")
            for obj in all_results['results']:
                obj_type = obj.get('object', 'unknown')
                obj_id = obj.get('id', 'unknown')
                print(f"- {obj_type}: {obj_id}")

    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    test_integration()
