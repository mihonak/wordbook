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
from src.wordbook.i18n import get_text, get_available_languages


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
    # 言語設定をサイドバーに追加
    with st.sidebar:
        st.header("Settings")
        languages = get_available_languages()
        selected_lang = st.selectbox(
            "Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0,  # デフォルトは英語
            help="Select your preferred language"
        )

    st.set_page_config(
        page_title=get_text('page_title', selected_lang),
        page_icon="📚",
        layout="wide"
    )

    st.title(get_text('app_title', selected_lang))

    # Notion接続テスト
    try:
        get_notion_client()
    except Exception as e:
        st.error(f"{get_text('notion_api_error', selected_lang)} {e}")
        return

    # データを取得
    st.toast(get_text('loading_words', selected_lang), icon="📚")
    words_data = get_words_data()

    if not words_data:
        st.warning(get_text('no_data_found', selected_lang))
        return

    # DataFrameに変換
    df = pd.DataFrame(words_data)

    # 単語選択と例文表示
    if not df.empty:
        st.header(get_text('unmastered_words_header', selected_lang))
        word_count = len(df)
        words_found_text = get_text('words_found', selected_lang)
        st.markdown(f"**{word_count}** {words_found_text}")

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
                get_text('select_word', selected_lang),
                options=word_options,
                index=default_index,
                help=get_text('select_word_help', selected_lang)
            )

        with col2:
            if st.button(get_text('pick_one_button', selected_lang),
                         help=get_text('pick_one_help', selected_lang),
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
            example_text = get_text('example_sentences_for', selected_lang)
            st.markdown(f"{example_text} **{selected_word}**")
            section = word_info['Section']
            no = word_info['No.']
            status = word_info['Status']
            status_emoji = get_status_emoji(status)

            section_text = get_text('section', selected_lang)
            number_text = get_text('number', selected_lang)
            status_text = get_text('status', selected_lang)
            info_text = (f"**{section_text}:** {section} | "
                         f"**{number_text}:** {no}")
            info_text += f" | **{status_text}:** {status} {status_emoji}"
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
                    st.info(get_text('no_example_sentences', selected_lang))

            except Exception as e:
                error_msg = get_text('sentence_fetch_error', selected_lang)
                st.error(f"{error_msg} {e}")
    else:
        st.info(get_text('no_unmastered_words', selected_lang))


if __name__ == "__main__":
    main()
