#!/usr/bin/env python3
"""
Notion API クライアントとデータ取得機能
"""

import os
import streamlit as st
from dotenv import load_dotenv
from notion_client import Client

# 環境変数を読み込み
load_dotenv()


@st.cache_resource
def get_notion_client():
    """Notionクライアントを取得（リソースキャッシュあり）"""
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        st.error("NOTION_TOKENが設定されていません")
        st.stop()
    return Client(auth=notion_token)


@st.cache_data(ttl=60, show_spinner=False)  # スピナーを非表示
def get_sentence_text(sentence_id):
    """例文IDから例文テキストを取得"""
    if not sentence_id:
        return ""

    notion = get_notion_client()

    try:
        sentence_page = notion.pages.retrieve(page_id=sentence_id)
        properties = sentence_page['properties']

        # Example sentence (rich_text) プロパティから例文を取得
        example_sentence_prop = properties.get('Example sentence')
        is_rich_text = (
            example_sentence_prop and
            example_sentence_prop.get('type') == 'rich_text'
        )
        if is_rich_text:
            rich_text_data = example_sentence_prop.get('rich_text', [])
            if rich_text_data:
                sentence_parts = []
                for text_element in rich_text_data:
                    if text_element.get('plain_text'):
                        sentence_parts.append(text_element['plain_text'])
                text = ''.join(sentence_parts).strip()
                return text
    except Exception:
        pass

    return ""


@st.cache_data(ttl=60, show_spinner=False)  # スピナーを非表示
def get_words_data():
    """Wordsデータベースから全データを取得"""
    notion = get_notion_client()  # キャッシュされたクライアントを使用
    words_db_id = "2230dc53-a13b-8007-91d2-c3ed98f8dc95"  # WordsデータベースのID

    try:
        # 全データを取得
        all_results = []
        has_more = True
        start_cursor = None

        while has_more:
            query_params = {
                "database_id": words_db_id,
                "page_size": 100
            }
            if start_cursor:
                query_params["start_cursor"] = start_cursor

            result = notion.databases.query(**query_params)
            all_results.extend(result['results'])
            has_more = result['has_more']
            start_cursor = result.get('next_cursor')

        # データを整理
        words_data = []
        for page in all_results:
            word_text = ""
            section = None
            status = None
            example_sentence = ""
            example_no = None

            for prop_name, prop_value in page['properties'].items():
                prop_type = prop_value.get('type')

                if prop_type == 'title':
                    # Word (title) - 単語
                    title_content = prop_value.get('title')
                    if title_content and len(title_content) > 0:
                        word_parts = []
                        for text_element in title_content:
                            if text_element.get('plain_text'):
                                word_parts.append(text_element['plain_text'])
                        word_text = ''.join(word_parts).strip()

                elif prop_type == 'relation':
                    # Example No (relation) - スキップ（パフォーマンス改善のため）
                    pass

                elif prop_type == 'rollup':
                    # Section, Example sentence (rollup)
                    rollup_result = prop_value.get('rollup', {})

                    if rollup_result.get('type') == 'array':
                        # rollupが配列の場合
                        array_data = rollup_result.get('array', [])
                        if array_data and len(array_data) > 0:
                            first_item = array_data[0]

                            if first_item.get('type') == 'number':
                                number_value = first_item.get('number')
                                if number_value is not None:
                                    if prop_name == 'Section':
                                        section = int(number_value)
                                    elif prop_name == 'Example No':
                                        example_no = int(number_value)

                            elif first_item.get('type') == 'title':
                                # Example No (rollup) - titleタイプからExample Noを取得
                                if prop_name == 'Example No':
                                    title_data = first_item.get('title', [])
                                    if title_data:
                                        title_parts = []
                                        for text_element in title_data:
                                            if text_element.get('plain_text'):
                                                title_parts.append(
                                                    text_element['plain_text']
                                                )
                                        title_text = ''.join(title_parts).strip()
                                        if title_text.isdigit():
                                            example_no = int(title_text)

                            elif first_item.get('type') == 'rich_text':
                                # Example sentence (rollup) - 例文をrollupから取得
                                if prop_name == 'Example sentence':
                                    rich_text_data = first_item.get('rich_text', [])
                                    if rich_text_data:
                                        sentence_parts = []
                                        for text_element in rich_text_data:
                                            if text_element.get('plain_text'):
                                                sentence_parts.append(
                                                    text_element['plain_text']
                                                )
                                        example_sentence = ''.join(
                                            sentence_parts
                                        ).strip()

                    elif rollup_result.get('type') == 'number':
                        # rollupが直接数値の場合
                        number_value = rollup_result.get('number')
                        if number_value is not None:
                            if prop_name == 'Section':
                                section = int(number_value)
                            elif prop_name == 'Example No':
                                example_no = int(number_value)

                elif prop_type == 'status':
                    # Status
                    if prop_name == 'Status':
                        status_obj = prop_value.get('status')
                        if status_obj:
                            status = status_obj.get('name', '')

            # 未習得の単語のみを取得 (Statusが"Mastered"でないもの)
            if word_text and status != "Mastered":
                words_data.append({
                    'Section': section,
                    'Word': word_text,
                    'Status': status,
                    'example_sentence': example_sentence,  # rollupから取得した例文
                    'example_no': example_no,  # rollupから取得したExample No
                    'page_id': page['id']
                })

        return words_data

    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return []


def update_word_status(page_id, new_status):
    """単語のステータスを更新"""
    try:
        notion = get_notion_client()

        # ステータスプロパティを更新
        notion.pages.update(
            page_id=page_id,
            properties={
                "Status": {
                    "status": {
                        "name": new_status
                    }
                }
            }
        )

        # キャッシュをクリア
        get_words_data.clear()

        return True

    except Exception as e:
        st.error(f"ステータス更新エラー: {e}")
        return False
