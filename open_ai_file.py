import openai as openai

from config import openai_key

openai.api_key = openai_key


async def send_analyzed_report(report: str) -> str:
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Забудь про всі попередні повідомлення. "
                        f"Ти асистен який вміє якісно аналізувати інформацію та складати по цій інформації гарний розписаний звіт, "
                        f"також залишай посилання на фото в тексті звііту, якщо такі є."},
            {"role": "user", "content": f"{report}"}
        ]
    )

    return completion.choices[0].message.content


