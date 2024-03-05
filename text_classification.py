from dotenv import dotenv_values
import requests

config = dotenv_values('.env')

URL = "https://api.mistral.ai/v1/chat/completions"

API_KEY = config['MISTRAL_API_KEY']

user_history = []


def get_data_pattern_for_request_with_headers(text):
    data = {
        "model": "mistral-tiny",
        "messages": [
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.7,
        "top_p": 1,
        "max_tokens": 32,
        "stream": False,
        "safe_prompt": False,
        "random_seed": None
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    return data, headers


def consolidation_check() -> int:
    prompt = f"""
    You are a teacher who checks your student's assignment to categorize messages,
    where [1] is account analytics, [2] is music or sound analytics, [3] is predictions on sound or music.
    Answer in the format [assigned label] only.
    Look at this message and identify the class.
    MESSAGE = |{user_history[-1]}|
    """

    print(prompt)
    data, headers = get_data_pattern_for_request_with_headers(prompt)

    response = requests.post(URL, json=data, headers=headers)

    try:
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
    except (KeyError, requests.HTTPError) as e:
        print("There is an error inside response:")
        print(response)
        raise e
    else:
        try:
            label = int(content[1])
        except (ValueError, IndexError) as e:
            print('Cannot cast label to int or label is missing')
            raise e
        else:
            print('Consolidation label', label)
            return label


def classify(text: str) -> tuple[int, str]:
    global user_history
    '''
    1 -> account analytic,
    2 -> song analytic,
    3 -> prediction
    '''

    user_history.append(text)

    prompt = f"""
    You are a smart message classifier.
    Your task is to classify messages into one of 3 categories by assigning them labels 1, 2, or 3.
    Important! Each message must include a link to TikTok. If there is no link, ask the user to provide it.
    assign [1] if the user in his message means TikTok account.
    assign [2] if the user in his message means song or sound.
    assign [3] if the user in his message means prediction by sound or song. 
    Limit your answer to a maximum of 20 words and always follow the format [assigned class][your answer].
    My prompt is |{text}|
    """

    print(prompt)

    data, headers = get_data_pattern_for_request_with_headers(prompt)

    response = requests.post(URL, json=data, headers=headers)

    try:
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
    except (KeyError, requests.HTTPError) as e:
        print("There is an error inside response:")
        print(response)
        raise e
    else:
        try:
            label = int(content[1])
        except (ValueError, IndexError) as e:
            print('Cannot cast label to int or label is missing')
            raise e
        else:
            content = content[3:]
            print('My label', label)
            consolidation_label = consolidation_check()
            if consolidation_label == label:
                return label, content
            else:
                return consolidation_label, content
