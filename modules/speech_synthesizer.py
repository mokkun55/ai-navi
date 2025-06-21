import requests
import json
from playsound import playsound
import os
import config

def speak(text):
    """
    VOICEVOX Engineを使用してテキストを音声に変換し、再生します。

    Args:
        text (str): 読み上げさせたいテキスト。
    """
    host = '127.0.0.1'
    port = '50021'
    speaker_id = config.speaker_id

    # 1. 音声合成用のクエリを作成
    params = {'text': text, 'speaker': speaker_id}
    try:
        response = requests.post(f'http://{host}:{port}/audio_query', params=params)
        response.raise_for_status() # HTTPエラーがあれば例外を発生させる
        query = response.json()
    except requests.exceptions.RequestException as e:
        print(f"音声クエリの作成に失敗しました: {e}")
        print("VOICEVOX Engineが起動しているか、ポート番号が正しいか確認してください。")
        return

    # 2. クエリから音声合成
    try:
        response = requests.post(f'http://{host}:{port}/synthesis', params={'speaker': speaker_id}, data=json.dumps(query))
        response.raise_for_status() # HTTPエラーがあれば例外を発生させる
        voice_data = response.content
    except requests.exceptions.RequestException as e:
        print(f"音声合成に失敗しました: {e}")
        return

    # 3. 音声データを再生
    # playsoundはファイルパスを要求するため、一時ファイルとして保存
    temp_wav_path = "temp_voicevox_output.wav"
    try:
        with open(temp_wav_path, "wb") as f:
            f.write(voice_data)
        playsound(temp_wav_path)
    except Exception as e:
        print(f"音声の再生に失敗しました: {e}")
        print("playsoundライブラリが正しく動作しているか確認してください。")
    finally:
        # 一時ファイルを削除
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

if __name__ == '__main__':
    # 例: 好きな文章を喋らせる
    my_text = input("\n喋らせたい文章を入力してください: ")
    try:
        speak(my_text)
    except ValueError:
        print("無効な話者IDが入力されました。数値で入力してください。")

    print("\nプログラムを終了します。")