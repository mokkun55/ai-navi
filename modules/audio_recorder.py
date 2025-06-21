import pyaudio
import wave
from pydub import AudioSegment
import os
import config

# --- 設定 (config.pyから読み込む) ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
TEMP_WAVE_FILENAME = "temp_audio.wav"

def record_audio():
    """
    録音を開始し、ユーザーがEnterキーを押すと録音を停止してMP3に保存する。
    """
    p = pyaudio.PyAudio()
    frames = []

    def audio_callback(in_data, frame_count, time_info, status):
        frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=audio_callback)

    stream.start_stream()
    print(">>> 録音を開始しました。Enterキーを押すと停止します。")

    input() # ユーザーがEnterキーを押すのを待つ

    print(">>> 録音を停止しました。ファイルを保存しています...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(TEMP_WAVE_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    try:
        audio = AudioSegment.from_wav(TEMP_WAVE_FILENAME)
        audio.export(config.input_file, format="mp3")
        print(f">>> '{config.input_file}' として保存しました。")
    except Exception as e:
        print(f"MP3への変換に失敗しました: {e}")
        print("ffmpegがインストールされているか確認してください。")
    finally:
        if os.path.exists(TEMP_WAVE_FILENAME):
            os.remove(TEMP_WAVE_FILENAME)

if __name__ == '__main__':
    record_audio() 