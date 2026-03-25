import random
import time

def string_to_bits(data):
    return ''.join(format(ord(c), '08b') for c in data)


def bits_to_string(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)


def random_noise(bits, probability=0.1):
    noisy = ''
    for b in bits:
        if random.random() < probability:
            noisy += '1' if b == '0' else '0'
        else:
            noisy += b
    return noisy


def burst_noise(bits, burst_length=3):
    bits = list(bits)
    start = random.randint(0, len(bits)-burst_length)
    for i in range(start, start+burst_length):
        bits[i] = '1' if bits[i] == '0' else '0'
    return ''.join(bits)


def parity_bit(bits):
    ones = bits.count('1')
    return bits + ('0' if ones % 2 == 0 else '1')


def check_parity(bits):
    return bits.count('1') % 2 == 0


def hamming_encode(data):
    d = list(data)
    p1 = str(int(d[0]) ^ int(d[1]) ^ int(d[3]))
    p2 = str(int(d[0]) ^ int(d[2]) ^ int(d[3]))
    p4 = str(int(d[1]) ^ int(d[2]) ^ int(d[3]))
    return p1 + p2 + d[0] + p4 + d[1] + d[2] + d[3]


def hamming_decode(bits):
    b = list(bits)
    p1 = int(b[0]) ^ int(b[2]) ^ int(b[4]) ^ int(b[6])
    p2 = int(b[1]) ^ int(b[2]) ^ int(b[5]) ^ int(b[6])
    p4 = int(b[3]) ^ int(b[4]) ^ int(b[5]) ^ int(b[6])

    error = p4*4 + p2*2 + p1

    if error != 0:
        print(f"Error detected at position {error}")
        b[error-1] = '1' if b[error-1] == '0' else '0'

    return ''.join([b[2], b[4], b[5], b[6]])


class Frame:
    def __init__(self, src, dest, data):
        self.src = src
        self.dest = dest
        self.data = data

    def show(self):
        print(f"Frame | SRC: {self.src} | DEST: {self.dest} | DATA: {self.data}")


class Device:
    def __init__(self, name):
        self.name = name
        self.links = []

    def connect(self, link):
        self.links.append(link)


class EndDevice(Device):

    def send(self, dest, message):
        print(f"\n{self.name} sending data to {dest.name}: {message}")

        bits = string_to_bits(message)
        print("Bits:", bits)

        bits = parity_bit(bits)
        print("After parity:", bits)

        frame = Frame(self.name, dest.name, bits)
        frame.show()

        for link in self.links:
            link.transmit(frame, self)

    def receive(self, frame):
        print(f"{self.name} received frame from {frame.src}")

        corrupted = random_noise(frame.data, 0.05)

        if corrupted != frame.data:
            print("Noise detected in transmission")

        if check_parity(corrupted):
            print("No error detected")
            data = bits_to_string(corrupted[:-1])
            print(f"Data received: {data}")
        else:
            print("Error detected! Requesting retransmission")


class Switch(Device):

    def __init__(self, name):
        super().__init__(name)
        self.mac_table = {}

    def receive(self, frame, source):
        print(f"\n{self.name} received frame from {source.name}")

        self.mac_table[frame.src] = source

        print("MAC Table:", self.mac_table)

        if frame.dest in self.mac_table:
            dest_device = self.mac_table[frame.dest]
            print(f"Forwarding frame directly to {frame.dest}")
            dest_device.receive(frame)
        else:
            print("Unknown destination -> Broadcasting")
            for link in self.links:
                device = link.other(self)
                if device != source:
                    device.receive(frame)


class Link:
    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2
        d1.connect(self)
        d2.connect(self)

    def other(self, device):
        return self.d2 if device == self.d1 else self.d1

    def transmit(self, frame, sender):
        time.sleep(0.5)
        receiver = self.other(sender)

        if isinstance(receiver, Switch):
            receiver.receive(frame, sender)
        else:
            receiver.receive(frame)


def csma_cd_simulation():
    print("\nSimulating CSMA/CD")

    channel_busy = random.choice([True, False])

    if channel_busy:
        print("Channel busy -> waiting")
        time.sleep(1)
        print("Channel free now -> transmitting")
    else:
        print("Channel free -> transmitting")


def stop_and_wait(sender, receiver, message):
    print("\nFlow Control: Stop and Wait")

    for char in message:
        print(f"Sending frame: {char}")
        sender.send(receiver, char)
        print("Waiting for ACK")
        time.sleep(1)
        print("ACK received\n")


if __name__ == "__main__":

    print("DATA LINK LAYER SIMULATOR")

    A = EndDevice("A")
    B = EndDevice("B")
    C = EndDevice("C")
    D = EndDevice("D")
    E = EndDevice("E")

    S = Switch("Switch1")

    Link(A, S)
    Link(B, S)
    Link(C, S)
    Link(D, S)
    Link(E, S)

    csma_cd_simulation()

    msg = input("Enter data to send: ")

    stop_and_wait(A, B, msg)
