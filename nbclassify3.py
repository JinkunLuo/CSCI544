import os
import sys


def readInput(root_path_data):
    """
    According to root path, return all file paths
    :param root_path_data:
    :return: List of file paths
    """
    # "/Users/jinkunluo/Downloads/op_spam_training_data"
    # for test
    # import os
    # all_input_path = []
    # for filename in os.walk("/Users/jinkunluo/Downloads/op_spam_training_data"):
    #     filename = list(filename)
    #     if len(filename[1]) == 0:
    #         for f2 in filename[2]:
    #             all_input_path.append(filename[0] + '/' + f2)
    # for p in all_input_path:
    #     with open(p, 'r') as f:
    #         print(f.read())
    all_input_path = []
    for filename in os.walk(root_path_data):
        filename = list(filename)
        if len(filename[1]) == 0:
            for f2 in filename[2]:  # filename[2] is a list of .txt file name
                all_input_path.append(filename[0] + '/' + f2)
    return all_input_path


def readModel(root_path, model_path):
    """

    :param root_path: "/Users/jinkunluo/Downloads/op_spam_training_data"
    :param model_path: "nbmodel.txt"
            "/Users/jinkunluo/Downloads/op_spam_training_data/nbmodel.txt"
    :return:
    """
    model_dict = {}
    file_path = root_path + '/' + model_path
    with open(file_path, 'r') as model:
        data = model.readlines()[4:]

    for line in range((len(data) - 3) // 2):
        key = data[line * 2].strip()
        value = []
        for s in data[line * 2 + 1].split('\t'):
            if (len(s)) > 0:
                s.strip()
                index = s.find(':')
                value.append(float(s[index + 1:]))
        model_dict[key] = value

    print(model_dict)
    return model_dict


def classify_data(text_path, model_dict):
    """
    Classify data according to model
    :param text_path: path of document for classify
    :param model_dict: dictionary --> model parameters
    :return: output String
    """
    with open(text_path, 'r') as input_data:
        text = input_data.read()
        word_list = split_String(text)

    score_positive = 0
    score_negative = 0
    score_truthful = 0
    score_deceptive = 0

    for word in word_list:
        if word in model_dict.keys():
            v = model_dict[word]
            score_positive += v[0]
            score_negative += v[1]
            score_truthful += v[2]
            score_deceptive += v[3]

    if score_positive > score_negative:
        label1 = "positive"
    else:
        label1 = "negative"

    if score_truthful > score_deceptive:
        label2 = "truthful"
    else:
        label2 = "deceptive"

    result = label1 + '\t' + label2 + '\t' + text_path + '\n'
    return result


def split_String(text):
    """
    Token each document.
    Give string, split it into dictionary. --> {word:count}
    Convert uppercase to lowercase.
    :param text: String
    :return: List of all words
    """
    rest_text = text.lower()
    words = []
    tmp_word = ''
    for c in rest_text:
        if c.isalpha():
            tmp_word += c
        elif tmp_word.isalpha():
            words.append(tmp_word)
            tmp_word = ''
        else:
            tmp_word = ''
    # print(word_bag)
    return words


def main(argv):
    # model所在跟路径 & output输出txt的文件夹
    root_path = "/Users/jinkunluo/Downloads/op_spam_training_data"
    # root_path = argv[1]
    model_path = "nbmodel.txt"
    model_dict = readModel(root_path, model_path)

    # output path
    output_name = "nboutput.txt"
    output_whole_path = root_path + '/' + output_name
    with open(output_whole_path, 'w') as f:
        f.write("classified result is:\n")

    # test_data所在根路径
    # root_path_data = ""
    root_path_data = root_path
    test_paths = readInput(root_path_data)  # List of .txt path
    for p in test_paths:
        result = classify_data(p, model_dict)
        # write every result here
        with open(output_whole_path, 'a') as f:
            f.write(result)


if __name__ == "__main__":
    main(sys.argv)
