TEST_CHAT_ID = 123456  # Ваш chat_id
await context.bot.send_message(
    chat_id=TEST_CHAT_ID,
    text=f"[TEST] {message_text}",
    parse_mode='HTML'
)