"""
This script takes an idlak database structured as specified (github.com/idlak/idlak-resources) and parses
all of its sentences through the front-end of Idlak. From the resulting xml-file, phone-information per sentence
is converted into diphone information and stored with a sentence-id.

A diphone wishlist is made which contains every diphone present in the database and how often it occurs.
This information is used to pick sentences iteratively that add the most uncommon diphones.


"""


# TODO: make python2 compatible


from datetime import datetime
startTime = datetime.now()
import operator
import subprocess
from lxml import etree
import argparse
import re
import os
import json
import copy


parser = argparse.ArgumentParser(description='Specify location for temporary file storage and of the Wikipedia dump'
                                             'to generate an xml file in Idlak structure ')
parser.add_argument('idlak_path', nargs='+', help="Specify file path to Idlak installation")
parser.add_argument('language', nargs='+', help="Specify the language code of the language "
                                                "you're generating a script for.")
parser.add_argument('dialect', nargs='+', help="Specify the dialect code.")
parser.add_argument('database_path', nargs='+', help="Specify the file path to Idlak-formatted database.")
parser.add_argument('sentence_number', nargs='+', help="Specify how many sentences the resulting script should have. "
                                                       "NOTE: this number cannot be more than the number of "
                                                       "sentences (between 5 and 16 words long) in the database.")
parser.add_argument('language_letters', nargs='+', help="give regex of all the characters that are part of the language"
                                                        " or occur in the database/lexicon")
parser.add_argument('addition_factor', nargs='?', help="Set factor by which diphone frequencies "
                                                       "are changed after script selection")
args = parser.parse_args()


def get_txp_input(idlak_database, temp_folder):
    """
    Takes idlak database returns file path to the converted database ready for the ./idlaktxp
    :param idlak_database: xml database in idlak format
    :return: path of idlaktxp-ready file
    """
    subprocess.call('mkdir {}'.format(temp_folder), shell=True)
    tree = etree.parse(idlak_database)
    characters = re.compile(r'[^{}\d\s.\"\'\-\,\:\;]+'.format(args.language_letters[0]), re.U)
    for child in tree.getroot():
        string = re.sub(characters, ' ', re.sub(r'[<>]', '', child[0].text))
        new_string = re.sub(r'[\n\r]', ' ', string)

        final_string = '<parent>\n' + new_string.replace(u"\u00A0", " ") + '</parent>'
        with open('{}/{}.xml'.format(temp_folder, str(child.get("id"))), 'w',encoding="utf-8") as outfile:
            outfile.write(final_string)
    return temp_folder


def get_txp_output(txp_input, idlak_location, language, dialect, temp_folder):
    """database-nl.xml
    takes location of idlak and xml input file as well as a language and dialect code to generate an output xml with
    the phonetic specification of all the text in the input file.
    :param txp_input: path of xml input file
    :param idlak_location: path of idlak installation
    :param language: language code
    :param dialect: accent/dialect code
    :return: path of generated output
    """
    subprocess.call('mkdir {}'.format(temp_folder), shell=True)
    count = 0
    for subdir, dirs, files in os.walk(txp_input):
        for file in files:
            count += 1
            file_path = os.path.abspath(os.path.join(subdir, file))
            if os.path.getsize(file_path) < 100000:
                print("\n\n{} Getting phone-sequence... \n".format(count))
                current_loc = os.getcwd()
                cmd1 = 'cd {}/src/idlaktxpbin'.format(idlak_location)
                cmd2 = "./idlaktxp --tpdb=../../idlak-data --general-lang={} --general-acc={} {} {}/{}/{}".format(
                    language, dialect, file_path, current_loc,temp_folder, str(file))
                subprocess.call("{}; {}".format(cmd1, cmd2), shell=True)
    return temp_folder


