from __future__ import annotations

from enum import Enum

import vrchatapi
from PIL.ImageQt import QImage
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from vrchatapi import TwoFactorEmailCode, TwoFactorAuthCode
from vrchatapi.api import authentication_api
from vrchatapi.exceptions import UnauthorizedException


class AvatarData:
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.img: QImage | None = None


class VRCApiService(QObject):
    """
    This class provides an interface for accessing the VRC API.
    """
    # signals
    logged_in = pyqtSignal()

    class Login2FAVersion(Enum):
        NONE = 0
        EMAIL_2FA = 1
        EXTERNAL_2FA = 2

    def __init__(self, network_manager):
        super(QObject, self).__init__()
        self.api_client = None
        self.current_user = None
        self.user_agent = "OSC Helper Kvn7604"
        self.client_config = vrchatapi.Configuration()
        self.requested_2fa = VRCApiService.Login2FAVersion.NONE
        self.network_manager: QNetworkAccessManager = network_manager

    def interactive_login_user(self):
        """
        Tries to log in the user. On success emits self.logged_in.
        Silences all excpetions deemed to only have been caused by wrong Username/Password/2FA Code input,
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
                    return
                current_user = auth_api.get_current_user()
            else:
                # failure wasn't related to 2FA?
                QMessageBox.warning(None, "Error while logging in:", "{}".format(str(e)))
                return
        except vrchatapi.ApiException as e:
            # failure wasn't related to logging in?
            QMessageBox.warning(None, "Error while logging in:", "{}".format(str(e)))
            return
        self.current_user = current_user
        self.api_client = new_api_client
        self.logged_in.emit()

    def get_current_user(self, cached=True):
        if not cached:
            auth_client = vrchatapi.AuthenticationApi(self.api_client)
            self.current_user = auth_client.get_current_user()
        return self.current_user

    def get_avatar_stuff(self, avatar_id, callback) -> None:
        result: AvatarData = AvatarData()
        result.id = avatar_id

        avatar_api = vrchatapi.AvatarsApi(self.api_client)
        avatar_data = avatar_api.get_avatar(avatar_id)

        result.name = avatar_data.name
        # full image is .image_url

        img_url = avatar_data.thumbnail_image_url
        request = self.network_manager.get(QNetworkRequest(QUrl(img_url)))
        request.finished.connect(lambda req=request, s=self, res=result, cb=callback: s.finish_get_avatar_stuff(req, res, cb))
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
