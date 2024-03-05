Start date 2024-03-04 10:57

---
> I define which endpoint to send the query by using the mixtral-tiny model, giving it the role of a classifier. 
>> prompt for student - You are a smart message classifier.
    Your task is to classify messages into one of 3 categories by assigning them labels 1, 2, or 3.
    Important! Each message must include a link to TikTok. If there is no link, ask the user to provide it.
    assign [1] if the user in his message means TikTok account.
    assign [2] if the user in his message means song or sound.
    assign [3] if the user in his message means prediction by sound or song. 
    Limit your answer to a maximum of 20 words and always follow the format [assigned class][your answer].
    My prompt is |{text}|
> 
>> prompt for teacher - You are a teacher who checks your student's assignment to categorize messages,
    where [1] is account analytics, [2] is music or sound analytics, [3] is predictions on sound or music.
    Answer in the format [assigned label] only.
    Look at this message and identify the class.
    MESSAGE = |{user_history[-1]}|
- https://mistral.ai/
---
### Problems I've encountered
> Not all the prompts were classified correctly.
- Solution: Added another check as if the teacher who has to agree or disagree with the student, if not I take the teacher's clasification.
 
> Sending graphs to the user via websockets was difficult
- Solution: I store html graphics locally, overwriting the content each time the user prompts and uploading it via url_for
---

### How to run
If you want run locally 
1. Create python virtual env
2. Clone this in folder repo git clone link
3. run pip install -r requirements.txt
4. run main.py and default access will be in http://127.0.0.1:5000

If you want run docker container
1. docker pull mggen/test_copilot
2. docker run -d -p 5000:5000 mggen/test_copilot
