

import sys
import socket
import json
import time
import winreg
import subprocess
import threading
import os
import netifaces as ni
from zeroconf import ServiceBrowser, Zeroconf
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QTimer,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QMessageBox, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(369, 339)
        self.Idle_B = QPushButton(Dialog)
        self.Idle_B.setObjectName(u"Idle_B")
        self.Idle_B.setGeometry(QRect(60, 180, 51, 24))
        self.Statement_E = QLineEdit(Dialog)
        self.Statement_E.setObjectName(u"Statement_E")
        self.Statement_E.setGeometry(QRect(130, 110, 61, 20))
        self.Statement_T = QLabel(Dialog)
        self.Statement_T.setObjectName(u"Statement_T")
        self.Statement_T.setGeometry(QRect(50, 110, 71, 16))
        self.Title_T = QLabel(Dialog)
        self.Title_T.setObjectName(u"Title_T")
        self.Title_T.setGeometry(QRect(160, 60, 121, 16))
        self.Running_B = QPushButton(Dialog)
        self.Running_B.setObjectName(u"Running_B")
        self.Running_B.setGeometry(QRect(140, 180, 61, 24))
        self.complete_B = QPushButton(Dialog)
        self.complete_B.setObjectName(u"complete_B")
        self.complete_B.setGeometry(QRect(220, 180, 61, 24))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.Idle_B.setText(QCoreApplication.translate("Dialog", u"Idle", None))
        self.Statement_T.setText(QCoreApplication.translate("Dialog", u"Statement", None))
        self.Title_T.setText(QCoreApplication.translate("Dialog", u"Render Farm Client", None))
        self.Running_B.setText(QCoreApplication.translate("Dialog", u"Running", None))
        self.complete_B.setText(QCoreApplication.translate("Dialog", u"complete", None))
    # retranslateUi

class ClientApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setup_connections()

        # 상태를 주기적으로 전송하기 위한 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_periodic_status)
        self.timer.start(2000)  # 2초 간격으로 설정

        self.current_status = "Idle"  # 초기 상태

        self.client_sockets = {}  # 여러 서버에 대한 소켓을 저장하기 위한 딕셔너리
        self.zeroconf = Zeroconf()
        self.start_service_browser()
        threading.Thread(target=self.receive_commands, daemon=True).start()

        # 저장된 모든 서버 정보를 로드하고 각 서버에 연결 시도
        self.connect_to_servers()

    def save_server_info(self, server_name, ip, port):
        # 기존 서버 정보를 유지하면서 새 서버 정보를 추가
        try:
            server_infos = self.load_server_infos()
            server_infos[server_name] = f"{ip}:{port}"
            with open("server_info.txt", "w") as file:
                for name, info in server_infos.items():
                    file.write(f"{name},{info}\n")
            print(f"Server info saved for {server_name}: {ip}:{port}")
        except Exception as e:
            print(f"Failed to save server info: {e}")

    def load_server_info(self):
        # 서버 정보를 파일에서 로드
        if os.path.exists("server_info.txt"):
            try:
                with open("server_info.txt", "r") as file:
                    ip, port = file.read().split(":")
                    return ip, int(port)
            except Exception as e:
                print(f"Failed to load server info: {e}")
                return None, None
        else:
            return None, None

    def load_server_infos(self):
        # 모든 서버 정보를 로드
        server_infos = {}
        if os.path.exists("server_info.txt"):
            try:
                with open("server_info.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(',')
                        if len(parts) == 3:
                            server_infos[parts[0]] = parts[1] + ':' + parts[2]
                return server_infos
            except Exception as e:
                print(f"Failed to load server infos: {e}")
        return server_infos

    def start_service_browser(self):
        valid_ipv4_addresses = []
        interfaces = ni.interfaces()
        for interface in interfaces:
            addr_info = ni.ifaddresses(interface)
            if ni.AF_INET in addr_info:
                ipv4_info = addr_info[ni.AF_INET]
                for addr in ipv4_info:
                    ipv4_addr = addr.get('addr')
                    if ipv4_addr and not ipv4_addr.startswith("127."):
                        valid_ipv4_addresses.append(ipv4_addr)

        if valid_ipv4_addresses:
            self.zeroconf = Zeroconf(interfaces=valid_ipv4_addresses)
            self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)
        else:
            print("No valid IPv4 address found.")
        # "_CFX"를 이름에 포함하는 서비스를 검색
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)


    def update_service(self, zeroconf, type, name, service_info):
        # 서비스가 업데이트되었을 때 호출되는 메서드
        # 현재는 이 메서드가 하는 일이 없지만, 필요에 따라 여기에 로직을 추가할 수 있습니다.
        pass


    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        if "_CFX" in name:
            info = zeroconf.get_service_info(type, name)
            if info:
                server_ip = socket.inet_ntoa(info.addresses[0])
                server_port = info.port
                server_name = name.split('.')[0]  # 서비스 이름을 서버 이름으로 사용
                self.connect_to_server(server_name, server_ip, server_port)

    def connect_to_servers(self):
        server_infos = self.load_server_infos()
        for server_name, info in server_infos.items():
            ip, port = info.split(':')
            self.connect_to_server(server_name, ip, int(port))

    def connect_to_server(self, server_name, ip, port):
        # Check if we're already connected to this server
        if server_name in self.client_sockets:
            print(f"Already connected to {server_name}")
            return

        attempt_count = 0
        while attempt_count < 5:  # Retry up to 5 times
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))
                self.client_sockets[server_name] = client_socket
                print(f"Connected to {server_name} at {ip}:{port}")
                break  # Exit loop on successful connection
            except socket.error as e:
                print(f"Attempt {attempt_count + 1}: Connection Error to {server_name}: {e}")
                attempt_count += 1
                time.sleep(2)  # Wait 2 seconds before retrying

        if attempt_count == 5:
            print(f"Failed to connect to {server_name} after 5 attempts.")

    def setup_connections(self):
        self.ui.Idle_B.clicked.connect(lambda: self.set_status("Idle"))
        self.ui.Running_B.clicked.connect(lambda: self.set_status("Running"))
        self.ui.complete_B.clicked.connect(lambda: self.set_status("Complete"))


    def set_status(self, status):
        self.current_status = status
        self.ui.Statement_E.setText(status)  # 텍스트 필드 업데이트
        self.send_status(status)

    def send_periodic_status(self):
        self.send_status(self.current_status)
    def send_status(self, status):
        if not self.client_sockets:
            print("No server connections, waiting for server discovery...")
            return

        try:
            current_time = time.time()
            message = json.dumps({
                "status": status,
                "hostname": socket.gethostname(),
                "last_update_time": current_time
            })
            for server_name, srv_socket in self.client_sockets.items():
                srv_socket.send(message.encode('utf-8'))
                print(f"Sent status to {server_name}: {status}")
        except socket.error as e:
            print(f"Socket Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def receive_commands(self):
        while True:
            for server_name, client_socket in list(self.client_sockets.items()):
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if data:
                        command = json.loads(data).get("command")
                        if command == "run_houdini":
                            self.run_houdini()
                except ConnectionResetError as e:
                    print(f"Connection was reset by server {server_name}: {e}")
                    self.client_sockets.pop(server_name, None)
                    # 서버 연결 종료 시 Zeroconf 서비스 브라우저 재시작
                    self.restart_zeroconf_browser()
                except Exception as e:
                    print(f"Unexpected error from {server_name}: {e}")
            time.sleep(2)

    def restart_zeroconf_browser(self):
        # Zeroconf 서비스 브라우저 재시작 로직
        if self.browser:
            self.browser.cancel()
            self.zeroconf.close()
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)

    def run_houdini(self):
        houdini_path = self.find_houdini_install_path()
        if houdini_path:
            subprocess.Popen([os.path.join(houdini_path, 'houdini.exe')])

    def find_houdini_install_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, '.hip') as key:
                program_name = winreg.QueryValue(key, None)

            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f'{program_name}\\shell\\open\\command') as key:
                command_path, _ = winreg.QueryValueEx(key, "")
                houdini_bin_path = command_path.split('"')[1]
                houdini_bin_path = '\\'.join(houdini_bin_path.split('\\')[:-1])

                return houdini_bin_path
        except Exception as e:
            print(f"Houdini 실행 파일 경로를 찾는 데 실패했습니다: {e}")
            return None

    def closeEvent(self, event):
        self.zeroconf.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec())
