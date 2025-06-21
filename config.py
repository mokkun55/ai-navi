# --- 設定 ---

# 音声入力設定
is_bypass_whisper = False # 音声データの文字起こしをスキップする場合はTrueにする
bypass_text = "この文化祭でやっている屋台は何がありますか？"
input_file = "record_result_tmp.mp3"  # 音声データのファイルパス

# モデル設定
whisper_model = "small"
lm_model = "gemma-3-4b-it-qat"
speaker_id = 2

# プロンプト設定
with open("prompt.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 対話履歴を記憶する最大数 (ユーザーの発言とAIの応答を1セットとする)
MAX_HISTORY = 5
