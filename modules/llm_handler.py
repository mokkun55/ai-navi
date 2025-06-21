import lmstudio as lms
import config

# グローバル変数としてモデルとチャットセッションを保持
model = None
chat_session = None

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
    対話の履歴を記憶し、文脈に応じた応答を返す。

    Args:
        user_text (str): ユーザーからの入力テキスト。

    Returns:
        str: LLMからの応答テキスト。
    """
    global chat_session
    initialize_model()

    if not model:
        return "LM Studioモデルの初期化に失敗しました。"

    # チャットセッションがなければ初期化
    if chat_session is None:
        print("新しいチャットセッションを開始します。")
        chat_session = lms.Chat(config.system_prompt)

    try:
        # ユーザーのメッセージをチャットに追加
        chat_session.add_user_message(user_text)

        # 応答を生成（ここでチャット履歴が送信される）
        response = model.respond(chat_session)
        
        # --- 対話履歴の管理 ---
        # 履歴が設定した最大数を超えた場合、古いものから削除する
        # Chatオブジェクトの内部構造を仮定しています
        if hasattr(chat_session, 'messages'):
            # システムプロンプトは常に保持する
            system_prompt = chat_session.messages[0]
            
            # ユーザーとAIの対話履歴のみを対象にする
            conversation_messages = chat_session.messages[1:]

            # 制限数を超えていれば、古い履歴を削除
            max_len = config.MAX_HISTORY * 2
            if len(conversation_messages) > max_len:
                # 最新の `max_len` 件のメッセージを残す
                conversation_messages = conversation_messages[-max_len:]
            
            # 履歴を再構築
            chat_session.messages = [system_prompt] + conversation_messages

        return response
    except Exception as e:
        return f"応答生成中にエラーが発生しました: {e}"

if __name__ == '__main__':
    # テスト用
    # 連続で呼び出して履歴が機能するか確認
    print("--- 1回目の対話 ---")
    test_message_1 = "こんにちは！何かおすすめの屋台はありますか？"
    print(f"ユーザー: {test_message_1}")
    response_1 = generate_response(test_message_1)
    print(f"AI: {response_1}")

    print("\n--- 2回目の対話 ---")
    test_message_2 = "たこ焼き以外でお願いします。"
    print(f"ユーザー: {test_message_2}")
    response_2 = generate_response(test_message_2)
    print(f"AI: {response_2}")
    
    if chat_session and hasattr(chat_session, 'messages'):
        print(f"\n現在のチャット履歴 ({len(chat_session.messages)}件):")
        for msg in chat_session.messages:
            print(f"- {msg}")