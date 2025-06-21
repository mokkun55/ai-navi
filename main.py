import time
import config
from modules import audio_recorder, transcriber, llm_handler, speech_synthesizer

def main():
    """
    音声対話アプリケーションのメイン処理。
    """
    print("--- 音声対話を開始します ---")
    print("会話を終了したいときは、「さようなら」または「終了」と言ってください。")

    while True:
        # 1. 音声録音
        print("\n--- 1. 音声録音 ---")
        audio_recorder.record_audio()
        print("録音完了")

        # 2. 文字起こし
        print("--- 2. 文字起こし ---")
        start_time = time.time()
        if config.is_bypass_whisper:
            user_text = config.bypass_text
            print(f"Whisperをスキップしました。入力テキスト: '{user_text}'")
        else:
            user_text = transcriber.transcribe_audio(config.input_file)
        end_time = time.time()
        print(f"ユーザー入力: '{user_text}'")
        print(f"(文字起こし時間: {end_time - start_time:.2f}秒)")

        # 終了キーワードのチェック
        if user_text in ["さようなら", "バイバイ", "終了", "さよなら"]:
            print("--- 会話を終了します ---")
            break

        # 3. 応答生成
        print("--- 3. 応答生成 ---")
        start_time = time.time()
        ai_response = llm_handler.generate_response(user_text)
        end_time = time.time()
        print(f"AI応答: '{ai_response}'")
        print(f"(応答生成時間: {end_time - start_time:.2f}秒)")

        # 4. 音声合成
        print("--- 4. 音声合成 ---")
        start_time = time.time()
        speech_synthesizer.speak(ai_response)
        end_time = time.time()
        print(f"(音声合成時間: {end_time - start_time:.2f}秒)")

if __name__ == "__main__":
    main()