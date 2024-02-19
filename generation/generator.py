from uuid import uuid4
import random
import requests
import time
import json

class PromptGenerate():
    
    def __init__(self, api, cookie, assistant_id, max_retry= 10):
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
                            article1 = article1,
                            article2 = article2,
                            article3 = article3
                            ),
                        "additional_kwargs": {},
                        "type": "human",
                        "example": False
                    }
                ],
            "assistant_id": self.assistant_id,
            "thread_id": thread_id
        }

    def new_thread_id(self, num_ids = 10):
        uuids = []
        for i in range(num_ids):
            uuids.append(str(uuid4()))
        return random.choice(uuids)

    def renew_thread_id(self):
        self.thread_id = self.new_thread_id(10)
        
    def process(self, response):
        response = response[-5]
        response = response.replace("data: ","")
        response = json.loads(response)["messages"][-1]["additional_kwargs"]["agent"]["return_values"]["output"]
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
            if message_response is  not None and message_response['type'] == 'ai':
                break
            else:
                message_response = None
            print(self.thread_id)
            print(f"The 'messages' key not in response. Retrying ({i}/{self.max_retry})...")
            time.sleep(3)
        return message_response
    
    def get_response(self, article1, article2, article3):
        message_response = None
        for i in range(self.max_retry):
            
            message_response = self._get_response(article1, article2, article3, self.thread_id)
            if message_response is None:
                self.renew_thread_id()
            else:
                break
        if message_response is not None:
            text = message_response['content']
            if "```" in text:
                text = text.replace("```json","")
                text = text.replace("```","")
            return json.loads(text)
        else:
            return None

