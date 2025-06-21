import lmstudio as lms
import config

# グローバル変数としてモデルを保持（セッションは関数内で管理）
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

def generate_response(user_text, history):
    """
    ユーザーのテキストと対話履歴に対してLLMからの応答を生成する。

    Args:
        user_text (str): ユーザーからの最新の入力テキスト。
        history (list): GradioのChatbot形式の対話履歴のリスト。
                        例: [["ユーザー1", "AI1"], ["ユーザー2", "AI2"]]

    Returns:
        str: LLMからの応答テキスト。
    """
    initialize_model()

    if not model:
        return "LM Studioモデルの初期化に失敗しました。"

    # Gradioの履歴からLM Studioのチャットセッションを構築
    chat_session = lms.Chat(config.system_prompt)
    for user_msg, ai_msg in history:
        if user_msg:
            chat_session.add_user_message(user_msg)
        if ai_msg:
            chat_session.add_assistant_response(ai_msg)

    try:
        # ユーザーの最新のメッセージをチャットに追加
        chat_session.add_user_message(user_text)

        # 応答を生成
        response = model.respond(chat_session)
        
        # model.respondの戻り値はオブジェクトの可能性があるため、明示的に文字列に変換
        return str(response)
    except Exception as e:
        return f"応答生成中にエラーが発生しました: {e}"

if __name__ == '__main__':
    # テスト用
    print("--- 1回目の対話 ---")
    test_history_1 = []
    test_message_1 = "こんにちは！何かおすすめの屋台はありますか？"
    print(f"ユーザー: {test_message_1}")
    response_1 = generate_response(test_message_1, test_history_1)
    print(f"AI: {response_1}")

    print("\n--- 2回目の対話 ---")
    test_history_2 = [[test_message_1, response_1]]
    test_message_2 = "たこ焼き以外でお願いします。"
    print(f"ユーザー: {test_message_2}")
    response_2 = generate_response(test_message_2, test_history_2)
    print(f"AI: {response_2}")
    
    # 3回目の対話で履歴が正しく引き継がれているか確認
    print("\n--- 3回目の対話 ---")
    test_history_3 = test_history_2 + [[test_message_2, response_2]]
    test_message_3 = "では、その特徴を教えてください。"
    print(f"ユーザー: {test_message_3}")
    response_3 = generate_response(test_message_3, test_history_3)
    print(f"AI: {response_3}")