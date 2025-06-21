import lmstudio as lms

model = lms.llm("gemma-3-4b-it-qat")
chat = lms.Chat("あなたは猫です。語尾には「にゃ」をつけてください。")
chat.add_user_message("こんにちは！")
result = model.respond(chat)

print(result)