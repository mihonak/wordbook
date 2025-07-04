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
def get_sentence_texts(sentence_ids):
    """例文IDリストから例文テキストを一括取得"""
    if not sentence_ids:
        return []

    notion = get_notion_client()
    sentences = []

    # バッチ処理で例文を取得（最大10個まで）
    for sentence_id in sentence_ids[:10]:  # パフォーマンス向上のため最大10個に制限
        try:
            sentence_page = notion.pages.retrieve(page_id=sentence_id)
            properties = sentence_page['properties']
            title_prop = properties.get('例文')
            if title_prop and title_prop.get('type') == 'title':
                titles = title_prop.get('title', [])
                if titles and len(titles) > 0:
                    sentence_parts = []
                    for text_element in titles:
                        if text_element.get('plain_text'):
                            sentence_parts.append(text_element['plain_text'])
                    text = ''.join(sentence_parts).strip()
                    sentences.append(text)
        except Exception:
            continue

    return sentences


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
            no = None
            status = None
            sentences = []

            for prop_name, prop_value in page['properties'].items():
                prop_type = prop_value.get('type')

                if prop_type == 'title':
                    # 単語
                    title_content = prop_value.get('title')
                    if title_content and len(title_content) > 0:
                        # 前後の空白を除去
                        word_parts = []
                        for text_element in title_content:
                            if text_element.get('plain_text'):
                                word_parts.append(text_element['plain_text'])
                        word_text = ''.join(word_parts).strip()

                elif prop_type == 'relation':
                    # Sentences (relation) - IDのみ収集、後でバッチ取得
                    if 'sentences' in prop_name.lower():
                        relation_data = prop_value.get('relation', [])
                        sentence_ids = []
                        for relation_item in relation_data:
                            sentence_id = relation_item.get('id')
                            if sentence_id:
                                sentence_ids.append(sentence_id)
                        sentences = sentence_ids  # IDリストを保存

                elif prop_type == 'rollup':
                    # Section, No (rollup)
                    rollup_result = prop_value.get('rollup', {})

                    if rollup_result.get('type') == 'array':
                        # rollupが配列の場合
                        array_data = rollup_result.get('array', [])
                        if array_data and len(array_data) > 0:
                            first_item = array_data[0]
                            if first_item.get('type') == 'number':
                                number_value = first_item.get('number')
                                if number_value is not None:
                                    if prop_name.lower() == 'section':
                                        section = int(number_value)
                                    elif 'no' in prop_name.lower():
                                        no = int(number_value)
                    elif rollup_result.get('type') == 'number':
                        # rollupが直接数値の場合
                        number_value = rollup_result.get('number')
                        if number_value is not None:
                            if prop_name.lower() == 'section':
                                section = int(number_value)
                            elif 'no' in prop_name.lower():
                                no = int(number_value)

                elif prop_type == 'status':
                    # Status
                    if 'status' in prop_name.lower():
                        status_obj = prop_value.get('status')
                        if status_obj:
                            status = status_obj.get('name', '')

            # 未習得の単語のみを取得 (Statusが"Mastered"でないもの)
            if word_text and status != "Mastered":
                words_data.append({
                    'Section': section,
                    'No.': no,
                    'Word': word_text,
                    'Status': status,
                    'sentence_ids': sentences,  # 例文IDを保存
                    'page_id': page['id']
                })

        return words_data

    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return []
