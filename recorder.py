import pyaudio
import wave
from pydub import AudioSegment
import os

# --- 設定 ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "temp_audio.wav"
MP3_OUTPUT_FILENAME = "record_result_tmp.mp3"

# --- グローバル変数 ---
is_recording = False
frames = []
p = None
stream = None
should_quit = False

def audio_callback(in_data, frame_count, time_info, status):
    """pyaudioが録音データを取得した際に呼び出すコールバック関数"""
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)

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
                    frames_per_buffer=CHUNK,
                    stream_callback=audio_callback)
    stream.start_stream()
    print(">>> 録音を開始しました。Enterキーを押すと停止します。")

def stop_recording():
    """録音を停止し、ファイルを保存する。保存したMP3ファイル名を返す。"""
    global p, stream, frames, is_recording
    if not is_recording:
        return None

    print(">>> 録音を停止しました。ファイルを保存しています...")
    is_recording = False

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    try:
        audio = AudioSegment.from_wav(WAVE_OUTPUT_FILENAME)
        audio.export(MP3_OUTPUT_FILENAME, format="mp3")
        print(f">>> '{MP3_OUTPUT_FILENAME}' として保存しました。")
        return MP3_OUTPUT_FILENAME
    except Exception as e:
        print(f"MP3への変換に失敗しました: {e}")
        print("ffmpegがインストールされているか確認してください。")
        return None
    finally:
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            os.remove(WAVE_OUTPUT_FILENAME)

def main():
    """メイン処理"""
    global is_recording, should_quit
    print("--- Python音声録音プログラム ---")
    print("Enterキーを押して録音を開始します。")
    print("録音中に再度Enterキーを押すと録音を停止し、プログラムを終了します。")
    print("'q'と入力してEnterキーを押すとプログラムを終了します。")
    print("------------------------------------")

    while not should_quit:
        command = input()
        if command.lower() == 'q':
            if is_recording:
                stop_recording()
            should_quit = True
            print(">>> プログラムを終了します。")
        elif not is_recording:
            start_recording()
        else:
            saved_filename = stop_recording()
            if saved_filename:
                print(f"保存されたファイル名: {saved_filename}")
            should_quit = True # 録音完了で終了
            print(">>> 録音を完了し、プログラムを終了します。")

if __name__ == '__main__':
    main() 