#!/usr/bin/env python3
"""
Streamlit単語帳アプリ - セクション別未習得単語表示
"""

import os
import streamlit as st
import pandas as pd
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


@st.cache_data
def get_sentences_data():
    """Sentencesデータベースから全データを取得"""
    notion = get_notion_client()  # キャッシュされたクライアントを使用
    sentences_db_id = "2230dc53-a13b-8055-9c36-cbe6162846ef"

    try:
        # 全データを取得
        all_results = []
        has_more = True
        start_cursor = None

        while has_more:
            query_params = {
                "database_id": sentences_db_id,
                "page_size": 100
            }
            if start_cursor:
                query_params["start_cursor"] = start_cursor

            result = notion.databases.query(**query_params)
            all_results.extend(result['results'])
            has_more = result['has_more']
            start_cursor = result.get('next_cursor')

        # データを整理
        sentences_data = []
        for page in all_results:
            sentence_text = ""
            unmastered_words = ""
            section = None
            no = None

            for prop_name, prop_value in page['properties'].items():
                prop_type = prop_value.get('type')

                if prop_type == 'title':
                    # 例文
                    title_content = prop_value.get('title')
                    if title_content and len(title_content) > 0:
                        sentence_text = title_content[0]['plain_text']

                elif prop_type == 'formula':
                    # Unmastered Words
                    formula_result = prop_value.get('formula', {})
                    if formula_result.get('type') == 'string':
                        string_value = formula_result.get('string')
                        if string_value and string_value.strip():
                            if 'unmastered' in prop_name.lower():
                                unmastered_words = string_value

                elif prop_type == 'number':
                    # Section, No
                    number_value = prop_value.get('number')
                    if number_value is not None:
                        if prop_name.lower() == 'section':
                            section = int(number_value)
                        elif prop_name.lower() == 'no':
                            no = int(number_value)

            if sentence_text and unmastered_words:
                sentences_data.append({
                    'section': section,
                    'no': no,
                    'sentence': sentence_text,
                    'unmastered_words': unmastered_words,
                    'page_id': page['id']
                })

        return sentences_data

    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return []


def main():
    """メイン関数"""
    st.set_page_config(
        page_title="Wordbook - セクション別未習得単語",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Wordbook")

    # データを取得
    with st.spinner("データを読み込み中..."):
        sentences_data = get_sentences_data()

    if not sentences_data:
        st.warning("データが見つかりませんでした")
        return

    # DataFrameに変換
    df = pd.DataFrame(sentences_data)

    # サイドバーでフィルタ設定
    st.sidebar.header("🔍 Filter")

    # 未習得単語でのフィルタ
    search_word = st.sidebar.text_input(
        "Search",
        placeholder="例: density, gradually",
        help="部分一致で検索します"
    )

    # フィルタ適用
    filtered_df = df.copy()

    if search_word:
        filtered_df = filtered_df[
            filtered_df['unmastered_words'].str.contains(
                search_word, case=False, na=False
            )
        ]

    # 例文一覧表示
    if not filtered_df.empty:
        st.header("📖 Sentences contains unmastered words.")
        st.markdown(f"**{len(filtered_df)}** sentences found")

        # 表形式で表示
        columns = ['section', 'no', 'sentence', 'unmastered_words']
        display_df = filtered_df[columns].copy()
        display_df = display_df.sort_values(['section', 'no'])
        display_df.columns = ['Section', 'No.', '例文', '未習得単語']

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Section": st.column_config.NumberColumn(
                    width="small"
                ),
                "No.": st.column_config.NumberColumn(
                    width="small"
                ),
                "例文": st.column_config.TextColumn(
                    width="large"
                ),
                "未習得単語": st.column_config.TextColumn(
                    width="medium"
                )
            }
        )
    else:
        st.info("未習得単語がある例文が見つかりませんでした。")


if __name__ == "__main__":
    main()
