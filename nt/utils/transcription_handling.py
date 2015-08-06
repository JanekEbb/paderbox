import numpy

class CharLabelHandler():
    """ Handles transforming from chars to integers and vice versa

    """

    def __init__(self, transcription_list, add_blank=True):
        self.label_to_int = dict()
        self.int_to_label = dict()
        if add_blank:
            self.label_to_int['BLANK'] = 0
            self.int_to_label[0] = 'BLANK'
        for transcription in transcription_list:
            for char in transcription:
                if not char in self.label_to_int:
                    number = len(self.label_to_int)
                    self.label_to_int[char] = number
                    self.int_to_label[number] = char

    def label_seq_to_int_arr(self, label_seq):
        int_arr = numpy.empty(len(label_seq), dtype=numpy.int32)
        for idx, char in enumerate(label_seq):
            int_arr[idx] = self.label_to_int[char]
        return int_arr

    def int_arr_to_label_seq(self, int_arr):
        return ''.join([self.int_to_label[i] for i in int_arr])

    def print_mapping(self):
        for char, i in self.label_to_int.items():
            print('{} -> {}'.format(char, i))

    def __len__(self):
        return len(self.label_to_int)