class APIConfig:
    log_filename = "logs/api.log"
    log_format = "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    log_filemode = "w+"
    host = "0.0.0.0"
    port = 8000