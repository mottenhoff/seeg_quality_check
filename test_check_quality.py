'''
Tests the performance of numerical retrieval of non-eeg
channels
'''

import sys
from pathlib import Path
from os.path import exists

paths = [r"./../../Utility/Helpers/xdf_reader/"]
for path in paths:
    sys.path.insert(0, path)
from read_xdf import read_xdf

from check_quality import QualityChecker

VERBOSE = True


class TestQualityChecker():

    def __init__(self, qc, verbose=True):
        self.results = []
        self.qc = qc
        self.verbose = verbose
    
    def evaluate(self, fn_name, chs_name, chs_num):
        tp = [ch in chs_name for ch in chs_num]
        fp = [ch not in chs_name for ch in chs_num]
        fn = [ch not in chs_num for ch in chs_name]

        self.results += [(fn_name, {
            'channels_by_name': chs_name,
            'channels_by_num': chs_num,
            'TP': tp,
            'FP': fp,
            'FN': fn})]

    def get_results(self, fn, data, channel_names):
        # Channels by name, channel by numerical
        return fn(data, channel_names), fn(data)
        
    def test_fn(self, fn, data, channel_names):
        chs_by_name, chs_by_num = self.get_results(fn, data, channel_names)
        self.evaluate(fn.__name__, chs_by_name, chs_by_num)
    
    def test_all(self, data, channel_names):
        # 'abnormal_amplitude', 'consistent_timestamps'
        # 'excessive_line_noise', 'flat_signal'

        methods_to_test = [
            self.qc.get_marker_channels,
            self.qc.get_ekg_channel,
            self.qc.get_disconnected_channels
        ]
        
        for method in methods_to_test:
            self.test_fn(method, data, channel_names)

        return 0
    

def _get_filenames(path_main, extension, keywords=[], exclude=[]):
    ''' Recursively retrieves all files with 'extension', 
    and subsequently filters by given keywords. 
    '''

    if not exists(path_main):
        print("Cannot access path <{}>. Make sure you're on the university network"\
                .format(path_main))
        raise NameError

    keywords = extension if len(keywords)==0 else keywords
    extension = '*.{}'.format(extension)
    files = [path for path in Path(path_main).rglob(extension) \
             if any(kw in path.name for kw in keywords)]

    if any(exclude):
        files = [path for path in files for excl in exclude \
                   if excl not in path.name]
    return files

def _get_related_files(path):
    seeg_filenames = _get_filenames(path, 'xdf', 
                                    keywords=['grasp'],
                                    exclude=['speech'])
    contact_filenames  = _get_filenames(path, 'csv', keywords=['electrode_locations'])
    return seeg_filenames

def print_results(results, file=None):
    f = open(file, 'a+') if file else file

    for i, (p, r) in enumerate(results):
        if i==0:
            print(''.join(['{:<8s}'.format('')] + ['{:<40s}'.format(tests[0]) for tests in r]), file=f)
            print(''.join(['{:<8s}'.format('')] + ['{:<10s}'.format(metric) for metric in ['N', 'TP', 'FP', 'FN']]*len(r)), file=f)
        print(''.join(
            ['{:<8s}'.format(p)] + \
            ['{:<10d}{:<10d}{:<10d}{:<10d}'.format(len(t[1]['channels_by_name']), sum(t[1]['TP']), sum(t[1]['FP']), sum(t[1]['FN'])) \
                for t in r]), file=f)

    if file:
        f.close()

if __name__ == '__main__':
    path = r'L:\FHML_MHeNs\sEEG\\'
    files = _get_related_files(path)
    results = []
    for i, file in enumerate(files):
        data, raw = read_xdf(file)
        qc = QualityChecker()
        tqc = TestQualityChecker(qc, verbose=True)
        tqc.test_all(data['Micromed']['data'], data['Micromed']['channel_names'])
        results += [(file.parts[3], tqc.results)]

    print_results(results, file='./results.txt')
