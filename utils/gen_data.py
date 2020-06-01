import csv
import random
import argparse
import numpy as np
import json

'''
Take in verb-object and object-embedding pairs,
and generate command-embedding pairs for training and testing of the model
'''

parser = argparse.ArgumentParser()
#annotated verb-object pairs data
parser.add_argument('--inputVO', type=str, default='../data/annotated-vo.csv', help='input verb-object file')
#below file is generated by resnet.py
parser.add_argument('--inputOA', type=str, default='../data/object-embedding.csv', help='input object-embedding file')
parser.add_argument('--train', type=str, default='../data/corpus-train.csv', help='output file')
parser.add_argument('--test', type=str, default='../data/corpus-test.csv', help='output file')
opt = parser.parse_args()

#only use the verb in generating natural language commands,
#if set to False then use both the verb and object/noun
verb_only = True
#threshold value to filter out verbs that can only be paired with very few objects
THRESHOLD = 5
data_aug = 10 # rate of data augmentation

# Generates a string/command from templates
def gen_from_template(verb, obj):
    pre_obj = ['Give me the ', 'Hand me the ', 'Pass me the ', 'Fetch the ',
           'Get the ', 'Bring the ', 'Bring me the ',
           'I need the ', 'I want the ',
           'I need a ', 'I want a ']

    pre_verb = ['An item that can ', 'An object that can ',
           'Give me something that can ', 'Give me an item that can ',
           'Hand me something with which I can ',
           'Give me something with which I can ',
           'Hand me something to ', 'Give me something to ',
           'I want something to ', 'I need something to ']

    if verb_only:
        template = random.choice(pre_verb)
        sentence = template + verb
    else:
        template = random.choice(pre_obj)
        sentence = template + obj + ' to ' + verb
    return sentence


with open(opt.inputVO, 'r') as inputVOFile:
    with open(opt.inputOA, 'r') as inputOAFile:
        with open(opt.train, 'w', newline='') as outputTrain:
            with open(opt.test, 'w', newline='') as outputTest:
                writer_train = csv.writer(outputTrain, delimiter=',')
                writer_test = csv.writer(outputTest, delimiter=',')
                voData = list(csv.reader(inputVOFile))
                oaData = list(csv.reader(inputOAFile))

                aff_dict = {}
                for row in oaData:
                    obj = str(row[0]).lower()
                    aff = str(row[1])
                    img = str(row[2])
                    if obj not in aff_dict:
                        aff_dict[obj] = []
                    aff_dict[obj].append([aff, img])

                vo_dict = {}
                objects = []
                for row in voData:
                    verb = str(row[0])
                    obj = str(row[1])
                    label = str(row[2])
                    #if the verb-object pair is annotated to be valid
                    if (len(label) > 0):
                        if verb not in vo_dict:
                            vo_dict[verb] = []
                        if obj not in vo_dict[verb]:
                            vo_dict[verb].append(obj)
                        if obj not in objects:
                            objects.append(obj)

                with open('../data/vo_dict.json', 'w+') as f:
                    f.write(json.dumps(vo_dict))

                verbs = []
                for v, obj in vo_dict.items():
                    if (len(obj) >= THRESHOLD):
                        verbs.append(v)

                #holdout 20% of the object classes for testing
                test = random.sample(objects, k=int(len(objects)/5))
                train = []
                for o in objects:
                    if o not in test:
                        train.append(o)

                for v, obj in vo_dict.items():
                    for o in obj:
                        if v in verbs:
                            if o in train:
                                #each verb-object pair datapoint is augmented
                                #by generating a different natural language command
                                #and pairing it with a randomly selected image/embedding of the object
                                for i in range(data_aug):
                                    sentence = gen_from_template(v, o)
                                    aff, img = random.choice(aff_dict[o])
                                    row = (v, o, sentence, aff, img)
                                    writer_train.writerow(row)
                            else:
                                sentence = gen_from_template(v, o)
                                aff, img = random.choice(aff_dict[o])
                                row = (v, o, sentence, aff, img)
                                writer_test.writerow(row)
