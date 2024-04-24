from __future__ import annotations

from typing import Optional, Callable

import vrchatapi
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, pyqtBoundSignal
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from vrchatapi import TwoFactorEmailCode, TwoFactorAuthCode
from vrchatapi.api import authentication_api
from vrchatapi.exceptions import UnauthorizedException


class AvatarData:
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.user: str = ""
        self.img: Optional[QImage] = None


class VRCApiService(QObject):
    # signals
    logged_in: pyqtBoundSignal = pyqtSignal(bool)

    def __init__(self, network_manager):
        super(QObject, self).__init__()
        self.api_client: Optional[vrchatapi.ApiClient] = None
        self.current_user: Optional[dict] = None
        self.user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
        # "Kvn7604 kevi98@gmx.de OSCHelper/0.2.1"
        self.client_config: vrchatapi.Configuration = vrchatapi.Configuration()
        self.network_manager: QNetworkAccessManager = network_manager

    def interactive_login_user(self):
        """
        Tries to log in the user. On success emits self.logged_in.
        Silences all exceptions deemed to only have been caused by wrong
        Username/Password/2FA Code input,
        the rest are passed through.
        :return:
        """
        self.client_config.username = QInputDialog().getText(None, "Username", "Enter")[0]
        self.client_config.password = QInputDialog().getText(None, "Password", "Enter")[0]

        new_api_client = vrchatapi.ApiClient(self.client_config)
        new_api_client.user_agent = self.user_agent

        auth_api = authentication_api.AuthenticationApi(new_api_client)
        current_user = None

        try:
            current_user = auth_api.get_current_user()
        except UnauthorizedException as e:
            # check if 2FA is requested
            if e.status == 200:
                # if the follow call also throws, the 2FA code was wrong. Refactor later?
                try:
                    if "Email 2 Factor Authentication" in e.reason:
                        auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(
                            QInputDialog().getText(None, "2FA Code", "Enter")[0]
                        ))
                    elif "2 Factor Authentication" in e.reason:
                        auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(
                            QInputDialog().getText(None, "2FA Code", "Enter")[0]
                        ))
                except vrchatapi.exceptions.ApiException as _:
                    self.logged_in.emit(False)
                    return
                current_user = auth_api.get_current_user()
            else:
                # failure wasn't related to 2FA?

                QMessageBox.warning(None, "Error while logging in:", "{}".format(str(e)))
                return
        except vrchatapi.ApiException as e:
            # failure wasn't related to logging in?
            QMessageBox.warning(None, "Error while logging in:", "{}".format(str(e)))
            self.logged_in.emit(False)
            return
        self.current_user = current_user
        self.api_client = new_api_client
        self.logged_in.emit(True)

    def get_current_user(self, cached=True):
        if not cached:
            auth_client = vrchatapi.AuthenticationApi(self.api_client)
            self.current_user = auth_client.get_current_user()
        return self.current_user

    def get_avatar_stuff(self, avatar_id, callback: Callable[[AvatarData], None]) -> None:
        """
        requires a successful call of self.interactive_login_user() before this
        works. Otherwise, this will throw a bunch of exceptions related to not
        being authenticated.
        callback is called after all network communication (avatar json, icon)
        is finished. If the image fetching didn't work, AvatarData.img might
        be None
        """
        result: AvatarData = AvatarData()
        avatar_api = vrchatapi.AvatarsApi(self.api_client)
        avatar_data = avatar_api.get_avatar(avatar_id)
        result.user = self.current_user.id
        result.name = avatar_data.name
        result.id = avatar_id
        # full image is .image_url
        img_url = QUrl(avatar_data.thumbnail_image_url)

        request = self.network_manager.get(QNetworkRequest(img_url))
        request.finished.connect(
            lambda
            req=request,
            s=self,
            res=result,
            cb=callback:
            s.finish_get_avatar_stuff(req, res, cb)
        )
        return

    # noinspection PyMethodMayBeStatic
    def finish_get_avatar_stuff(self, request: QNetworkReply, res: AvatarData, callback):
        if request.error() == QNetworkReply.NetworkError.NoError:
            data = request.readAll()
            image = QImage.fromData(data)
            res.img = image
        else:
            res.img = None
        callback(res)
