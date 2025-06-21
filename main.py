import time
import config
from modules import audio_recorder, transcriber, llm_handler, speech_synthesizer

def main():
    """
    音声対話アプリケーションのメイン処理。
    """
    total_start_time = time.time()

    # 1. 音声録音
    print("--- 1. 音声録音 ---")
    audio_recorder.record_audio()
    print("録音完了\n")

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
    print(f"(文字起こし時間: {end_time - start_time:.2f}秒)\n")

    # 3. 応答生成
    print("--- 3. 応答生成 ---")
    start_time = time.time()
    ai_response = llm_handler.generate_response(user_text)
    end_time = time.time()
    print(f"AI応答: '{ai_response}'")
    print(f"(応答生成時間: {end_time - start_time:.2f}秒)\n")

    # 4. 音声合成
    print("--- 4. 音声合成 ---")
    start_time = time.time()
    speech_synthesizer.speak(ai_response)
    end_time = time.time()
    print(f"(音声合成時間: {end_time - start_time:.2f}秒)\n")

    total_end_time = time.time()
    print("--- 処理完了 ---")
    print(f"総実行時間: {total_end_time - total_start_time:.2f}秒")

if __name__ == "__main__":
    main()