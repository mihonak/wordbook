#!/usr/bin/env python3
"""
Streamlit単語帳アプリ - セクション別未習得単語表示
"""

import streamlit as st
import pandas as pd
import random
from src.wordbook.notion_client import (
    get_sentence_texts,
    get_words_data,
    get_notion_client
)


def get_status_emoji(status):
    """ステータスに対応するemojiを返す"""
    status_map = {
        'Not Sure': '🤔',
        'Seen It': '👀',
        'Almost There': '😃',
        'Mastered': '✅',  # 通常は表示されないが念のため
        None: '❓',
        '': '❓'
    }
    return status_map.get(status, '❓')


def main():
    """メイン関数"""
    st.set_page_config(
        page_title="Wordbook - セクション別未習得単語",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Wordbook")

    # Notion接続テスト
    try:
        get_notion_client()
    except Exception as e:
        st.error(f"Notion API接続エラー: {e}")
        return

    # データを取得
    st.toast("Loading unmastered words...", icon="📚")
    words_data = get_words_data()

    if not words_data:
        st.warning("データが見つかりませんでした")
        return

    # DataFrameに変換
    df = pd.DataFrame(words_data)

    # 単語選択と例文表示
    if not df.empty:
        st.header("📖 Unmastered words.")
        st.markdown(f"**{len(df)}** words found")

        # ソート済みのリストを作成
        sorted_df = df.sort_values(['Section', 'No.'])

        # 単語選択
        word_options = []
        for _, row in sorted_df.iterrows():
            section = row['Section'] if row['Section'] is not None else '?'
            no = row['No.'] if row['No.'] is not None else '?'
            word = row['Word']
            status = row['Status'] if row['Status'] else 'Unknown'
            status_emoji = get_status_emoji(status)
            display_text = f"Section {section}-{no}: {status_emoji} {word}"
            word_options.append(display_text)

        # デフォルトインデックスを決定
        default_index = 0
        if 'selected_word' in st.session_state:
            try:
                selected_word = st.session_state.selected_word
                default_index = word_options.index(selected_word)
            except ValueError:
                # 選択された単語がリストにない場合はデフォルトのまま
                pass

        # ランダム選択ボタンを追加
        col1, col2 = st.columns([1, 1], vertical_alignment='bottom')

        # 単語選択用のselectbox
        with col1:
            selected_display = st.selectbox(
                "Select a word:",
                options=word_options,
                index=default_index,
                help="単語を選択すると例文が表示されます"
            )

        with col2:
            if st.button("🎲 Pick One",
                         help="ランダムに単語を選択",
                         use_container_width=True):
                random_index = random.randint(0, len(word_options) - 1)
                st.session_state.selected_word = word_options[random_index]
                st.rerun()

        if selected_display:
            # 選択された単語のインデックスを取得
            selected_index = word_options.index(selected_display)
            word_info = sorted_df.iloc[selected_index]
            selected_word = word_info['Word']

            st.markdown("---")
            st.markdown(f"Example sentences for: **{selected_word}**")
            section = word_info['Section']
            no = word_info['No.']
            status = word_info['Status']
            status_emoji = get_status_emoji(status)
            info_text = f"**Section:** {section} | **No.:** {no}"
            info_text += f" | **Status:** {status} {status_emoji}"
            st.markdown(info_text)

            # 例文を表示（保存されたIDを使用）
            try:
                sentence_ids = word_info.get('sentence_ids', [])
                all_sentences = get_sentence_texts(sentence_ids)

                if all_sentences:
                    for sentence in all_sentences:
                        # 改行で分割して行ごとに処理
                        lines = (sentence.replace('\r\n', '\n')
                                         .replace('\r', '\n')
                                         .split('\n'))

                        # 例文ブロックを開始
                        style = ("font-size: 18px; line-height: 1.6; "
                                 "margin-bottom: 16px")

                        for line in lines:
                            # 各行の余分な空白を除去
                            cleaned_line = ' '.join(line.split())
                            if cleaned_line:  # 空行でない場合のみ表示
                                div = (f'<div style="{style};">'
                                       f'{cleaned_line}</div>')
                                st.markdown(div, unsafe_allow_html=True)
                else:
                    st.info("この単語には例文がありません。")

            except Exception as e:
                st.error(f"例文の取得に失敗しました: {e}")
    else:
        st.info("未習得単語が見つかりませんでした。")


if __name__ == "__main__":
    main()
