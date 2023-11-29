# 测试1： GPT-4V直接读文档
from openai import OpenAI
import json
client = OpenAI()
SampleJson = '''{
  "load_customer": {
    "customer_company_name": "C.H. Robinson",
    "contact_person_first_name": "",
    "contact_person_last_name": "",
    "contact_email": "LoadDocs@chrobinson.com",
    "contact_number": "866-581-0813."
  },
  "equipment_type": "Van",
  "equipment_length": "53",
  "reference": "402493667",
  "weight": 40000,
  "rate": 900,
  "notes": "Fax POD to 866-746-1562 immediately upon delivery! Thanks!",
  "pickup_info": {
    "business_name": "Bulloch Fertilizer Co",
    "contact_number": "912-764-9084",
    "location_name": "STATESBORO, GA 30458",
    "location_street": "15 Blitch Lane",
    "time_range": {
      "start_time": 1656403200000,
      "end_time": 1656428400000
    },
    "site_instruction": ""
  },
  "dropoff_info": {
    "business_name": "Helena INDUSTRIES",
    "contact_number": "770-945-0686",
    "location_name": "Suwanee, GA 30024",
    "location_street": "3211 Shawnee Industrial",
    "time_range": {
      "start_time":  1656489600000,
      "end_time": 1656518400000
    },
    "site_instruction": ""
  }
}'''
serialized_json = json.dumps(SampleJson)
def extract():
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content":"You are a Json extractor for a US fleet company. You will receive Rate Confirmation from broker, and your job is extract info from image to the following Json format. When you can't find an answer, just put null, don't make things up. Also don't generate anything other than json."
            },
            {
                "role": "user",
                "content": [
                    # 下面这行一会注释掉看看，可以的话就不传text msg了
                    {"type": "text", "text": f"this is an exapmle, the json extracted is: {serialized_json}"},
                    {
                        "type": "image_url", "image_url": {"url":"https://raw.githubusercontent.com/Andrew-ppppeng/Explore-LLM-in-COMMAND/main/1-1.png"},
                    },
                    {
                        "type": "image_url", "image_url": {"url": "https://raw.githubusercontent.com/Andrew-ppppeng/Explore-LLM-in-COMMAND/main/1-2.png"},
                    },
                    # {
                    #     "type": "image_url", "image_url": {"url": "https://raw.githubusercontent.com/Andrew-ppppeng/Explore-LLM-in-COMMAND/main/1-3.png", "detail":"high"},
                    # }
                ],
            },
            # {
            #     "role": "assistant",
            #     "content": serialized_json
            # },
            {
                "role": "user",
                "content":[
                    {
                        "type":"text",
                        "text": "extract info in this img to json, follow the format above"
                    },
                    {
                        "type": "image_url",
                        # "image_url": img_url
                        "image_url": {"url": "https://raw.githubusercontent.com/Andrew-ppppeng/Explore-LLM-in-COMMAND/main/2-1.jpg"}
                    },
                    {
                        "type": "image_url", "image_url": {"url":"https://raw.githubusercontent.com/Andrew-ppppeng/Explore-LLM-in-COMMAND/main/2-2.jpg"}
                    }
                ]
            }
        ],

        max_tokens=2000,
    )
    return response

R = extract()

print(R)





# print(response.choices[0])



# 测试2： 用langchain转换
# from langchain.document_loaders import PyPDFLoader
#
# loader = PyPDFLoader("doc1175398954.pdf")
# pages = loader.load_and_split()


