from dotenv import dotenv_values
import requests
import re


config = dotenv_values('.env')

URL = "https://api.mistral.ai/v1/chat/completions"

API_KEY = config['MISTRAL_API_KEY']

user_history = []

PROMPT = """
Imagine you are an assistant in a company based on Spotify and TikTok analytics.
Your goal is to communicate with the customer, but also, you need to recognize their commands,
you need to classify their message into one of these classes <aa> is any analytics or information about the TikTok account,
<sa> is any music analytics, <ps> is popular music on the platform, <pb> is predictions about the popularity of either the account, video or music.
You can assign multiple tags to a post. Your limitations, always reply short and in the format <tags assigned> | [your reply].
{text}
"""


def get_data_pattern_for_request_with_headers(text):
    data = {
        "model": "mistral-tiny",
        "messages": [
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.9,
        "top_p": 0.5,
        "max_tokens": 64,
        "stream": False,
        "safe_prompt": False,
        "random_seed": None
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    return data, headers


def classify(text: str) -> tuple[list[int], str]:
    global user_history

    user_history.append(text)

    prompt = PROMPT.format(text=f"My question is {text}")

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
        labels = recognize_actions(content)
        print("ACTIONS", labels)
        return labels, content


def extend_ai_answer(extend_text) -> str:
    prompt = PROMPT.format(text=extend_text)
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
        return content


def recognize_actions(text) -> list[int]:
    """
        0 -> account analytic,
        1 -> song analytic,
        2 -> prediction
        3 -> top song on platform
    """
    action_to_ix = {
        'aa': 11,
        'sa': 12,
        'pb': 13,
        'ps': 14
    }

    regexp = re.compile(r'^\W*<(.*?)>')
    labels = regexp.findall(text)[0]
    print("LABELS I FOUND IN TEXT", labels)
    try:
        labels = labels.split(',')
        labels = list(map(lambda x: x.rstip(), labels))
    except Exception as e:
        print("EXCEPTION IN SPLITTING LABELS")
        print(e)

    actions = []

    for label in labels:
        if (action := action_to_ix.get(label)) is not None:
            actions.append(action)

    return actions
