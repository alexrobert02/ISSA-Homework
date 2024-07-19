import socket
import select
import pickle
import datetime

from typing import *


class ObjectSocketParams:
    """A class containing parameters for ObjectSocket."""
    OBJECT_HEADER_SIZE_BYTES = 4
    """The size of the object header in bytes."""
    DEFAULT_TIMEOUT_S = 1
    """Default timeout value in seconds."""
    CHUNK_SIZE_BYTES = 1024
    """Size of the data chunks for sending/receiving."""



class ObjectSenderSocket:
    """A class for sending objects over a socket connection."""
    ip: str
    port: int
    sock: socket.socket
    conn: socket.socket
    print_when_awaiting_receiver: bool
    print_when_sending_object: bool

    def __init__(self, ip: str, port: int,
                 print_when_awaiting_receiver: bool = False,
                 print_when_sending_object: bool = False):
        """
        Initialize ObjectSenderSocket.

        Args:
            ip: The IP address to bind the socket.
            port: The port to bind the socket.
            print_when_awaiting_receiver: Whether to print when awaiting receiver connection. Default value is False.
            print_when_sending_object: Whether to print when sending an object. Default value is False.
        """
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.conn = None

        self.print_when_awaiting_receiver = print_when_awaiting_receiver
        self.print_when_sending_object = print_when_sending_object

        self.await_receiver_conection()

    def await_receiver_conection(self):
        """
        Wait for a receiver connection.

        Prints a message when awaiting receiver connection.
        """
        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] awaiting receiver connection...')

        self.sock.listen(1)
        self.conn, _ = self.sock.accept()

        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] receiver connected')

    def close(self):
        """Close the socket connection."""
        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """Check if the socket is connected."""
        return self.conn is not None

    def send_object(self, obj: Any):
        """
        Send an object over the socket connection.

        Args:
            obj: The object to send.
        """
        data = pickle.dumps(obj)
        data_size = len(data)
        data_size_encoded = data_size.to_bytes(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES, 'little')
        self.conn.sendall(data_size_encoded)
        self.conn.sendall(data)
        if self.print_when_sending_object:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] Sent object of size {data_size} bytes.')



class ObjectReceiverSocket:
    """A class for receiving objects over a socket connection."""
    ip: str
    port: int
    conn: socket.socket
    print_when_connecting_to_sender: bool
    print_when_receiving_object: bool

    def __init__(self, ip: str, port: int,
                 print_when_connecting_to_sender: bool = False,
                 print_when_receiving_object: bool = False):
        """
        Initialize ObjectReceiverSocket.

        Args:
            ip: The IP address to connect to.
            port: The port to connect to.
            print_when_connecting_to_sender: Whether to print when connecting to sender.
            print_when_receiving_object: Whether to print when receiving an object.
        """
        self.ip = ip
        self.port = port
        self.print_when_connecting_to_sender = print_when_connecting_to_sender
        self.print_when_receiving_object = print_when_receiving_object

        self.connect_to_sender()

    def connect_to_sender(self):
        """
        Connect to the sender.

        Prints a message when connecting to sender.
        """
        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connecting to sender...')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connected to sender')

    def close(self):
        """Close the socket connection."""
        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """Check if the socket is connected."""
        return self.conn is not None

    def recv_object(self) -> Any:
        """
        Receive an object over the socket connection.

        Returns:
            The received object.
        """
        obj_size_bytes = self._recv_object_size()
        data = self._recv_all(obj_size_bytes)
        obj = pickle.loads(data)
        if self.print_when_receiving_object:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] Received object of size {obj_size_bytes} bytes.')
        return obj

    def _recv_with_timeout(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> Optional[bytes]:
        """
        Receive data with a timeout.

        Args:
            n_bytes: Number of bytes to receive.
            timeout_s: Timeout in seconds.

        Returns:
            Received data or None if timeout occurs.
        """
        rlist, _1, _2 = select.select([self.conn], [], [], timeout_s)
        if rlist:
            data = self.conn.recv(n_bytes)
            return data
        else:
            return None  # Only returned on timeout

    def _recv_all(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> bytes:
        """
        Receive all data.

        Args:
            n_bytes: Number of bytes to receive.
            timeout_s: Timeout in seconds.

        Returns:
            Received data.
        """
        data = []
        left_to_recv = n_bytes
        while left_to_recv > 0:
            desired_chunk_size = min(ObjectSocketParams.CHUNK_SIZE_BYTES, left_to_recv)
            chunk = self._recv_with_timeout(desired_chunk_size, timeout_s)
            if chunk is not None:
                data += [chunk]
                left_to_recv -= len(chunk)
            else:  # no more data incoming, timeout
                bytes_received = sum(map(len, data))
                raise socket.error(f'Timeout elapsed without any new data being received. '
                                   f'{bytes_received} / {n_bytes} bytes received.')
        data = b''.join(data)
        return data

    def _recv_object_size(self) -> int:
        """
        Receive the size of the object.

        Returns:
            Size of the object in bytes.
        """
        data = self._recv_all(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES)
        obj_size_bytes = int.from_bytes(data, 'little')
        return obj_size_bytes

