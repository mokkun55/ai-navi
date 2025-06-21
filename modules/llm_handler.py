import lmstudio as lms
import config

# グローバル変数としてモデルを保持
model = None

def initialize_model():
    """
    LM Studioモデルを初期化する。
    """
    global model
    if model is None:
        print("LM Studioモデルをロードしています...")
        model = lms.llm(config.lm_model)
        print("LM Studioモデルのロードが完了しました。")

def generate_response(user_text):
    """
    ユーザーのテキストに対してLLMからの応答を生成する。

    Args:
        user_text (str): ユーザーからの入力テキスト。

    Returns:
        str: LLMからの応答テキスト。
    """
    initialize_model()

    if not model:
        return "LM Studioモデルの初期化に失敗しました。"

    try:
        chat = lms.Chat(config.system_prompt)
        chat.add_user_message(user_text)
        response = model.respond(chat)
        return response
    except Exception as e:
        return f"応答生成中にエラーが発生しました: {e}"

if __name__ == '__main__':
    # テスト用
    test_message = "こんにちは！何かおすすめの屋台はありますか？"
    print(f"ユーザー: {test_message}")
    response = generate_response(test_message)
    print(f"AI: {response}")