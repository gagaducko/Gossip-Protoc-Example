import socket
from threading import Thread, Lock
import time
from datetime import datetime


class GossipNode:
    def __init__(self, port, connected_nodes):
        # create a new socket
        self.node = socket.socket(type=socket.SOCK_DGRAM)
        self.counter = 0
        self.time_transmitted = ''
        self.previous_message = ''
        self.received_messages = []
        
        # 为共享资源添加锁
        self.lock = Lock()
        
        # set hostname and port
        self.hostname = socket.gethostname()
        self.port = port
        self.node.bind((self.hostname, self.port))
        self.susceptible_nodes = connected_nodes
        self.start_threads()

    def input_message(self):
        while True:
            if self.counter == 0:
                self.print_info(f"[input] Setup the Node and the Port is: [{self.port}]")
                self.counter += 1

            message_to_send = input("Please Enter a message you to send: ")
            self.transmit_message(message_to_send.encode('ascii'))

    def receive_message(self):
        while True:
            try:
                message_to_forward, address = self.node.recvfrom(1024)

                with self.lock:
                    # 检查是否接收到重复的消息
                    if self.previous_message == message_to_forward:
                        continue
                    self.previous_message = message_to_forward

                previous_node = address[1]

                # 收到消息的处理
                self.print_info(f"Received message: '{message_to_forward.decode('ascii')[19:]}' From [{address[1]}]")
                self.print_info(f"Now forwarding to: {self.susceptible_nodes}")
                self.relay_message(message_to_forward, previous_node)

            except ConnectionResetError as e:
                # 处理远程主机关闭连接的错误
                self.print_error(f"Connection reset by peer. Error: {str(e)}")
            except Exception as e:
                # 处理其他未知错误
                self.print_error(f"An unexpected error occurred: {str(e)}")

    def transmit_message(self, message):
        # 记录消息的时间戳
        self.message_timestamp = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        message = self.message_timestamp + message.decode('ascii')

        with self.lock:
            self.previous_message = message.encode('ascii')

        # Transmit message to all susceptible nodes
        self.print_info(f"Transmitting message: '{message}'")
        for selected_port in self.susceptible_nodes:
            self.node.sendto(message.encode(), (self.hostname, selected_port))
            self.print_info(f"Message sent to port {selected_port} at {self.get_current_timestamp()}")

    def relay_message(self, message, previous_node=0):
        """转发消息，并检查目标节点是否可达"""
        for selected_port in self.susceptible_nodes:
            try:
                # 尝试发送消息，如果目标节点不可达则会抛出异常
                self.node.sendto(message, (self.hostname, selected_port))
                self.print_info(f"Message relayed to node on port {selected_port} at {self.get_current_timestamp()}")
            except OSError as e:
                # 如果发送失败，输出错误信息
                self.print_error(f"Failed to forward message to port {selected_port}. Error: {str(e)}")

    def start_threads(self):
        Thread(target=self.input_message).start()
        Thread(target=self.receive_message).start()

    def print_info(self, message):
        """统一输出格式化的消息"""
        print(f"[INFO] {self.get_current_timestamp()} - {message}")

    def print_warning(self, message):
        """用于输出警告信息"""
        print(f"[WARNING] {self.get_current_timestamp()} - {message}")

    def print_error(self, message):
        """用于输出错误信息"""
        print(f"[ERROR] {self.get_current_timestamp()} - {message}")

    def get_current_timestamp(self):
        """获取当前时间戳，格式化输出"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
