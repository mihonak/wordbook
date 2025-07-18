#!/usr/bin/env python3
"""
Streamlit単語帳アプリ - セクション別未習得単語表示
"""

import streamlit as st
import pandas as pd
import random
from src.wordbook.notion_client import (
    get_words_data,
    get_notion_client,
    update_word_status
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


def on_word_selection_change():
    """単語選択変更時のコールバック"""
    # selectboxで選択されたインデックスをセッション状態に保存
    selected_index = st.session_state.word_selectbox_index
    st.session_state.selected_word_index = selected_index
    st.session_state.selection_changed = True


@st.dialog("Confirm Status Update")
def show_confirmation_dialog(current_status, new_status, page_id, lang):
    """ステータス更新確認ダイアログ"""
    current_emoji = get_status_emoji(current_status)
    new_emoji = get_status_emoji(new_status)

    st.write(f"**Current:** {current_status} {current_emoji}")
    st.write(f"**New:** {new_status} {new_emoji}")
    st.write("")
    st.write("Are you sure you want to update the status?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Update", use_container_width=True,
                     type="primary"):
            updating_msg = get_text('updating_status', lang)
            with st.spinner(updating_msg):
                success = update_word_status(page_id, new_status)

            if success:
                success_msg = get_text('status_updated', lang)
                st.toast(success_msg, icon="✅")
                # ダイアログを閉じるためのフラグをクリア
                if 'show_dialog' in st.session_state:
                    del st.session_state.show_dialog
                st.rerun()
            else:
                error_msg = get_text('status_update_error', lang)
                st.error(error_msg)

    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            # ダイアログを閉じるためのフラグをクリア
            if 'show_dialog' in st.session_state:
                del st.session_state.show_dialog
            # selectboxの値を元に戻すためのフラグを設定
            st.session_state.reset_selectbox = True
            st.rerun()


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
        sorted_df = df.sort_values(['Section'])

        # 単語選択
        word_options = []
        for _, row in sorted_df.iterrows():
            section = row['Section'] if row['Section'] is not None else '?'
            word = row['Word']
            status = row['Status'] if row['Status'] else 'Unknown'
            status_emoji = get_status_emoji(status)
            display_text = f"Section {section}: {status_emoji} {word}"
            word_options.append(display_text)

        # デフォルトインデックスを決定
        default_index = st.session_state.get('selected_word_index', 0)
        # 範囲チェック
        if default_index >= len(word_options):
            default_index = 0

        # ランダム選択ボタンを追加
        col1, col2 = st.columns([1, 1], vertical_alignment='bottom')

        # 単語選択用のselectbox
        with col1:
            selected_index = st.selectbox(
                get_text('select_word', selected_lang),
                options=range(len(word_options)),
                format_func=lambda x: word_options[x],
                index=default_index,
                help=get_text('select_word_help', selected_lang),
                key="word_selectbox_index",
                on_change=on_word_selection_change
            )

            # セッション状態を更新
            st.session_state.selected_word_index = selected_index

        with col2:
            if st.button(get_text('pick_one_button', selected_lang),
                         help=get_text('pick_one_help', selected_lang),
                         use_container_width=True):
                random_index = random.randint(0, len(word_options) - 1)
                st.session_state.selected_word_index = random_index
                st.session_state.selection_changed = True
                st.rerun()

        if selected_index is not None and selected_index < len(word_options):
            # 選択された単語の情報を取得
            word_info = sorted_df.iloc[selected_index]
            selected_word = word_info['Word']

            st.markdown("---")
            example_text = get_text('example_sentences_for', selected_lang)
            st.markdown(f"{example_text} **{selected_word}**")
            section = word_info['Section']
            status = word_info['Status']
            status_emoji = get_status_emoji(status)

            section_text = get_text('section', selected_lang)
            info_text = f"**{section_text}:** {section}"

            # 単語情報とステータス更新を横並びに配置
            col_info, col_status = st.columns(
                [1, 2], vertical_alignment='bottom')

            with col_info:
                st.markdown(info_text)

            with col_status:
                # 現在のステータスを含むすべての選択肢を作成
                all_statuses = ['Not Sure', 'Seen It',
                                'Almost There', 'Mastered']

                # 現在のステータスのインデックスを取得
                try:
                    current_index = all_statuses.index(status)
                except ValueError:
                    current_index = 0

                # selectboxリセットフラグをチェック
                if st.session_state.get('reset_selectbox', False):
                    # リセットフラグをクリア
                    st.session_state.reset_selectbox = False
                    # selectboxのキーをリセットして再描画を促す
                    selectbox_key = f"status_update_{selected_index}"
                    if selectbox_key in st.session_state:
                        del st.session_state[selectbox_key]

                new_status = st.selectbox(
                    get_text('update_status', selected_lang),
                    options=all_statuses,
                    index=current_index,
                    help=get_text('update_status_help', selected_lang),
                    key=f"status_update_{selected_index}"
                )

                # 現在のステータスと異なる場合、確認ダイアログを表示
                if (new_status != status and
                        not st.session_state.get('show_dialog', False)):
                    # ダイアログ表示フラグを設定
                    st.session_state.show_dialog = True
                    page_id = word_info['page_id']
                    show_confirmation_dialog(
                        status, new_status, page_id, selected_lang)

            # 例文を表示（rollupから取得した例文を使用）
            try:
                example_sentence = word_info.get('example_sentence', '')

                # デバッグ情報を追加
                preview = example_sentence[:100] if example_sentence else '(空)'
                st.write(f"**DEBUG**: example_sentence = '{preview}...'")

                if example_sentence:
                    # 改行で分割して行ごとに処理
                    lines = (example_sentence.replace('\r\n', '\n')
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
