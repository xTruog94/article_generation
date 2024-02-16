import re

class Cleaner():
    
    def __init__(self):
        return
    
    def clean_raw_html(self, html_string):
        clean_html = re.sub(r'<script.*?</script>', '', html_string, flags=re.DOTALL)
        clean_html = re.sub(r'<script\s+.*\s+>', '', clean_html)
        cleanr = re.compile(r'<[^>]+>|<.*?>|&nbsp;|&amp;|&lt|p&gt|\u260e|<STYLE>(.*?)<\/STYLE>|<style>(.*?)<\/style>')
        text = re.sub(cleanr, ' ', clean_html)
        text = re.sub(r'https?://\S+', '', text)
        text = text.replace("\'","")
        return text

    def clean_space(self, text):
        if text is not None:
            text = re.sub("\t+","\n",text)
            text = re.sub("\n+","\n",text)
            text = re.sub("\s+", " ",text)
        return text
    
    def clean(self, text):
        if text is not None:
            text = self.clean_raw_html(text)
        text = self.clean_space(text)
        return text