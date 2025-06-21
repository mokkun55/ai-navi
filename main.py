import gradio as gr
import time
import config
from modules import transcriber, llm_handler, speech_synthesizer

def create_ui():
    """のUIを作成し、イベントハンドラを定義する。"""

    def convert_history_for_llm(chat_history):
        """GradioのMessage形式の履歴を、LLM Handlerが期待する形式に変換する。"""
        history_for_llm = []
        for message in chat_history:
            if message["role"] == "user":
                # 新しいユーザーメッセージのペアを開始
                history_for_llm.append([message["content"], None])
            elif message["role"] == "assistant":
                # 直前のユーザーメッセージに応答を追加
                if history_for_llm:
                    history_for_llm[-1][1] = message["content"]
        return history_for_llm

    def chat_handler(user_input, chat_history):
        """
        ユーザーの入力（テキストまたは音声）を処理し、AIの応答を生成する。
        """
        if isinstance(user_input, str):
            # テキスト入力の場合
            user_text = user_input
            print(f"ユーザー入力 (テキスト): '{user_text}'")
            # テキスト入力時は入力コンポーネントを即座に有効化
            yield {
                text_input: gr.Textbox(interactive=True, value=""), 
                audio_input: gr.Audio(interactive=True)
            }
        else: # 音声入力の場合 (user_input is a filepath)
            # 処理中は入力ボタンを無効化
            yield {
                status_text: "【ステータス】ユーザーの音声を文字に変換しています...",
                chatbot: chat_history,
                response_audio: None,
                audio_input: gr.Audio(interactive=False),
                text_input: gr.Textbox(interactive=False),
            }
            # 1. 文字起こし
            start_time = time.time()
            user_text = transcriber.transcribe_audio(user_input)
            end_time = time.time()
            print(f"ユーザー入力 (音声): '{user_text}' (文字起こし時間: {end_time - start_time:.2f}秒)")

            if not user_text:
                yield {
                    status_text: "【ステータス】エラー：音声の文字起こしに失敗しました。",
                    chatbot: chat_history,
                    audio_input: gr.Audio(interactive=True), # ボタンを有効化
                    text_input: gr.Textbox(interactive=True), # ボタンを有効化
                }
                return

        chat_history.append({"role": "user", "content": user_text})

        # 終了キーワードのチェック
        if user_text in ["さようなら", "バイバイ", "終了", "さよなら"]:
            farewell = "会話を終了します。ご利用ありがとうございました。"
            chat_history.append({"role": "assistant", "content": farewell})
            yield {
                status_text: f"【ステータス】{farewell}",
                chatbot: chat_history,
                audio_input: gr.Audio(interactive=True),
                text_input: gr.Textbox(interactive=True, value=""),
            }
            return

        # 応答生成
        yield {
            status_text: "【ステータス】AIが応答を考えています...",
            chatbot: chat_history,
        }
        start_time = time.time()
        history_for_llm = convert_history_for_llm(chat_history[:-1])
        ai_response = llm_handler.generate_response(user_text, history_for_llm)
        end_time = time.time()
        print(f"AI応答: '{ai_response}' (応答生成時間: {end_time - start_time:.2f}秒)")
        chat_history.append({"role": "assistant", "content": ai_response})

        # 音声合成
        yield {
            status_text: "【ステータス】AIの応答を音声に変換しています...",
            chatbot: chat_history,
        }
        start_time = time.time()
        output_audio_path = speech_synthesizer.synthesize_speech_to_file(ai_response, config.response_audio_file)
        end_time = time.time()
        print(f"音声合成完了 (音声合成時間: {end_time - start_time:.2f}秒)")

        if output_audio_path is None:
            yield {
                status_text: "【ステータス】エラー：音声合成に失敗しました。",
                chatbot: chat_history,
                audio_input: gr.Audio(interactive=True),
                text_input: gr.Textbox(interactive=True, value=""),
            }
            return

        # UIを最終状態に更新
        yield {
            status_text: "【ステータス】準備完了。マイクボタンかテキスト入力で話しかけてください。",
            chatbot: chat_history,
            response_audio: gr.Audio(value=output_audio_path, autoplay=True),
            audio_input: gr.Audio(value=None, interactive=True),
            text_input: gr.Textbox(value="", interactive=True),
        }

    def clear_session():
        """会話履歴とステータスを初期化する。"""
        initial_status = "【ステータス】準備完了。マイクボタンかテキスト入力で話しかけてください。"
        print("--- セッションをリセットしました ---")
        return [], initial_status, None, ""


    with gr.Blocks(title="AI音声対話アプリ", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# AI音声対話アプリ")
        gr.Markdown("マイクボタンで音声入力、または下のテキストボックスに入力してEnterキーを押してください。")

        chatbot = gr.Chatbot(label="会話ログ", height=400, type="messages")
        status_text = gr.Textbox(
            "【ステータス】準備完了。マイクボタンかテキスト入力で話しかけてください。",
            label="現在の状態",
            interactive=False
        )
        
        with gr.Row():
            audio_input = gr.Audio(
                sources=["microphone"], 
                type="filepath", 
                label="音声入力",
            )
        
        with gr.Row():
            text_input = gr.Textbox(
                label="テキスト入力",
                placeholder="ここにメッセージを入力してEnter",
                scale=4,
            )
            clear_button = gr.Button("セッションを終了する", scale=1)

        # 自動再生用の非表示コンポーネント
        response_audio = gr.Audio(label="AIの応答", autoplay=True, visible=False)

        # イベントリスナー
        audio_input.stop_recording(
            chat_handler,
            inputs=[audio_input, chatbot],
            outputs=[status_text, chatbot, response_audio, audio_input, text_input],
        )

        text_input.submit(
            chat_handler,
            inputs=[text_input, chatbot],
            outputs=[status_text, chatbot, response_audio, audio_input, text_input],
        )
        
        clear_button.click(
            clear_session,
            inputs=[],
            outputs=[chatbot, status_text, response_audio, text_input],
        )

    return demo

if __name__ == "__main__":
    app = create_ui()
    app.launch()