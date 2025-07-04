#!/usr/bin/env python3
"""
国際化対応（i18n）モジュール
"""

# 言語設定
LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
}

# テキスト定義
TEXTS = {
    'en': {
        # Page config
        'page_title': 'Wordbook - Unmastered Words by Section',

        # Main UI
        'app_title': '📚 Wordbook',
        'unmastered_words_header': '📖 Unmastered words.',
        'words_found': 'words found',
        'select_word': 'Select a word:',
        'select_word_help': 'Select a word to display example sentences',
        'pick_one_button': '🎲 Pick One',
        'pick_one_help': 'Randomly select a word',
        'example_sentences_for': 'Example sentences for:',
        'section': 'Section',
        'number': 'No.',
        'status': 'Status',

        # Messages
        'loading_words': 'Loading unmastered words...',
        'no_data_found': 'No data found',
        'no_unmastered_words': 'No unmastered words found.',
        'no_example_sentences': 'No example sentences for this word.',
        'sentence_fetch_error': 'Failed to fetch example sentences:',
        'notion_api_error': 'Notion API connection error:',
        'notion_token_missing': 'NOTION_TOKEN is not set',

        # Settings
        'language_setting': 'Language',
        'language_help': 'Select your preferred language'
    },
    'ja': {
        # Page config
        'page_title': 'Wordbook - セクション別未習得単語',

        # Main UI
        'app_title': '📚 Wordbook',
        'unmastered_words_header': '📖 未習得単語',
        'words_found': '語が見つかりました',
        'select_word': '単語を選択:',
        'select_word_help': '単語を選択すると例文が表示されます',
        'pick_one_button': '🎲 Pick One',
        'pick_one_help': 'ランダムに単語を選択',
        'example_sentences_for': '例文:',
        'section': 'セクション',
        'number': '番号',
        'status': 'ステータス',

        # Messages
        'loading_words': '未習得単語を読み込み中...',
        'no_data_found': 'データが見つかりませんでした',
        'no_unmastered_words': '未習得単語が見つかりませんでした。',
        'no_example_sentences': 'この単語には例文がありません。',
        'sentence_fetch_error': '例文の取得に失敗しました:',
        'notion_api_error': 'Notion API接続エラー:',
        'notion_token_missing': 'NOTION_TOKENが設定されていません',

        # Settings
        'language_setting': '言語',
        'language_help': '使用する言語を選択してください'
    }
}


def get_text(key, lang='en'):
    """指定されたキーと言語のテキストを取得"""
    return TEXTS.get(lang, TEXTS['en']).get(key, key)


def get_available_languages():
    """利用可能な言語のリストを取得"""
    return LANGUAGES
