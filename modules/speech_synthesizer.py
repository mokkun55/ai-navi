import requests
import json
from playsound import playsound
import os
import config

def synthesize_speech(text):
    """
    VOICEVOX Engineを使用してテキストから音声データを生成します。

    Args:
        text (str): 音声合成したいテキスト。

    Returns:
        bytes: 音声データ。失敗した場合はNone。
    """
    try:
        # 1. 音声合成用のクエリを作成
        params = {'text': text, 'speaker': config.voicevox_speaker_id}
        response_query = requests.post(f'{config.voicevox_url}/audio_query', params=params, timeout=30)
        response_query.raise_for_status()
        query = response_query.json()

        # 2. クエリから音声合成
        response_synth = requests.post(
            f'{config.voicevox_url}/synthesis',
            params={'speaker': config.voicevox_speaker_id},
            data=json.dumps(query),
            timeout=30
        )
        response_synth.raise_for_status()
        return response_synth.content
    except requests.exceptions.RequestException as e:
        print(f"VOICEVOX APIリクエストに失敗しました: {e}")
        print("VOICEVOX Engineが起動しているか、URLやポート、話者IDが正しいか確認してください。")
        return None

def synthesize_speech_to_file(text, filepath):
    """
    テキストを音声合成し、ファイルに保存します。

    Args:
        text (str): 音声合成したいテキスト。
        filepath (str): 保存先のファイルパス。

    Returns:
        str: 保存したファイルパス。失敗した場合はNone。
    """
    voice_data = synthesize_speech(text)
    if voice_data:
        try:
            with open(filepath, "wb") as f:
                f.write(voice_data)
            return filepath
        except IOError as e:
            print(f"音声ファイル '{filepath}' の書き込みに失敗しました: {e}")
            return None
    return None

def speak(text):
    """
    テキストを音声合成して再生します。（一時ファイルを利用）

    Args:
        text (str): 読み上げさせたいテキスト。
    """
    temp_wav_path = "temp_voicevox_output.wav"
    if synthesize_speech_to_file(text, temp_wav_path):
        try:
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
    speak(my_text)
    print("\nプログラムを終了します。")