def sentence_dict_gen(xml_file):
    """
    Takes an idlaktxp output file and retrieves utterance-id and the utterance. A dictionary with these two elements
    is returned.
    :param xml_file: path of idlaktxp output file
    :return: dict with utterance-id as key and utterance as value
    """
    sentences = {}
    sentence_count = 0
    word_count = 0
    with open('data_file.txt', 'w') as out:
        for subdir, dirs, files in os.walk(xml_file):
            for file in files:
                file_path = os.path.abspath(os.path.join(subdir, file))
                tree = etree.parse(file_path)
                for child in tree.getroot():
                    lts_count = 0
                    string = ''
                    sent_length = len([element for phrase in child.iter("spt") for element in phrase.iter("tk")])
                    if 5 <= sent_length < 16:
                        print("Wiki ID:", str(file[:-4])+';', 'Sentence:', child.get("uttid"), '({} words)'.format(sent_length))
                        word_count += sent_length
                        sentence_count += 1
                        phones = ['silbb']
                        for phrase in child.iter("spt"):
                            for element in phrase.iter("tk"):
                                if "lts" in element.attrib:
                                    lts_count += 1
                                    print('LTS:', element.text, element.get('pron'), file=out)
                                    print('LTS:', element.text, element.get('pron'))
                                try:
                                    phones.extend(element.get("pron").split())
                                    string += element.text + ' '
                                except TypeError as e:
                                    print(e)
                            phones.append('silb')
                        phones[-1] = 'silbb'
                        diphones = ['_'.join(phones[i:i + 2]) for i in range(len(phones) - 1)]
                        print(string, lts_count/sent_length, file=out)
                        print(string, lts_count / sent_length)
                        sentences[str(file[:-4]) + '_' + child.get("uttid").zfill(5)] = [diphones, string[:-1]]
                        print('\n')
        print("Number of sentences:", sentence_count, '\nNumber of words:', word_count)
        print("Number of sentences:", sentence_count, '\nNumber of words:', word_count, file=out)
    with open('sentence_dict.json', 'w') as out:
        out.write(json.dumps(sentences))

    return sentences


def diphone_wishlist_gen(diphone_dict):
    """
    Take a dictionary with sentences and diphones and construct a diphone wishlist with frequency counts.
    :param diphone_dict: dict with diphones of each sentence
    :return: dict with diphone and frequency count
    """
    diphone_wishlist = {} # dictionary with diphones
    for k, v in diphone_dict.items():
        for type in v[0]:  # making the wishlist for diphones
            if type in diphone_wishlist:
                diphone_wishlist[type] += 1
            else:
                diphone_wishlist[type] = 1
    with open('wishlist_out.txt', 'w') as out:
        out.write(json.dumps(sorted(diphone_wishlist.items(), key=lambda x: x[1]), indent=4))
    return diphone_wishlist


def script_generator(sentences_dict, diphone_wishlist, number_of_sentence, addition_args):
    """
    Generates a script with the most phonetically rich sentences. Rarer diphones are prioritised over more common ones.
    To ensure that very uncommon diphones don't skew the script too much, an addition factor is used to
    'artificially' change the diphone frequency after a sentence has been added to the script containing that diphone.
    :param sentences_dict: Sentence keys with sentences as values
    :param sentence_diphone_dict: Sentence keys with diphones of each sentence as values
    :param diphone_wishlist: Diphone wishlist with diphone as key and number of time it occurs in the sentences as value
    :param number_of_sentence: The number of sentences the script should contain
    :return: Dictionary with 'best' sentences for the script
    """
    if addition_args is None:
        addition_factor = 10
    else:
        addition_factor = addition_args[0]
    diphone_inventory = copy.deepcopy(diphone_wishlist)
    dict_final = {}
    for n in range(number_of_sentence):  # need to ensure the script doesn't fail when this range is higher
        # than sentence_diphone_dict.items()
        score_dict = {}
        discores = {}
        for k, v in sentences_dict.items():
            discores[k] = []
            score = 0
            for i, diphone in enumerate(v[0]):
                try:
                    score += 1 / diphone_wishlist[diphone]
                    individual_score = 1 / diphone_wishlist[diphone]
                    discores[k].extend([diphone, individual_score])
                except:
                    pass
                score2 = score / len(v)
                score_dict[k] = score2
        best = max(score_dict.items(), key=operator.itemgetter(1))[0]  # finding max value in dict
        best_sentence = sentences_dict[best][1]  # actual sentence
        print('phones left: ', len(diphone_inventory))
        for diphone in sentences_dict[best][0]:
            try:
                diphone_wishlist[diphone] = diphone_wishlist[diphone] + addition_factor  # used to find a flatter distribution
                diphone_inventory.pop(diphone)
            except:
                pass
        print('Sentence', n+1, '({} diphones)'.format(len(sentences_dict[best][0])))
        dict_final['z001_' + str(n).zfill(4)] = best_sentence
        sentences_dict.pop(best)
    return dict_final


if __name__ == "__main__":
    txp_input = get_txp_input(args.database_path[0], 'tmp_input')
    txp_output = get_txp_output(txp_input, args.idlak_path[0], args.language[0], args.dialect[0],
                                'tmp_output')

    sentences = sentence_dict_gen(txp_output)
    wishlist = diphone_wishlist_gen(sentences)
    script = script_generator(sentences, wishlist, int(args.sentence_number[0]), args.addition_factor)

    subprocess.call('rm script.txt', shell=True)

    with open("script.txt", 'w') as final_inventory:
        for k, v in script.items():
            string = k + ': ' + v + '\n'
            final_inventory.write(string)

    print("time: ", datetime.now() - startTime)
