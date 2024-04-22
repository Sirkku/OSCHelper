from __future__ import annotations

import sqlite3

import translate
from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtGui import QAction


class _TranslationTaskSignals(QObject):
    done = pyqtSignal(object)


class _TranslationTask(QRunnable):
    def __init__(self, phrase, tl):
        super().__init__()
        self.phrase = phrase
        self.tl = tl
        self.signals = _TranslationTaskSignals()

    @pyqtSlot()
    def run(self):
        self.signals.done.emit(self.tl.translate(self.phrase))


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
        self.from_lang = 'zh'
        self.to_lang = 'en'
        self.tl = (translate.Translator(from_lang=self.from_lang, to_lang=self.to_lang))

        self.set_from_zh_action = QAction("Translate from Chinese")
        self.set_from_zh_action.triggered.connect(lambda: self._set_from_lang("zh"))

        self.set_from_jp_action = QAction("Translate from Japanese")
        self.set_from_jp_action.triggered.connect(lambda: self._set_from_lang("jp"))

        self.set_from_ko_action = QAction("Translate from Korean")
        self.set_from_ko_action.triggered.connect(lambda: self._set_from_lang("ko"))

        self.set_from_auto_action = QAction("Translate from Auto-Detect")
        self.set_from_auto_action.triggered.connect(lambda: self._set_from_lang("autodetect"))

        self.con = sqlite3.connect('translations.sqlite3')
        self.con.execute(
            """
CREATE TABLE IF NOT EXISTS translation_cache(phrase, translation, from_lang, to_lang);
            """
        )

        self.threadpool = QThreadPool()

    def _recreate_translator(self):
        self.tl = translate.Translator(
            from_lang=self.from_lang,
            to_lang=self.to_lang
        )

    def _set_from_lang(self, from_lang: str):
        self.from_lang = from_lang
        self._recreate_translator()

    def translate(self, text, callback=None):
        """
        Translate the given text with the current settings of the translator.

        Utilizes a sqlite cache and multithreading to prevent freezes
        :param text: Phrase to be translated
        :param callback: callback function called when translation is done.
            It's only argument is the translated text.
        :return: translated text
        """

        cur = self.con.cursor()
        cur.execute("SELECT translation FROM translation_cache WHERE phrase = ? AND from_lang = ? AND to_lang = ?",
                    (text, self.from_lang, self.to_lang)
                    )
        translation = cur.fetchone()
        # translation takes a second, so delegate it to another thread
        if translation is None:
            new_task = _TranslationTask(phrase=text, tl=self.tl)
            new_task.signals.done.connect(
                lambda trans: self._translate_callback(text, trans, self.from_lang, self.to_lang, callback)
            )
            self.threadpool.start(new_task)
        else:
            callback(translation[0])

    def _translate_callback(self, phrase, translation, from_lang, to_lang, callback):
        self.con.execute("INSERT INTO translation_cache VALUES (?, ?, ?, ?)",
                         (phrase, translation, from_lang, to_lang)
                         )
        self.con.commit()
        callback(translation)

