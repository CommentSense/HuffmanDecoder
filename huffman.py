'''
    Valentin Becerra
    CS4364: Data Protection

'''


class HuffDecompressor:
    huff_mapping: dict = {}
    characters: list = []
    map_size: int
    bit_string: str
    tree_index: int
    leaf_index: int = 0
    bit_string_index: int = 0

    def __init__(self, path: str):
        self.init_bit_string(path)
        self.map_size = int(self.bit_string[:8], 2)
        self.tree_index = 8 * (self.map_size + 2)
        char_segment = self.bit_string[8: 8 * self.tree_index]
        self.extract_chars(char_segment)
        self.bit_string_index = self.tree_index

    def init_bit_string(self, path: str):
        size = 0
        with open(path, 'rb') as file:
            bit_string = ""

            byte = file.read(1)

            # convert bytes to bits
            while (len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
                size += 1

        self.bit_string = bit_string

    def extract_chars(self, char_bit_string: str):
        start = 0
        for i in range(8, len(char_bit_string) + 1, 8):
            character = chr(int(char_bit_string[start: i], 2))
            if character in self.characters:
                start += 8
                continue
            else:
                self.characters.append(character)
                start += 8

    def decode(self):
        self.create_map()
        if len(self.bit_string[self.bit_string_index:]) % 8 != 0:
            self.bit_string_index += len(self.bit_string[self.bit_string_index:]) % 8

        print(self.bit_string[self.bit_string_index:])
        message = self.encode_message()
        with open('decode.txt', 'w') as output:
            output.write(message)

        print('Message Decoded')

    def create_map(self, code: str = "", branch: bool = False):
        if self.bit_string[self.bit_string_index] == '1' and not branch:
            self.huff_mapping[code] = self.characters[self.leaf_index]
            self.leaf_index += 1
            return True
        elif self.bit_string[self.bit_string_index] == '1' and branch:
            self.huff_mapping[code] = self.characters[self.leaf_index]
            self.leaf_index += 1
            return False
        else:
            self.bit_string_index += 1
            branch = self.create_map(code + '0')

            self.bit_string_index += 1
            self.create_map(code + '1', branch)

    def encode_message(self):
        key = ""
        message = ""
        encoded_text = self.bit_string[self.bit_string_index:]
        print(self.bit_string_index)
        for bit in encoded_text:
            # keep concatenating bit until we find a matching key
            key += bit
            if (key in self.huff_mapping):
                # use huffman code key to get character
                character = self.huff_mapping[key]
                print(character, end='')
                message += character
                key = ""

        return message


if __name__ == "__main__":
    huffman = HuffDecompressor("compressed.bin")
    huffman.decode()
