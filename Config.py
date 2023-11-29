import json
import os
import PyPDF2

tools = [
  {
    "type": "function",
    "function": {
      "name": "create_load",
      "description": "create a load based on info in rate confirmation",
      "parameters": {
        "type": "object",
        "properties": {
          "load_customer": {
            "type": "object",
            "properties": {
              "customer_company_name": {"type": "string", "description": "The name of the broker/shipper company"},
              "contact_person_first_name": {"type": "string", "description": "The first name of the broker contact person"},
              "contact_person_last_name": {"type": "string", "description": "The last name of the broker contact person"},
              "contact_email": {"type": "string", "description": "The email of the broker contact person."},
              "contact_number": {"type": "string", "description": "The phone number of the broker contact."}
            }
          },
          "equipment_type": {"type": "string", "enum": ["FLATBED", "FLATBED_HOTSHOT", "VAN_HOTSHOT", "VAN_SPECIALIZED", "VAN_STANDARD", "STRAIGHT_VAN", "REEFER", "CONTAINER", "DRY_BULK", "TANKER", "REMOVABLE_GOOSENECK", "DECKS_SPECIALIZED", "DECKS_STANDARD", "CONESTOGA", "ANY", "HAZARDOUS_MATERIALS", "POWER_ONLY", "OTHER_EQUIPMENT"]},
          "equipment_length": {"type": "number", "description": "Load equipment length(ft.)"},
          "reference": {"type": "string", "description": "load's reference ID"},
          "weight": {"type": "number", "description": "load's max weight"},
          "rate": {"type": "number", "description": "Load price,unit:$"},
          "note": {"type": "string", "description": "Important notes about the load."},
          "pickup_info": {
            "type": "object",
            "properties": {
              "business_name": {"type": "string", "description": "The company name of the location point"},
              "contact_number": {"type": "string", "description": "contact number of the location"},
              "location_name": {"type": "string", "description": "the city, state and zipcode of location"},
              "location_street": {"type": "string", "description": "The street of the location"},
              "time_range": {
                "type": "object",
                "properties": {
                  "start_time": {"type": "string", "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"},
                  "end_time": {"type": "string", "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"}
                }
              },
              "site_instruction": {"type": "string", "description": "Instructions for driver about that location"}
            }
          },
          "stop_points": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "business_name": {"type": "string", "description": "The company name of the location point"},
                "contact_number": {"type": "string",
                                   "description": "contact number of that location"},
                "location_name": {"type": "string", "description": "the city, state and zipcode of location"},
                "location_street": {"type": "string", "description": "The street of the location"},
                "time_range": {
                  "type": "object",
                  "properties": {
                    "start_time": {"type": "string",
                                   "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"},
                    "end_time": {"type": "string",
                                 "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"}
                  }
                },
                "site_instruction": {"type": "string", "description": "Instructions for driver about that location"}
              }
            }
          },
          "dropoff_info": {
            "type": "object",
            "properties": {
              "business_name": {"type": "string", "description": "The company name of that location"},
              "contact_number": {"type": "string",
                                 "description": "contact number of that location"},
              "location_name": {"type": "string", "description": "the city, state and zipcode of location"},
              "location_street": {"type": "string", "description": "The street of the location"},
              "time_range": {
                "type": "object",
                "properties": {
                  "start_time": {"type": "string",
                                 "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"},
                  "end_time": {"type": "string",
                               "description": "follow the format ISO 8601, like this: 2022-08-15T05:00:00.000+0000"}
                }
              },
              "site_instruction": {"type": "string", "description": "The site instruction of the location point."}
            }
          }
        }
      }
    }
  }
]


sample_json = '''{
  "load_customer": {
    "customer_company_name": "C.H. Robinson",
    "contact_person_first_name": null,
    "contact_person_last_name": null,
    "contact_email": "LoadDocs@chrobinson.com",
    "contact_number": "866-581-0813."
  },
  "equipment_type": "Van",
  "equipment_length": 53,
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
      "start_time": "2022-06-28T08:00:00.000+0000",
      "end_time": "2022-06-28T15:00:00.000+0000"
    },
    "site_instruction": null
  },
  "dropoff_info": {
    "business_name": "Helena INDUSTRIES",
    "contact_number": "770-945-0686",
    "location_name": "Suwanee, GA 30024",
    "location_street": "3211 Shawnee Industrial",
    "time_range": {
      "start_time":  "2022-06-29T08:00:00.000+0000",
      "end_time": "2022-06-29T16:00:00.000+0000"
    },
    "site_instruction": null
  }
}'''

prompt = '''
You are a helpful assistant designed to extract info from US fleet's rate confirmation pdf to specified JSON. You will follow these rules:
1. When you can't find an answer, just put null, don't make things up.
2. Don't generate anything other than Json, always follow the sample’s format.
3. If there’s multi-stop in rate confirmation, just add an array called stops, schema is the same as pickup and dropoff.
4. if the schedule time in pickup/drop off/stop is a fixed appointment, just fill pickup time, drop off time is null.
5. The format for the phone number is XXX-XXX-XXXX, no parentheses, no country prefix, and no extension number.
'''


def read_pdf(file_path):
  with open(file_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
      text += page.extract_text() + "\n"
  return text






def compare_dicts(dict1, dict2, weights):
  """
  Recursively compare two dictionaries and calculate weighted matching ratio.
  """
  all_keys = set(dict1.keys()) | set(dict2.keys())
  total_weight = 0
  matching_weight = 0

  for key in all_keys:
    weight = weights.get(key, 1)  # 默认权重为1

    # 对嵌套字典递归调用
    if isinstance(dict1.get(key), dict) and isinstance(dict2.get(key), dict):
      nested_weight, nested_matching = compare_dicts(dict1[key], dict2[key], weights)
      total_weight += nested_weight
      matching_weight += nested_matching
    else:
      total_weight += weight
      if dict1.get(key) == dict2.get(key):
        matching_weight += weight

  return total_weight, matching_weight


def compare_jsons_and_calculate_ratio(json_str_list1, json_str_list2, weights):
  total_weight = 0
  matching_weight = 0

  # 遍历JSON字符串数组
  for json_str1, json_str2 in zip(json_str_list1, json_str_list2):
    json_str1 = json_str1.replace("\n", "")
    json_str2 = json_str2.replace("\n", "")
    dict1 = json.loads(json_str1)
    dict2 = json.loads(json_str2)

    # 比较字典并计算权重
    weight, matching = compare_dicts(dict1, dict2, weights)
    total_weight += weight
    matching_weight += matching

  matching_ratio = matching_weight / total_weight if total_weight else 0

  # 将比例转换为JSON字符串输出
  result_json_str = json.dumps({"matching_ratio": matching_ratio})
  print(f"matching weight is {matching_weight}, total weight is {total_weight}")
  return result_json_str


# 设置权重
weights = {'notes': 0, 'site_instruction': 0}
