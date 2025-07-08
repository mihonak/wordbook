#!/usr/bin/env python3
"""
Sentences データベースの Unmastered words フィルタリング
"""

import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()


def get_unmastered_sentences():
    """Unmastered wordsに値があるSentencesを取得"""
    notion_token = os.getenv("NOTION_TOKEN")
    notion = Client(auth=notion_token)

    # Sentences データベースID
    sentences_db_id = "2230dc53-a13b-8055-9c36-cbe6162846ef"

    try:
        # まず、データベースの構造を確認
        database = notion.databases.retrieve(database_id=sentences_db_id)

        print("=== Sentences データベース構造 ===")
        print("プロパティ:")
        for prop_name, prop_info in database['properties'].items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"  - {prop_name}: {prop_type}")

        print("\n=== 全レコード取得（最初の20件）===")

        # 全レコードを取得して内容を確認
        query_result = notion.databases.query(
            database_id=sentences_db_id,
            page_size=20
        )

        print(f"取得したレコード数: {len(query_result['results'])}")

        unmastered_sentences = []

        for i, page in enumerate(query_result['results'], 1):
            print(f"\n【レコード {i}】")

            sentence_text = ""
            unmastered_words = None

            # 各プロパティの値を取得
            for prop_name, prop_value in page['properties'].items():
                prop_type = prop_value.get('type')

                if prop_type == 'title':
                    # 例文（タイトル）
                    title_data = prop_value.get('title')
                    if title_data and len(title_data) > 0:
                        sentence_text = title_data[0]['plain_text']
                        print(f"例文: {sentence_text}")

                elif prop_type == 'rich_text':
                    # リッチテキスト
                    rich_text_data = prop_value.get('rich_text')
                    if rich_text_data and len(rich_text_data) > 0:
                        text = rich_text_data[0]['plain_text']
                        print(f"{prop_name}: {text}")

                        # Unmastered words かどうか確認
                        prop_lower = prop_name.lower()
                        if 'unmastered' in prop_lower or 'words' in prop_lower:
                            if text.strip():  # 空でない場合
                                unmastered_words = text

                elif prop_type == 'relation':
                    # リレーション
                    relations = prop_value.get('relation', [])
                    if relations:
                        print(f"{prop_name}: {len(relations)}個の関連")
                        # リレーションの詳細も表示したい場合
                        for rel in relations[:3]:  # 最初の3個まで
                            print(f"  - 関連ID: {rel['id']}")

                elif prop_type == 'number':
                    # 数値
                    number_value = prop_value.get('number')
                    if number_value is not None:
                        print(f"{prop_name}: {number_value}")

                elif prop_type == 'formula':
                    # 数式 - Unmastered Words はこれ
                    formula_result = prop_value.get('formula', {})
                    formula_type = formula_result.get('type')

                    if formula_type == 'string':
                        string_value = formula_result.get('string')
                        if string_value and string_value.strip():
                            print(f"{prop_name}: {string_value}")
                            # Unmastered Words プロパティかどうか確認
                            if 'unmastered' in prop_name.lower():
                                unmastered_words = string_value

                    elif formula_type == 'number':
                        number_value = formula_result.get('number')
                        if number_value is not None:
                            print(f"{prop_name}: {number_value}")

                elif prop_type == 'select':
                    # セレクト
                    select_value = prop_value.get('select')
                    if select_value:
                        print(f"{prop_name}: {select_value.get('name', '')}")

                elif prop_type == 'multi_select':
                    # マルチセレクト
                    multi_select_values = prop_value.get('multi_select', [])
                    if multi_select_values:
                        values = [item['name'] for item in multi_select_values]
                        print(f"{prop_name}: {', '.join(values)}")

            # Unmastered words に値がある場合リストに追加
            if unmastered_words:
                unmastered_sentences.append({
                    'sentence': sentence_text,
                    'unmastered_words': unmastered_words,
                    'page_id': page['id']
                })

        # 結果をまとめて表示
        unmastered_count = len(unmastered_sentences)
        print(f"\n=== Unmastered words がある例文 ({unmastered_count}件) ===")
        for i, item in enumerate(unmastered_sentences, 1):
            print(f"\n{i}. {item['sentence']}")
            print(f"   未習得単語: {item['unmastered_words']}")
            print(f"   ページID: {item['page_id']}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    get_unmastered_sentences()
