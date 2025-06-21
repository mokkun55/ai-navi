import whisper
import config

# グローバル変数としてモデルを保持
model = None

def initialize_model():
    """
    Whisperモデルを初期化する。
    """
    global model
    if model is None:
        print("Whisperモデルをロードしています...")
        model = whisper.load_model(config.whisper_model)
        print("Whisperモデルのロードが完了しました。")

def transcribe_audio(audio_path):
    """
    指定された音声ファイルを文字起こしする。

    Args:
        audio_path (str): 音声ファイルのパス。

    Returns:
        str: 文字起こし結果のテキスト。
    """
    initialize_model()

    if not model:
        return "Whisperモデルの初期化に失敗しました。"
        
    try:
        result = model.transcribe(audio_path, fp16=False) # macではfp16=Trueはエラーになることがある
        return result['text']
    except Exception as e:
        return f"文字起こし中にエラーが発生しました: {e}"

if __name__ == '__main__':
    # テスト用
    # このファイル単体で実行した場合の動作
    text = transcribe_audio(config.input_file)
    print("--- 文字起こし結果 ---")
    print(text) 