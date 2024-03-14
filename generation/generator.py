from uuid import uuid4
import random
import requests
import time
import json
from openai import OpenAI
import os
import textwrap
import google.generativeai as genai
from memoization import cached
import markdown

class PromptGenerate():

    def __init__(self, api, cookie, assistant_id, max_retry=10):
        self.api = api
        self.max_retry = max_retry
        self.header = {"Cookie": cookie}
        self.assistant_id = assistant_id
        self.instruction = """
            Bạn sẽ tổng hợp thông tin về cùng 1 chủ đề từ các bài viết dưới đây. Nếu có một bài khác chủ đề với các bài còn lại, bài đấy sẽ bị loại bỏ. Viết lại một bài viết mới hoàn toàn từ các thông tin được cho trong các bài dưới đây. Các bài viết này phải tốt cho SEO.
            \n\n\n Bài viết 1: {article1}
            \n\n\n Bài viết 2: {article2} 
        """
        self.thread_id = self.new_thread_id(10)

    def payload(self, article1, article2, article3, thread_id):
        return {
            "input":
                [
                    {
                        "content": self.instruction.format(
                            article1=article1,
                            article2=article2,
                            article3=article3
                        ),
                        "additional_kwargs": {},
                        "type": "human",
                        "example": False
                    }
                ],
            "assistant_id": self.assistant_id,
            "thread_id": thread_id
        }

    def new_thread_id(self, num_ids=10):
        uuids = []
        for i in range(num_ids):
            uuids.append(str(uuid4()))
        return random.choice(uuids)

    def renew_thread_id(self):
        self.thread_id = self.new_thread_id(10)

    def process(self, response):
        response = response[-5]
        response = response.replace("data: ", "")
        response = json.loads(response)[
            "messages"][-1]["additional_kwargs"]["agent"]["return_values"]["output"]
        return response

    def _get_response(self, article1, article2, article3, thread_id):
        message_response = ''
        for i in range(self.max_retry):
            body = self.payload(article1, article2, article3, thread_id)
            response = requests.post(self.api, json=body, headers=self.header)
            print(response.status_code)
            for line in list(response.iter_lines())[::-1]:
                if line.decode('utf-8').startswith("data: ["):
                    message_response = json.loads(line.decode('utf-8')[6:])[-1]
                    break
            if message_response is not None and message_response['type'] == 'ai':
                break
            else:
                message_response = None
            print(self.thread_id)
            print(
                f"The 'messages' key not in response. Retrying ({i}/{self.max_retry})...")
            time.sleep(3)
        return message_response

    @cached(ttl=60)
    def get_response(self, article1, article2, article3):
        message_response = None
        for i in range(self.max_retry):

            message_response = self._get_response(
                article1, article2, article3, self.thread_id)
            if message_response is None:
                self.renew_thread_id()
            else:
                break
        if message_response is not None:
            text = message_response['content']
            if "```" in text:
                text = text.replace("```json", "")
                text = text.replace("```", "")
            return json.loads(text), 200
        else:
            return None, 500


