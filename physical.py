import matplotlib.pyplot as plt
import networkx as nx
import time

def string_to_bits(data):
    return ''.join(format(ord(char), '08b') for char in data)


def bits_to_string(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def unipolar_nrz(bits):
    return [1 if bit == '1' else 0 for bit in bits]


def nrz_l(bits):
    return [1 if bit == '1' else -1 for bit in bits]


def nrz_i(bits):
    signal = []
    level = -1

    for bit in bits:
        if bit == '1':
            level *= -1
        signal.append(level)

    return signal


def rz(bits):
    signal = []
    for bit in bits:
        if bit == '1':
            signal.extend([1, 0])
        else:
            signal.extend([-1, 0])
    return signal


def manchester(bits):
    signal = []
    for bit in bits:
        if bit == '1':
            signal.extend([1, -1])
        else:
            signal.extend([-1, 1])
    return signal


def diff_manchester(bits):
    signal = []
    level = 1

    for bit in bits:
        if bit == '0':
            level *= -1

        signal.extend([level, -level])
        level = -level

    return signal


def ami(bits):
    signal = []
    level = 1

    for bit in bits:
        if bit == '1':
            signal.append(level)
            level *= -1
        else:
            signal.append(0)

    return signal


def plot_signal(signal, title="Signal"):
    plt.figure()
    plt.step(range(len(signal)), signal, where='post')
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Voltage Level")
    plt.ylim(-2, 2)
    plt.grid(True)
    plt.show()

class Device:
    def __init__(self, name):
        self.name = name
        self.links = []

    def connect(self, link):
        self.links.append(link)

    def receive(self, bits, source):
        pass


class EndDevice(Device):

    def __init__(self, name):
        super().__init__(name)
        self.received_data = None

    def send(self, data, encoding="Manchester"):
        print(f"\n{self.name} is sending data: {data}")

        bits = string_to_bits(data)
        print(f"Bits: {bits}")

        if encoding == "nrz":
            signal = nrz_l(bits)
            plot_signal(signal, "NRZ-L Encoding")
        else:
            signal = manchester(bits)
            plot_signal(signal, "Manchester Encoding")

        for link in self.links:
            link.transmit(bits, self)

    def receive(self, bits, source):
        data = bits_to_string(bits)
        self.received_data = data
        print(f"{self.name} received data from {source.name}: {data}")


class Hub(Device):

    def receive(self, bits, source):
        print(f"{self.name} received signal from {source.name}")

        for link in self.links:
            other = link.other_end(self)
            if other != source:
                link.transmit(bits, self)


class Link:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2

        device1.connect(self)
        device2.connect(self)

    def other_end(self, device):
        if device == self.device1:
            return self.device2
        return self.device1

    def transmit(self, bits, source):
        time.sleep(0.3) 
        destination = self.other_end(source)
        destination.receive(bits, source)


def show_topology(devices, links):
    G = nx.Graph()

    for d in devices:
        G.add_node(d.name)

    for link in links:
        G.add_edge(link.device1.name, link.device2.name)

    plt.figure()
    nx.draw(G, with_labels=True, node_color="lightblue", node_size=2000)
    plt.title("Network Topology")
    plt.show()


def test_case_1():
    print("\nTEST CASE 1: POINT-TO-POINT")

    A = EndDevice("A")
    B = EndDevice("B")

    l1 = Link(A, B)

    show_topology([A, B], [l1])

    A.send("HELLO", encoding="manchester")


def test_case_2():
    print("\nTEST CASE 2: STAR TOPOLOGY USING HUB")

    hub = Hub("Hub1")

    A = EndDevice("A")
    B = EndDevice("B")
    C = EndDevice("C")
    D = EndDevice("D")
    E = EndDevice("E")

    l1 = Link(A, hub)
    l2 = Link(B, hub)
    l3 = Link(C, hub)
    l4 = Link(D, hub)
    l5 = Link(E, hub)

    show_topology([A, B, C, D, E, hub], [l1, l2, l3, l4, l5])

    A.send("DATA", encoding="manchester")


def get_encoding_choice():
    print("Select Line Encoding Technique:")
    print("1. Unipolar NRZ")
    print("2. Polar NRZ-L")
    print("3. Polar NRZ-I")
    print("4. Return-to-Zero (RZ)")
    print("5. Manchester Encoding")
    print("6. Differential Manchester")
    print("7. Bipolar AMI")

    choice = input("Enter your choice (1-7): ")
    return choice


def encode_signal(bits, choice):
    if choice == "1":
        return unipolar_nrz(bits), "Unipolar NRZ"
    elif choice == "2":
        return nrz_l(bits), "Polar NRZ-L"
    elif choice == "3":
        return nrz_i(bits), "Polar NRZ-I"
    elif choice == "4":
        return rz(bits), "Return-to-Zero (RZ)"
    elif choice == "5":
        return manchester(bits), "Manchester Encoding"
    elif choice == "6":
        return diff_manchester(bits), "Differential Manchester"
    elif choice == "7":
        return ami(bits), "Bipolar AMI"
    else:
        print("Invalid choice. Using Manchester by default.")
        return manchester(bits), "Manchester Encoding"


if __name__ == "__main__":

    data = input("Enter data to send: ")

    bits = string_to_bits(data)
    print(f"Binary representation: {bits}")

    choice = get_encoding_choice()

    signal, title = encode_signal(bits, choice)

    plot_signal(signal, title)

    hub = Hub("Hub1")

    A = EndDevice("A")
    B = EndDevice("B")
    C = EndDevice("C")
    D = EndDevice("D")
    E = EndDevice("E")

    l1 = Link(A, hub)
    l2 = Link(B, hub)
    l3 = Link(C, hub)
    l4 = Link(D, hub)
    l5 = Link(E, hub)

    show_topology([A, B, C, D, E, hub], [l1, l2, l3, l4, l5])

    A.send(data, choice)
