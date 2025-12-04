# 英単語を日本語に翻訳し、例文（辞書APIから取得）を付けて表示するスクリプト
# 使い方：
# 1) 事前に依存パッケージをインストール
#    pip install googletrans==4.0.0-rc1 requests
# 2) スクリプトを実行
#    python english_translator.py words.txt
#    または
#    python english_translator.py word1 word2 ...
#    words.txt は1行に1単語のテキストファイル

import sys
import requests
from googletrans import Translator
from typing import List, Dict, Optional

DICTAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

translator = Translator()

def fetch_dictionary_examples(word: str) -> List[str]:
    """dictionaryapi.dev から意味と例文を取得する。例文が無ければ空リストを返す。"""
    try:
        r = requests.get(DICTAPI_URL.format(word), timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
        examples = []
        # レスポンスは複数エントリを含むことがある
        for entry in data:
            meanings = entry.get('meanings', [])
            for meaning in meanings:
                for definition in meaning.get('definitions', []):
                    ex = definition.get('example')
                    if ex:
                        examples.append(ex)
        # 重複を削除して返す
        return list(dict.fromkeys(examples))
    except Exception:
        return []


def translate_text(text: str, dest: str = 'ja') -> str:
    """googletrans を使って翻訳する。失敗時は元の文字列を返す。"""
    try:
        res = translator.translate(text, dest=dest)
        return res.text
    except Exception:
        return text


def make_fallback_example(word: str) -> str:
    """辞書に例文が無かった場合の簡易例文を作成する（シンプル）"""
    return f"I used the word '{word}' in a sentence to show its meaning."


def translate_word_with_examples(word: str) -> Dict[str, Optional[List[str]]]:
    """単語とその訳、例文（英→日）をまとめて返す"""
    word_strip = word.strip()
    if not word_strip:
        return {}

    # 単語の翻訳
    translated = translate_text(word_strip)

    # 例文を取得
    examples_en = fetch_dictionary_examples(word_strip)
    if not examples_en:
        examples_en = [make_fallback_example(word_strip)]

    # 例文を翻訳
    examples_ja = [translate_text(s) for s in examples_en]
    print('translated', translated)
    print('examples_en', examples_en)
    print('examples_ja', examples_ja)

    return {
        'word': word_strip,
        'translation': translated,
        'examples_en': examples_en,
        'examples_ja': examples_ja
    }


def load_words_from_file(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def main(argv):
    print("main() 開始")
    if len(argv) < 2:
        print("使い方: python english_translator.py words.txt あるいは python english_translator.py word1 word2 ...")
        return

    # 引数が1つでファイルが存在する場合はファイルとして読み込む
    import os
    args = argv[1:]
    words = []
    if len(args) == 1 and os.path.isfile(args[0]):
        words = load_words_from_file(args[0])
    else:
        words = args

    results = []
    print('words',words)
    for w in words:
        res = translate_word_with_examples(w)
        if res:
            results.append(res)

    # ログ開始
    print("処理開始")
    print(f"対象単語数: {len(words)}")

        # CSV 出力
    import csv
    # 出力（見やすく表示）
    for r in results:
        print('---')
        print(f"単語: {r['word']}")
        print(f"訳: {r['translation']}")
        print("例文（英語）:")
        for i, s in enumerate(r['examples_en'], start=1):
            print(f"  {i}. {s}")
        print("例文（日本語訳）:")
        for i, s in enumerate(r['examples_ja'], start=1):
            print(f"  {i}. {s}")

    # CSV へ書き出し（word, translation 列）
    with open('translations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'translation'])
        for r in results:
            print(f"CSV書き込み: {r['word']} -> {r['translation']}")
            writer.writerow([r['word'], r['translation']])

    print("処理完了。translations.csv に出力しました")

if __name__ == '__main__':
    main(sys.argv)