class GPTAssistant():

    def __init__(self, api_key, assistant_id, thread_id=None, max_retry=3):
        self.max_retry = max_retry
        os.environ['OPENAI_API_KEY'] = api_key
        self.assistant_id = assistant_id
        self.instruction = """
            Bạn sẽ tổng hợp thông tin về cùng 1 chủ đề từ các bài viết dưới đây. Nếu có một bài khác chủ đề với các bài còn lại, bài đấy sẽ bị loại bỏ. Viết lại một bài viết mới hoàn toàn từ các thông tin được cho trong các bài dưới đây. Các bài viết này phải tốt cho SEO.
            \n\n\n Bài viết 1: {article1}
            \n\n\n Bài viết 2: {article2} 
        """
        self.thread_id = thread_id
        self.client = OpenAI()

    def create_new_thread(self):
        thread = self.client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": "hi"

            }]
        )
        self.thread_id = thread.id

    def process(self, response):
        response = response[-5]
        response = response.replace("data: ", "")
        response = json.loads(response)[
            "messages"][-1]["additional_kwargs"]["agent"]["return_values"]["output"]
        return response

    def wait_for_run_completion(self, run_id, sleep_interval=5, max_runtime=600):
        """
        Waits for a run to complete
        :param thread_id: The ID of the thread.
        :param run_id: The ID of the run.
        :param sleep_interval: Time in seconds to wait between checks.
        """
        response = None
        s = time.time()
        response = "An error occurred while retrieving the run"
        status_code = 500
        while True:
            try:
                if time.time()-s > max_runtime:
                    break
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id, run_id=run_id)
                if run.completed_at:
                    messages = self.client.beta.threads.messages.list(
                        thread_id=self.thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    status_code = 200
                    break
                time.sleep(sleep_interval)
            except Exception as e:
                response = str(e)
                break
        return response, status_code

    def _crop(self, *args, max_length=512):
        response = tuple()
        for arg in args:
            response = (*response, " ".join(arg.split()[:max_length]))
        return args

    @cached(ttl=60)
    def get_response(self, article1, article2, article3):
        message_response = None
        article1, article2, article3 = self._crop(
            article1, article2, article3, max_length=512)
        message_input = self.instruction.format(
            article1=article1, article2=article2, article3=article3)
        self.thread_id if self.thread_id is not None else self.create_new_thread()
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=message_input
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        message_response, status_code = self.wait_for_run_completion(run.id)
        if status_code == 200:
            if "```" in message_response:
                text = text.replace("```json", "")
                text = text.replace("```", "")
            return json.loads(text), 200
        else:
            return message_response, 500


class GeminiAssistant():

    def __init__(self, api_key, max_retry=3, **generation_config):
        self.max_retry = max_retry
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)
        # self.instruction = """
        #     Bạn sẽ tổng hợp thông tin về cùng 1 chủ đề từ các bài viết dưới đây. Nếu có một bài khác chủ đề với các bài còn lại, bài đấy sẽ bị loại bỏ. Viết lại một bài viết mới hoàn toàn từ các thông tin được cho trong các bài dưới đây. Các bài viết này phải tốt cho SEO.
        #     Câu trả lời của bạn sẽ ở dạng json với format: {{"title":"Chủ đề bài viết", "sapo":"Tóm tắt nội dung bài viết trong 2-3 câu", "content":"Nội dung chính của bài viết"}}. Phần nội dung chính của bài viết có định dạng html với các đầu mục là thẻ h3
        #     \n\n\n Bài viết 1: {article1}
        #     \n\n\n Bài viết 2: {article2}
        #     \n\n\n Câu trả lời của bạn: \n
        # """
        self.instruction = """
            Bạn sẽ viết lại bài viết dưới đây theo một cách viết mới hoàn toàn dựa trên những thông tin cho trước. Các bài viết này phải tốt cho SEO. Câu trả lời có độ dài 5000 ký tự.
            Câu trả lời của bạn có format với tên và giải thích như sau:***
            Tiêu đề: chủ đề của bài viết
            
            Tóm tắt: tóm tắt nội dung bài viết trong 2-3 câu
            
            Nội dung: nội dung chính của bài viết ở dạng html với các đầu mục là thẻ h3
            ***
            \n\n\n Bài viết cho trước: {article1}
            \n\n\n Câu trả lời của bạn: \n
        """
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 1,
            "max_output_tokens": 5000,
        }
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        self.client = genai.GenerativeModel(model_name="gemini-pro",
                                            generation_config=self.generation_config,
                                            safety_settings=self.safety_settings)

    def process(self, response):
        response = response[-5]
        response = response.replace("data: ", "")
        response = json.loads(response)[
            "messages"][-1]["additional_kwargs"]["agent"]["return_values"]["output"]
        return response

    def _crop(self, *args, max_length=512):
        response = tuple()
        for arg in args:
            response = (*response, " ".join(arg.split()[:max_length]))
        return args

    @cached(ttl=60)
    def get_response(self, article1, article2, article3):
        message_response = None
        # article1, article2, article3 = self._crop(article1, article2, article3, max_length = 512)
        message_input = self.instruction.format(
            article1=article1, article2=article2, article3=article3)
        convo = self.client.start_chat(history=[])
        convo.send_message(message_input)
        text = convo.last.text
        title = ""
        sapo = ""
        content = ""
        text = text.split("**Nội dung:**")
        content = markdown.markdown(text[1])
        ts = text[0]
        title_sapo = ts.split("**Tóm tắt:**")
        sapo = title_sapo[1]
        title = title_sapo[0]
        title = title.replace("Tiêu đề:","").replace("*","").replace("\n","")
        sapo = sapo.replace("Tóm tắt:","").replace("*","").replace("\n","")
        text_object = {
            "title": title,
            "sapo": sapo,
            "content": content
        }
        if text is not None:
            return text_object, 200
        else:
            return message_response, 500
