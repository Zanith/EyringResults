# standard libraries
import csv
import os
# installed libraries
import mpmath as mp

__author__ = 'Kyle Vitautas Lopin'

def mp_read_csv(filename):
    """ Similary to a pandas read_csv() but will save the data as mpmath matrix arrays
    :param filename: filename to open
    :return: data structure similar to pandas dataFrame
    """
    with open(filename, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter='\n', dialect='excel')

        items_string = rows.next()[0]
        # fix the formatting issues in the string with the names of the columns
        data_struct, data_elements = make_data_struct_keys(items_string)
        for row in rows:
            for i, element in enumerate(row[0].split(',')):
                data_struct[data_elements[i]].append(mp.mpf(element))
                # print 'voltage key in helper file: ', data_struct['voltage']

    if 'voltage' in data_struct.keys():
        data_struct['voltage'] = range(-150, 110, 10)
    for key in data_struct.keys():
        data_struct[key] = mp.matrix(data_struct[key])

    return data_struct

def make_data_struct_keys(items_string):
    """ Fix the formatting issues in the way the data is saved by the Eyring rate solver
    :param items_string: list of headers from eyring rate data file
    :return: list of strings - fixed data headers
    """
    data_struct = dict()
    items_list = []
    quotes_index = find_occurrences(items_string, '"')
    shifter = 0
    while quotes_index:
        first_index = quotes_index.pop(0) - shifter
        second_index = quotes_index.pop(0) - shifter
        items_string = items_string[:first_index] + \
                       items_string[first_index:second_index+1].replace(',', '') + \
                       items_string[second_index+1:]

        shifter += 1

    items_string = items_string.replace('"', '')

    for item in items_string.split(','):
        items_list.append(item)
        data_struct[item] = []
    return data_struct, items_list

def find_occurrences(string, char): # from http://stackoverflow.com/questions/13009675/find-all-the-occurrences-of-a-character-in-a-string
    return [i for i, letter in enumerate(string) if letter == char]