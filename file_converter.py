# standard libraries
import csv
import re
import os
import sys

__author__ = 'Kyle Vitautas Lopin'


METHODS = ['eig', 'svd', 'qr']


def _is_method_file(_filename):
    if 'eig' in _filename:
        return False
    if 'svd' in _filename:
        return False
    if 'qr' in _filename:
        return False
    return True

def _is_expanded_already(_file):
    """ Take filename and path and checks if the file has already been expanded
    :param _file: full path to the file
    i.e. "/Users/Prattana_Nut/PycharmProjects/Eyring_results/np_errors/2x6/2x6_wide_np.csv"
    :return: True of Fasle if the file has been expanding into methods arlready
    """
    _dir, _filename = os.path.split(_file)
    for method in METHODS:
        if (method+'_'+_filename) not in os.listdir(_dir):
            return False
    return True

def check_correct_file_type(filename, filepath):
    """ Check if the file is the correct format and not expanded already
    :param filename: filename with path attached
    :return: False if file should not be expanded
    """
    beginning_re = re.compile('[0-9]{1}x[0-9]{1}_')
    if not beginning_re.match(filename):  # check the nxn format at the beginning
        return  False # is not the right type of file
    if not filename.endswith('.csv'):
        return False # not correct type of file

    if filename is _is_method_file(filename):
        return  False # the file is a results file so can not be expanded
    if _is_expanded_already(filepath):
        return  False # file is already expanded
    return True

def write_file(_filename, _data):
    for i, new_line in enumerate(_data):
        _data[i] = ''.join(new_line)

    with open(_filename, 'wb') as _file:
        _file.write(''.join(_data))

def convert_file(results_folder, filename):
    filepath = os.path.join(results_folder, filename)
    if not check_correct_file_type(filename, filepath):
        return -1
    eig_lines = []
    svd_lines = []
    qr_lines = []
    with open(filepath) as data_file:
        data_index = []  # each new file will need a header so get the headers
        for i, line in enumerate(data_file.readlines()):
            if '{' in line:
                data_index.append(i)
        data_file.seek(0)  # go back to the beginning of the file
        for i, line in enumerate(data_file.readlines()):
            if i >= 252:
                break
            if i in data_index:
                pass
            elif i < data_index[1]:
                eig_lines.append([line[:-2]])  # :-1 is to remove \r\n
            elif i < data_index[2]:
                eig_lines[i-data_index[1]-1].append(line[:-2])  # :-1 is to remove \n
            elif i < data_index[3]:
                eig_lines[i-data_index[2]-1].append(line)
            elif i < data_index[4]:
                svd_lines.append([line[:-2]])
            elif i < data_index[5]:
                svd_lines[i-data_index[4]-1].append(line[:-2])
            elif i < data_index[6]:
                svd_lines[i-data_index[5]-1].append(line)
            elif i < data_index[7]:
                qr_lines.append([line[:-2]])
            elif i < data_index[8]:
                qr_lines[i-data_index[7]-1].append(line[:-2])
            else:
                qr_lines[i-data_index[8]-1].append(line)
    for i, new_line in enumerate(eig_lines):
        eig_lines[i] = ','.join(new_line)

    write_file(results_folder+'/eig_'+filename, eig_lines)
    for i, new_line in enumerate(svd_lines):
        svd_lines[i] = ','.join(new_line)
    write_file(results_folder+'/svd_'+filename, svd_lines)
    for i, new_line in enumerate(qr_lines):
        qr_lines[i] = ','.join(new_line)
    write_file(results_folder+'/qr_'+filename, qr_lines)
    data_file.close()


def convert_files_in_path(_path):
    print 'check', _path
    # _path = os.getcwd()+_path
    dirs = [x for x in os.listdir(_path) if not x.startswith('.')]
    print dirs
    for dir in dirs:
        directory_files = os.listdir(os.path.join(_path, dir))
        for file in directory_files:
            convert_file(os.path.join(_path, dir), file)

if __name__ == '__main__':
    convert_files_in_path('/np_error_data')
