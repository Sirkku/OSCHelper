from __future__ import annotations

import translate
from PyQt6.QtGui import QAction


class MyTranslator:
    from_lang: str
    to_lang: str
    tl: translate.Translator
    set_from_zh_action: QAction
    set_from_ko_action: QAction
    set_from_jp_action: QAction
    set_from_auto_action: QAction
    TRANSLATION_ERROR_SAME_LANGUAGE = "PLEASE SELECT TWO DISTINCT LANGUAGES"

    def __init__(self):
        self.from_lang = 'autodetect'
        self.to_lang = 'en'
        self.tl = (translate.Translator(from_lang='zh', to_lang='en'))

        self.set_from_zh_action = QAction("Translate from Chinese")
        self.set_from_zh_action.triggered.connect(lambda: self._set_from_lang("zh"))

        self.set_from_jp_action = QAction("Translate from Japanese")
        self.set_from_jp_action.triggered.connect(lambda: self._set_from_lang("jp"))

        self.set_from_ko_action = QAction("Translate from Korean")
        self.set_from_ko_action.triggered.connect(lambda: self._set_from_lang("ko"))

        self.set_from_auto_action = QAction("Translate from Auto-Detect")
        self.set_from_auto_action.triggered.connect(lambda: self._set_from_lang("autodetect"))

    def _recreate_translator(self):
        self.tl = translate.Translator(
            from_lang=self.from_lang,
            to_lang=self.to_lang
        )

    def _set_from_lang(self, from_lang: str):
        self.from_lang = from_lang
        self._recreate_translator()

    def translate(self, text):
        return self.tl.translate(text)
