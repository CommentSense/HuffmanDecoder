"""
    Author: Valentin Becerra
    CS4364: Data Protection
"""


class HuffDecompressor:
    """-----------------------------------------------------------------------
    Class that decompresses file compressed using the Huffman algorithm.

    Attributes
    ----------
    huff_mapping : dict
        Dictionary containing huffman code and character pairs
    char_list: list
        Contains a list of all characters that will be used to decompress file
    map_size: int
        Contains the length of the huff_mapping which is the same as characters
    bit_string : str
        String containing the bit sequence of the huffman compressed file
    tree_index : int
        Determine the start of the flattened binary tree
    leaf_index : int
        Used so we can keep track of what character to access on the list during post-order traversal
    bit_string_index: int
        Used so we can keep track of the last accessed bit in the bit sequence

    -----------------------------------------------------------------------"""

    huff_mapping: dict = {}
    char_list: list = []
    map_size: int
    bit_string: str
    tree_index: int
    leaf_index: int = 0
    bit_string_index: int = 0

    def __init__(self, path: str):
        """
        Initializer for the HuffmanDecompressor

        Parameters
        ----------
        path: str
            path variable to the file being decompressed

        """
        # turn file into bit sequence
        self.init_bit_string(path)

        # calculate map size and the index that the flattened tree starts at
        self.map_size = int(self.bit_string[:8], 2)
        self.tree_index = 8 * (self.map_size + 2)

        # extract characters from the first bytes of the compressed file and update current index
        char_segment = self.bit_string[8: 8 * self.tree_index]
        self.extract_chars(char_segment)
        self.bit_string_index = self.tree_index

    def init_bit_string(self, path: str):
        """
        This method converts the file given in bytes into a bit sequence
        Parameters
        ----------
        path: str
            path variable to the file being read
        """
        size = 0
        with open(path, 'rb') as file:
            self.bit_string = ""
            byte = file.read(1)

            # convert bytes to bits
            while (len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                self.bit_string += bits
                byte = file.read(1)
                size += 1

    def extract_chars(self, char_bit_string: str):
        """
        Extract characters from byte in the bit string sequence

        Parameters
        ----------
        char_bit_string: str
            string containing sequence of encoded bits
        """
        start = 0
        # read bit string in bytes
        for i in range(8, len(char_bit_string) + 1, 8):
            character = chr(int(char_bit_string[start: i], 2))
            # if the character already exists in the list do not add it again
            if character in self.char_list:
                start += 8
                continue
            else:
                self.char_list.append(character)
                start += 8

    def decode(self, remove: str = None):
        """
        This method created the map from the flattened binary tree in the bit sequence the uses the map to decoded the
        rest of the message.

        Parameters
        ----------
        remove: str
            string we wish to remove ie: \n, \r, since these sometimes come in pairs.
        """

        self.create_map()

        # remove the trailing padding from the flattened binary tree
        if len(self.bit_string[self.bit_string_index:]) % 8 != 0:
            self.bit_string_index += len(self.bit_string[self.bit_string_index:]) % 8

        # extract message and write it to a file
        message = self.encode_message(remove)
        with open('decode.txt', 'w') as output:
            output.write(message)

        print('Message Decoded')

    def create_map(self, code: str = "", branch: bool = False):
        """
        Recursive method used to read the flatted binary string in post-order

        Parameters
        ----------
        code: str
            Contains the binary string traversal from root to leaf
        branch: bool
            used to more sure we check both branches of a node

        Return
        ------
        branch: bool
            boolean that determines if we have finished traversing a branch
        """

        if self.bit_string[self.bit_string_index] == '1' and not branch:
            self.huff_mapping[code] = self.char_list[self.leaf_index]
            self.leaf_index += 1
            # we have reached a left leaf, return true to check right side
            return True
        elif self.bit_string[self.bit_string_index] == '1' and branch:
            self.huff_mapping[code] = self.char_list[self.leaf_index]
            self.leaf_index += 1
            # we have reached both leaves, return false to go back up the tree
            return False
        else:
            # left branch
            self.bit_string_index += 1
            branch = self.create_map(code + '0')

            # right branch
            self.bit_string_index += 1
            self.create_map(code + '1', branch)

    def encode_message(self, remove):
        """
        This methods read the bit sequence and check the mapping to see if the sequence matches a character key

        Parameters
        ----------
        remove: chr
            character we wish to omit decoding

        Return
        ------
        message: str
            decoded message
        """

        key = ""
        message = ""
        encoded_text = self.bit_string[self.bit_string_index:]
        for bit in encoded_text:
            # keep concatenating bit until we find a matching key
            key += bit
            if (key in self.huff_mapping):
                # use huffman code key to get character
                character = self.huff_mapping[key]

                # terminating symbol found. stop encoding
                if character == 'ï':
                    message += '\n'
                    return message
                # remove character we don't want to add to message
                elif character == remove:
                    key = ""
                    continue

                message += character
                key = ""

        return message


if __name__ == "__main__":
    huffman = HuffDecompressor("compressed1.bin")
    huffman.decode(remove='\r')
