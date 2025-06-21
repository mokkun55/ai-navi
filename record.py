import pyaudio
import wave
# import keyboard # keyboardは不要になります
from pydub import AudioSegment
import os
import time
import threading # スレッドを利用して録音中の入力を受け付けます

# --- 設定 ---
FORMAT = pyaudio.paInt16  # 音声のフォーマット
CHANNELS = 1              # モノラル
RATE = 44100              # サンプルレート
CHUNK = 1024              # 録音するデータの塊のサイズ
WAVE_OUTPUT_FILENAME = "temp_audio.wav"
MP3_OUTPUT_FILENAME = "audio.mp3"
# START_STOP_KEY = "s"      # 不要になります
# QUIT_KEY = "q"            # 不要になります

# --- グローバル変数 ---
is_recording = False
frames = []
p = None
stream = None
should_quit = False # 終了フラグ

def start_recording():
    """録音を開始する"""
    global p, stream, frames, is_recording
    if is_recording:
        return

    is_recording = True
    frames = []
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print(">>> 録音を開始しました。Enterキーを押すと停止します。")

    # 録音データを別スレッドで収集
    thread = threading.Thread(target=record_audio)
    thread.start()

def record_audio():
    """音声データを収集するスレッド関数"""
    global stream, frames, is_recording
    while is_recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except (IOError, OSError):
            break

def stop_recording():
    """録音を停止し、ファイルを保存する"""
    global p, stream, frames, is_recording
    if not is_recording:
        return

    print(">>> 録音を停止しました。ファイルを保存しています...")
    is_recording = False

    stream.stop_stream()
    stream.close()
    p.terminate()

    # WAVファイルとして一時保存
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # WAVをMP3に変換
    try:
        audio = AudioSegment.from_wav(WAVE_OUTPUT_FILENAME)
        audio.export(MP3_OUTPUT_FILENAME, format="mp3")
        print(f">>> '{MP3_OUTPUT_FILENAME}' として保存しました。")
    except Exception as e:
        print(f"MP3への変換に失敗しました: {e}")
        print("ffmpegがインストールされているか確認してください。")
    finally:
        # 一時WAVファイルを削除
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            os.remove(WAVE_OUTPUT_FILENAME)

def main():
    """メイン処理"""
    global is_recording, should_quit
    print("--- Python音声録音プログラム ---")
    print("Enterキーを押して録音を開始/停止します。")
    print("'q'と入力してEnterキーを押すとプログラムを終了します。")
    print("------------------------------------")

    while not should_quit:
        command = input() # ユーザーの入力を待つ
        if command.lower() == 'q':
            if is_recording:
                stop_recording()
            should_quit = True
            print(">>> プログラムを終了します。")
        elif not is_recording:
            start_recording()
        else:
            stop_recording()

if __name__ == '__main__':
    main() 