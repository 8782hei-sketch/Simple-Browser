from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Daftar sederhana domain tracker dan iklan untuk diblokir
        self.blocked_domains = [
            'doubleclick.net',
            'google-analytics.com',
            'googlesyndication.com',
            'adservice.google.com',
            'analytics.yahoo.com',
            'scorecardresearch.com',
            'quantserve.com',
            'zedo.com',
            'adbrite.com',
            'bidadx.com',
            'criteo.com',
            'outbrain.com',
            'taboola.com'
        ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return
