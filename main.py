import gradio as gr
import time
import config
from modules import transcriber, llm_handler, speech_synthesizer

def create_ui():
    """GradioのUIを作成し、イベントハンドラを定義する。"""

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

    def voice_chat(audio_path, chat_history):
        """
        音声入力からAI応答までの処理を行う。
        UIの状態を `yield` を使って段階的に更新する。
        """
        # 処理中は入力ボタンを無効化
        yield {
            status_text: "【ステータス】ユーザーの音声を文字に変換しています...",
            chatbot: chat_history,
            response_audio: None,
            audio_input: gr.Audio(interactive=False),
        }

        # 1. 文字起こし
        start_time = time.time()
        if config.is_bypass_whisper:
            user_text = config.bypass_text
            print(f"Whisperをスキップしました。入力テキスト: '{user_text}'")
        else:
            if audio_path is None:
                yield {
                    status_text: "【ステータス】エラー：音声が録音されていません。",
                    chatbot: chat_history,
                    audio_input: gr.Audio(interactive=True) # ボタンを有効化
                }
                return
            user_text = transcriber.transcribe_audio(audio_path)

        end_time = time.time()
        print(f"ユーザー入力: '{user_text}' (文字起こし時間: {end_time - start_time:.2f}秒)")

        if not user_text:
            yield {
                status_text: "【ステータス】エラー：音声の文字起こしに失敗しました。無音だったか、ノイズが大きすぎる可能性があります。",
                chatbot: chat_history,
                audio_input: gr.Audio(interactive=True) # ボタンを有効化
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
                audio_input: gr.Audio(interactive=True) # ボタンを有効化
            }
            return

        # 3. 応答生成
        yield {
            status_text: "【ステータス】AIが応答を考えています...",
            chatbot: chat_history,
        }
        start_time = time.time()
        # LLMに渡すために履歴の形式を変換
        history_for_llm = convert_history_for_llm(chat_history[:-1]) # 最新のユーザー発言は除く
        ai_response = llm_handler.generate_response(user_text, history_for_llm)
        end_time = time.time()
        print(f"AI応答: '{ai_response}' (応答生成時間: {end_time - start_time:.2f}秒)")
        chat_history.append({"role": "assistant", "content": ai_response})

        # 4. 音声合成
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
                audio_input: gr.Audio(interactive=True) # ボタンを有効化
            }
            return

        # 5. UIを最終状態に更新し、音声を再生
        yield {
            status_text: "【ステータス】準備完了。マイクボタンを押して話しかけてください。",
            chatbot: chat_history,
            response_audio: gr.Audio(value=output_audio_path, autoplay=True),
            audio_input: gr.Audio(value=None, interactive=True), # ボタンを有効化し、入力をクリア
        }

    def clear_session():
        """会話履歴とステータスを初期化する。"""
        initial_status = "【ステータス】準備完了。マイクボタンを押して話しかけてください。"
        print("--- セッションをリセットしました ---")
        return [], initial_status, None

    with gr.Blocks(title="AI音声対話アプリ", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# AI音声対話アプリ")
        gr.Markdown("下のマイクボタンを押し、話し終わったらもう一度押して録音を終了してください。AIが応答します。")

        chatbot = gr.Chatbot(label="会話ログ", height=400, type="messages")
        status_text = gr.Textbox(
            "【ステータス】準備完了。マイクボタンを押して話しかけてください。",
            label="現在の状態",
            interactive=False
        )
        
        with gr.Row():
            audio_input = gr.Audio(
                sources=["microphone"], 
                type="filepath", 
                label="音声入力",
                scale=3, # ボタンを大きく表示
            )
            clear_button = gr.Button("セッションを終了する", scale=1)

        # 自動再生用の非表示コンポーネント
        response_audio = gr.Audio(label="AIの応答", autoplay=True, visible=False)

        # イベントリスナー
        audio_input.stop_recording(
            voice_chat,
            inputs=[audio_input, chatbot],
            outputs=[status_text, chatbot, response_audio, audio_input],
        )
        
        clear_button.click(
            clear_session,
            inputs=[],
            outputs=[chatbot, status_text, response_audio],
        )

    return demo

if __name__ == "__main__":
    app = create_ui()
    app.launch()