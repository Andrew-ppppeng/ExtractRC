from openai import OpenAI
from Config import sample_json, prompt, tools, compare_jsons_and_calculate_ratio, read_pdf, weights
import os
from RC.Ideal_answer import String
client = OpenAI()



sample_pdf_text = read_pdf("doc1175398954.pdf")
pdf_filepaths = []
for filename in os.listdir('RC'):
  if filename.endswith('.pdf'):
    # 构造完整的文件路径
    pdf_filepaths.append(os.path.join("RC", filename))
target_pdf_text = []
for path in pdf_filepaths:
  target_pdf_text.append(read_pdf(path))


response = []
complete_token = 0
prompt_token = 0

for text in target_pdf_text:
    result = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            # model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"this is an example of pdf info:{sample_pdf_text}"},
                {"role": "user", "content": f"this is an example of json{sample_json}"},
                {"role": "user",
                 "content": f"take a deep breath, think step by step, extract this pdf into json, following the format above. pdf content is:{text}"}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "create_load"}},
            temperature=0
    )
    response.append(result.choices[0].message.tool_calls[0].function.arguments)
    complete_token += result.usage.completion_tokens
    prompt_token += result.usage.prompt_tokens




result_json_str = compare_jsons_and_calculate_ratio(response, String, weights)
print(f"Output JSON with weighted matching ratio: {result_json_str}")
print(f"\ncomplete token:{complete_token}")
print(f"\nprompt token: {prompt_token}")
