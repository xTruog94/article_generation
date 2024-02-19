class APIConfig:
    log_filename = "logs/api.log"
    log_format = "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    log_filemode = "w+"
    host = "0.0.0.0"
    port = 8000
    
class ChatGPTConfig:
    api = "https://opengpts-example-vz4y4ooboq-uc.a.run.app/runs/stream"
    cookie = 'opengpts_user_id=2871570f-833c-46bc-b26a-46dff7e594cd'
    assistant_id="e5785e8a-7acc-4337-89fc-70b80c24bc6c"