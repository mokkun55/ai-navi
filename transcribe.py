import time
import whisper

input_file = "test_audio.mp3"  # 音声データのファイルパス
model = whisper.load_model("tiny")  # 使用するモデルを指定する tiny / base / small / medium / large

start_time = time.time()
result = model.transcribe(input_file, fp16=False)  # 音声データの文字起こし fp16はオプションでTrueにすると精度が上がるが、処理時間が長くなる macはTrueにするとエラーが出る
end_time = time.time()
print(result["text"])  # 文字起こし結果の表示
print(f'実行時間: {end_time - start_time} seconds')