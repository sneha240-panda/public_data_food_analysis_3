# AUTOGENERATED! DO NOT EDIT! File to edit: 01_food_parser.ipynb (unless otherwise specified).

__all__ = ['FoodParser']

# Cell
import nltk
nltk.download('words', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

import pickle
import re
import string
import numpy as np
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, words
import pkg_resources

# Cell
class FoodParser():

    def __init__(self):
        # self.__version__ = '0.1.9'
        self.wnl = WordNetLemmatizer()
        # self.spell = SpellChecker()
        return

    ################# Read in Annotations #################
    def process_parser_keys_df(self, parser_keys_df):
        parser_keys_df = parser_keys_df.query('food_type in ["f", "b", "m", "w", "modifier", "general", "stopword", "selfcare"]').reset_index(drop = True)

        # 1. all_gram_sets
        all_gram_set = []
        for i in range(1, 6):
            all_gram_set.append(set(parser_keys_df.query('gram_type == ' + str(i)).gram_key.values))

        # 2. food_type_dict
        food_type_dict = dict(zip(parser_keys_df.gram_key.values, parser_keys_df.food_type.values))

        # 3. food2tag
        def find_all_tags(s):
            tags = []
            for i in range(1, 8):
                if not isinstance(s['tag' + str(i)], str) and np.isnan(s['tag' + str(i)]):
                    continue
                tags.append(s['tag' + str(i)])
            return tags
        food2tags = dict(zip(parser_keys_df.gram_key.values, parser_keys_df.apply(find_all_tags, axis = 1)))
        return all_gram_set, food_type_dict, food2tags

    # def run_setup(self):
    #     setup_dict = {}
    #
    #     # Read parser_keys
    #     parser_keys_df = self.read_parser_keys()
    #     all_gram_set, food_type_dict, food2tags = self.process_parser_keys_df(parser_keys_df)
    #     # my_stop_words = combined_gram_set_df.query('food_type == "stopwords"').gram_key.values
    #
    #     # Read the correction history for fire-fighters
    #     # correction_dic = pickle.load(open(pkg_resources.resource_stream(__name__, "data/correction_dic.pickle"), 'rb'))
    #     correction_dic = pickle.load(pkg_resources.resource_stream(__name__, "data/correction_dic.pickle"))
    #
    #     setup_dict['all_gram_set'] = all_gram_set
    #     setup_dict['food_type_dict'] = food_type_dict
    #     setup_dict['my_stop_words'] = my_stop_words
    #     setup_dict['correction_dic'] = correction_dic
    #     return setup_dict

    def initialization(self):
        # 1. read in manually annotated file and bind it to the object
        parser_keys_df = pd.read_csv(pkg_resources.resource_stream(__name__, "../data/parser_keys.csv"))
        all_gram_set, food_type_dict, food2tags = self.process_parser_keys_df(parser_keys_df)
        correction_dic = pickle.load(pkg_resources.resource_stream(__name__, "../data/correction_dic.pickle"))
        self.all_gram_set = all_gram_set
        self.food_type_dict = food_type_dict
        self.correction_dic = correction_dic
        self.tmp_correction = {}
        # setup_dict = self.run_setup()
        # self.my_stop_words = setup_dict['my_stop_words']
        # self.gram_mask = gram_mask
        # self.final_measurement = final_measurement

        # 2. Load common stop words and bind it to the object
        stop_words = stopwords.words('english')
        # Updated by Katherine August 23rd 2020
        stop_words.remove('out') # since pre work out is a valid beverage name
        stop_words.remove('no')
        stop_words.remove('not')
        self.stop_words = stop_words
        return

    ########## Pre-Processing ##########
    # Function for removing numbers
    def handle_numbers(self, text):
        clean_text = text
        clean_text = re.sub('[0-9]+\.[0-9]+', '' , clean_text)
        clean_text = re.sub('[0-9]+', '' , clean_text)
        clean_text = re.sub('\s\s+', ' ', clean_text)
        return clean_text

    # Function for removing punctuation
    def drop_punc(self, text):
        clean_text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
        return clean_text

    # Remove normal stopwords
    def remove_stop(self, my_text):
        text_list = my_text.split()
        return ' '.join([word for word in text_list if word not in self.stop_words])

    # def remove_my_stop(self, text):
    #     text_list = text.split()
    #     return ' '.join([word for word in text_list if word not in self.my_stop_words])

    def pre_processing(self, text):
        text = text.lower()
        # return self.remove_my_stop(self.remove_stop(self.handle_numbers(self.drop_punc(text)))).strip()
        return self.remove_stop(self.handle_numbers(self.drop_punc(text))).strip()

    ########## Handle Format ##########
    def handle_front_mixing(self, sent, front_mixed_tokens):
        # print(sent)
        cleaned_tokens = []
        for t in sent.split():
            if t in front_mixed_tokens:
                number = re.findall('\d+[xX]*', t)[0]
                for t_0 in t.replace(number, number + ' ').split():
                    cleaned_tokens.append(t_0)
            else:
                cleaned_tokens.append(t)
        return ' '.join(cleaned_tokens)

    def handle_x2(self, sent, times_x_tokens):
        # print(sent)
        for t in times_x_tokens:
            sent = sent.replace(t, ' ' + t.replace(' ', '').lower() + ' ')
        return ' '.join([s for s in sent.split() if s != '']).strip()

    def clean_format(self, sent):
        return_sent = sent

        # Problem 1: 'front mixing'
        front_mixed_tokens = re.findall('\d+[^\sxX]+', sent)
        if len(front_mixed_tokens) != 0:
            return_sent = self.handle_front_mixing(return_sent, front_mixed_tokens)

        # Problem 2: 'x2', 'X2', 'X 2', 'x 2'
        times_x_tokens = re.findall('[xX]\s*?\d', return_sent)
        if len(times_x_tokens) != 0:
            return_sent = self.handle_x2(return_sent, times_x_tokens)
        return return_sent

    ########## Handle Typo ##########
    def fix_spelling(self, entry, speller_check = False):
        result = []
        for token in entry.split():
            # Check known corrections
            if token in self.correction_dic.keys():
                token_alt = self.wnl.lemmatize(self.correction_dic[token])
            else:
                if speller_check and token in self.tmp_correction.keys():
                    token_alt = self.wnl.lemmatize(self.tmp_correction[token])
                elif speller_check and token not in self.food_type_dict.keys():
                    token_alt = self.wnl.lemmatize(token)
                    # token_alt = self.wnl.lemmatize((self.spell.correction(token)))
                    self.tmp_correction[token] = token_alt
                else:
                    token_alt = self.wnl.lemmatize(token)
            result.append(token_alt)
        return ' '.join(result)

    ########### Combine all cleaning ##########
    def handle_all_cleaning(self, entry):
        cleaned = self.pre_processing(entry)
        cleaned = self.clean_format(cleaned)
        cleaned = self.fix_spelling(cleaned)
        return cleaned

    ########## Handle Gram Matching ##########
    def parse_single_gram(self, gram_length, gram_set, gram_lst, sentence_tag):
        food_lst = []
        # print(gram_length, gram_lst, sentence_tag)
        for i in range(len(gram_lst)):
            if gram_length > 1:
                curr_word = ' '.join(gram_lst[i])
            else:
                curr_word = gram_lst[i]
            # print(curr_word, len(curr_word))
            if curr_word in gram_set and sum([t != 'Unknown' for t in sentence_tag[i: i+gram_length]]) == 0:
                # Add this founded food to the food list
                # food_counter += 1
                sentence_tag[i: i+gram_length] = str(gram_length)
                # tmp_dic['food_'+ str(food_counter)] = curr_word
                food_lst.append(curr_word)
                # print('Found:', curr_word)
        return food_lst

    def parse_single_entry(self, entry, return_sentence_tag = False):
        # Pre-processing and Cleaning
        cleaned = self.handle_all_cleaning(entry)
        # print(cleaned)

        # Create tokens and n-grams
        tokens = nltk.word_tokenize(cleaned)
        bigram = list(nltk.ngrams(tokens, 2)) if len(tokens) > 1 else None
        trigram = list(nltk.ngrams(tokens, 3)) if len(tokens) > 2 else None
        quadgram = list(nltk.ngrams(tokens, 4)) if len(tokens) > 3 else None
        pentagram = list(nltk.ngrams(tokens, 5)) if len(tokens) > 4 else None
        all_gram_lst = [tokens, bigram, trigram, quadgram, pentagram]

        # Create an array of tags
        sentence_tag = np.array(['Unknown'] * len(tokens))
        # for i in range(len(sentence_tag)):
        #     if tokens[i] in self.final_measurement:
        #         sentence_tag[i] = 'MS'

        all_food = []
        food_counter = 0
        for gram_length in [5, 4, 3, 2, 1]:
            if len(tokens) < gram_length:
                continue
            tmp_food_lst = self.parse_single_gram(gram_length,
                                                self.all_gram_set[gram_length - 1],
                                                all_gram_lst[gram_length - 1],
                                                sentence_tag)
            all_food += tmp_food_lst
        # print(sentence_tag)
        if return_sentence_tag:
            return all_food, sentence_tag
        else:
            return all_food

    def parse_food(self, entry, return_sentence_tag = False):
        result = []
        unknown_tokens = []
        num_unknown = 0
        num_token = 0
        for w in entry.split(','):
            all_food, sentence_tag = self.parse_single_entry(w, return_sentence_tag)
            result += all_food
            if len(sentence_tag) > 0:
                num_unknown += sum(np.array(sentence_tag) == 'Unknown')
                num_token += len(sentence_tag)
                cleaned = nltk.word_tokenize(self.handle_all_cleaning(w))

                # Return un-catched tokens, groupped into sub-sections
                tmp_unknown = ''
                for i in range(len(sentence_tag)):
                    if sentence_tag[i] == 'Unknown':
                        # unknown_tokens.append(cleaned[i])
                        tmp_unknown += (' ' + cleaned[i])
                        if i == len(sentence_tag) - 1:
                            unknown_tokens.append(tmp_unknown)
                    elif tmp_unknown != '':
                        unknown_tokens.append(tmp_unknown)
                        tmp_unknown = ''
        # for i in range(len(result)):
        #     if result[i] in self.gram_mask.keys():
        #          result[i] = self.gram_mask[result[i]]
        if return_sentence_tag:
            return result, num_token, num_unknown, unknown_tokens
        else:
            return result

    def find_food_type(self, food):
        if food in self.food_type_dict.keys():
            return self.food_type_dict[food]
        else:
            return 'u'

    ################# DataFrame Functions #################
    def expand_entries(self, df):
        assert 'desc_text' in df.columns, '[ERROR!] Required a column of "desc_text"!!'

        all_entries = []
        for idx in range(df.shape[0]):
            curr_row = df.iloc[idx]
            logging = curr_row.desc_text
            tmp_dict = dict(curr_row)
            if ',' in logging:
                for entry in logging.split(','):
                    tmp_dict = tmp_dict.copy()
                    tmp_dict['desc_text'] = entry
                    all_entries.append(tmp_dict)
            else:
                tmp_dict['desc_text'] = logging
                all_entries.append(tmp_dict)

        return pd.DataFrame(all_entries)
