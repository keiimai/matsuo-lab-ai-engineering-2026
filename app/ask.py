"""第1回: 会話履歴を保ちながら素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 既定の質問から会話を始める
    # 続けて質問し、exit または quit で終了

ツールは使わず、同じチャットに質問を送ることで会話履歴を維持する。
講座に固有のことを聞くと、講座の情報がないLLMがどう答えるか確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
from time import perf_counter

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat: genai.chats.Chat, question: str) -> str:
    started_at = perf_counter()
    response = chat.send_message(question)
    elapsed = perf_counter() - started_at
    print(f"[応答時間] {elapsed:.2f} 秒")

    usage = response.usage_metadata
    if usage is None:
        print("[トークン数] 利用情報なし")
    else:
        print(
            f"[トークン数] 入力: {usage.prompt_token_count}, "
            f"出力: {usage.candidates_token_count}"
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保って素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        question = args.question
        while True:
            print(f"[質問] {question}")
            print(ask(chat, question))

            while True:
                try:
                    question = input("\n質問（exit または quit で終了）> ").strip()
                except EOFError:
                    return
                if question.lower() in {"exit", "quit"}:
                    return
                if question:
                    break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
