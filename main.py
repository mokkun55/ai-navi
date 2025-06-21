import time
import whisper
import lmstudio as lms
import voicevox

# --- 設定 ---

is_bypass_whisper = False # 音声データの文字起こしをスキップする場合はTrueにする
bypass_text = "この文化祭でやっている屋台は何がありますか？"


input_file = "record_result_tmp.mp3"  # 音声データのファイルパス
whisper_model = "small"

speaker_id = 2

lm_model = "gemma-3-4b-it-qat"
system_prompt = """
あなたは文化祭のナビゲーションAIです。文化祭に来場しているユーザーからの質問に、親切かつ正確に答えてください。あなたの主な役割は以下の通りです。

おすすめスポットの案内: ユーザーの興味や状況に合わせて、文化祭のおすすめスポット（例：人気の展示、美味しい食べ物がある場所、見どころのあるイベント会場など）を提案してください。
場所の案内: ユーザーが探している場所（例：トイレ、救護室、特定の教室、出入口など）への道順や位置を具体的に教えてください。
一般的な質問への回答: 文化祭に関する一般的な質問（例：開催時間、パンフレットの入手場所、忘れ物センターなど）にも対応してください。

応答の原則:
解答は100字以内かつ、話し言葉にしてください。最初に名乗る必要はありません。
場所を案内する際は、具体的なランドマークや目印を挙げるとより分かりやすくなります。
もし質問の内容が不明確な場合は、追加で質問して情報を引き出してください。
分からない質問には、正直に「分かりません」と伝え、どこで情報が得られるか（例：会場案内図、近くのスタッフなど）を案内してください。
絵文字の利用は避けてください
時刻は 10:30 ではなく 10時30分 と言ってください

位置情報:
トイレ: このCAI教室を出て右にある(近くにある)
屋台: 
    フランクフルト: 広場右側
    ポップコーン: 広場左側
    バーベキュー: 広場左側
    フルーツサンド: 広場左側
    フルーツサンド: 広場左側
野外ステージ情報:
    10:00~11:00 開幕挨拶
    11:00~12:00 バンド演奏
    12:00~13:00 バンド演奏
    13:00~14:00 餅まきイベント
    14:00~15:00 バンド演奏
    15:00~16:00 吹奏楽部
    16:00~17:00 吹奏楽部

"""

#  --- recorder ---

import recorder

recorder.main()



# --- whisper ---
whisper_model = whisper.load_model(whisper_model)  # 使用するモデルを指定する


start_time = time.time()
if not is_bypass_whisper:
    whisper_result = whisper_model.transcribe(input_file, fp16=False)  # 音声データの文字起こし fp16はオプションでTrueにすると精度が上がるが、処理時間が長くなる macはTrueにするとエラーが出る
else:
    whisper_result = {"text": bypass_text}
end_time = time.time()

print(f"whisper: {whisper_result['text']}")
print(f'whisper実行時間: {end_time - start_time} seconds')

# --- lm-studio ---

lm_model = lms.llm(lm_model)
chat = lms.Chat(system_prompt)
chat.add_user_message(whisper_result["text"])
lm_result = lm_model.respond(chat)
total_end_time = time.time()

print(f"lm-studio: {lm_result}")
print(f"総実行時間: {total_end_time - start_time} seconds")

# --- voicevox ---

voicevox.speak_voicevox(lm_result, speaker_id)