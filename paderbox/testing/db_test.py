import unittest
import functools
import pathlib
from collections import Counter

from parameterized import parameterized


from paderbox.io.data_dir import database_jsons as database_jsons_dir
from paderbox.database.keys import *
from paderbox.database.iterator import recursive_transform, ExamplesIterator, \
    AudioReader

ROOT = database_jsons_dir


class DatabaseTest(unittest.TestCase):

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, value):
        self._json = value

    def _check_audio_file_exists(self, wav_path):
        wav_path = pathlib.Path(wav_path)
        if wav_path.exists() and wav_path.is_file():
            return True
        else:
            self.missing_wav.append(f'{wav_path}')
            self._wav_complete = False
            return False

    def test_audio_files_exist(self):
        """
        Tests if all audio files mentioned in the datasets are available.
        """
        successful = True
        self.missing_wav = list()
        for dataset_key, dataset_examples in self.json[DATASETS].items():
            self._wav_complete = True
            for example_key, example in dataset_examples.items():
                recursive_transform(self._check_audio_file_exists,
                                    example[AUDIO_PATH])

            if not self._wav_complete:
                successful = False

        self.assertTrue(successful, 'Some *.wav files referenced in the '
                                    'database json are not available:\n'
                                    f'{self.missing_wav}'
                        )

    def test_structure(self):
        self.assertIn(DATASETS, self.json)

    def assert_in_example(self, keys):
        dataset = list(self.json[DATASETS].values())[0]
        example = list(dataset.values())[0]

        for key in keys:
            self.assertIn(key, example,
                          f'The key "{key}" should be present in examples')

    def assert_in_datasets(self, datasets, full_match=True):
        """

        :param datasets: list of keys
        :param full_match: If True, `datasets` must match with
            `self.json[DATASETS].keys()`. Else, json dataset list needs only to
             contain `datasets`.
        :return:
        """
        assert isinstance(datasets, list), "Datasets is not a list!"

        if full_match:
            self.assertSetEqual(set(datasets), set(self.json[DATASETS].keys()),
                                msg=f'"{datasets}" should be '
                                    f'{self.json[DATASETS].keys()}')
        else:
            for ds in datasets:
                self.assertIn(ds, set(self.json[DATASETS].keys()),
                              msg=f'"{ds}" should be in DATASETS'
                              )

    def test_examples(self):
        self.assert_in_example([AUDIO_PATH, ])

    def assert_total_length(self, total_length):
        _total_length = 0
        for dataset in self.json[DATASETS].values():
            _total_length += len(dataset)

        self.assertEqual(total_length, _total_length,
                         f'The database should contain exactly {total_length} '
                         f'examples in total, but contains {_total_length}')
        
    def assert_len_for_dataset(self, dataset, expected_len):
        if dataset == 'total':
            self.assert_total_length(expected_len)
        elif dataset == 'num_datasets':
            self.assertEqual(len(list(self.json[DATASETS])), expected_len)
        else:
            actual = len(self.json[DATASETS][dataset])
            self.assertEqual(actual, expected_len,
                             f'{dataset}\nActual examples: {actual}\n'
                             f'Expected examples: {expected_len}'
                             )

    def test_reader(self):
        reader = AudioReader()
        for dataset_key, dataset in self.json[DATASETS].items():
            iterator = ExamplesIterator(dataset)
            example = next(iter(iterator))
            example = reader(example)

            # check if audio data was loaded
            self.assertIn(AUDIO_DATA, example)
            
    @classmethod
    def db_parameterized(cls, test_inputs):
        return parameterized.expand(test_inputs,
                                    name_func=lambda func, _, p:
                                    f'{func.__name__}_'
                                    f'{"_".join(str(arg) for arg in p.args)}',
                                    doc_func=(lambda func, num, p: None)
                                    )
    
    @classmethod
    def db_expect_failure(cls, *params,
                          desc=None,
                          **kwparams,
                          ):
        
        """
        A decorator which marks tests that are expected to fail. Increases
        transparency as to why a test should actually fail. Decorated test
        cases will not be counted as FAILURE but as SKIPPED. It is designed to
        work with `parameterized` test cases specified by `params` and
        `kwparams`. If neither of both is given then any failing test case will
        be skipped.
        
        :param params: Arguments (*args) that characterize failing parameterized
            test
        :param desc: A description of the expected error that would be thrown.
            Increases transparency why this test is expected to fail.
        :param kwparams: Keyword arguments (**kwargs) that characterize failing
            parameterized test
        """
        
        assert desc, 'Please provide a failure description to explain why you' \
                     ' expect this test case to fail!'
        
        def decorator_expect_failure(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                print(kwparams.items())
                # Skip unconditionally if `params` and `kwparams` is not given
                # or skip only if all expected parameters in `params`
                # are provided within `args` and `kwparams` match with `kwargs`
                cond = (
                    not (params or kwparams) or
                    (
                        all(param in args for param in params) and
                        all(v == kwargs[k] for k, v in kwparams.items())
                    )
                )
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    if cond:
                        unittest.TestCase.skipTest(func,
                                                   '"Ran into expected failure:'
                                                   f' {desc}"'
                                                   )
                    else:
                        raise e
                else:
                    if cond:
                        assert False, f'"Expected a failure: {desc}"!'
            return wrapper
        return decorator_expect_failure


class DatabaseClassTest(unittest.TestCase):

    def check_data_available(
            self,
            database,
            expected_example_keys,
            optional_example_keys=set(),
            dataset_names=None,
    ):
        if not dataset_names:
            dataset_names = database.dataset_names
        iterator = database.get_iterator_by_names(dataset_names)

        all_keys = [
            key
            for example in iterator
            for key in set(example.keys())
        ]
        num_examples = len(iterator)
        counter = Counter(all_keys)

        diff = set.symmetric_difference(
            set(counter.keys()),
            {*expected_example_keys, *optional_example_keys},
        )
        if len(diff) > 0:
            all_keys = {*expected_example_keys, *optional_example_keys}
            raise Exception(
                f'The datasets does not have the expected keys:\n'
                f'Diff: {diff}\n'
                f'Found: {set(counter.keys())}\n'
                f'Expected: {all_keys}'
            )
        for key in expected_example_keys:
            if counter[key] != num_examples:
                raise Exception(
                    f'Expected key "{key}" to occur {num_examples} times in '
                    f'the dataset, but found it {counter[key]} times.\n'
                    f'Other entries: {counter}'
                )

        for key in optional_example_keys:
            if counter[key] >= num_examples:
                raise Exception(
                    f'Expected key "{key}" to be optional and occur less than '
                    f'{num_examples} times in the dataset, but found it '
                    f'{counter[key]} times.\n'
                    f'Other entries: {counter}'
                )
            if counter[key] <= 0:
                raise Exception(
                    'Can not happen', key, counter[key], num_examples, counter
                )