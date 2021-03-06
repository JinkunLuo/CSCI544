import os
import sys
import glob

stop_word = ['on', 'this', 'with', 'they', 'our', 'have', 'from', 'there', 'for', 'it', 'at', 'that', 'a', 'an', 'the',
             'i', 'am', 'my', 'myself', 'she', 'her', 'he', 'his', 'is', 'am', 'are', 'was', 'we', 'you', 'were', 'because', 'had', 'when', 'would', 'will', 'just', 'about', 'after', 'did', 'which', 'could', 'what', 'their', 'some', 'been', 'can', 'your', 'has', 'them', 'then']

# Used to store corpus collected in training data
all_words = []

# Hyper_parameters
letter = 6
most_delete = 10  # Considered as stop words
converge_time = 10
count_features = 100  # counts of features : Choosing top 100 most words as features
total_iteration = 640  # file_count = 2*4*80
parameter_degree = '0.8'


def openFolder(root_path):
    """
    Open the folder of Positive or Negative
    :return: path to txt file
    """
    # Initialize empty word bags for each label
    list_positive = []
    list_negative = []
    list_truth = []
    list_deceptive = []
    wb_all = {}

    all_path = ["/negative_polarity/deceptive_from_MTurk", "/negative_polarity/truthful_from_Web",
                "/positive_polarity/deceptive_from_MTurk", "/positive_polarity/truthful_from_TripAdvisor"]
    for parent_path in all_path:
        for i in range(1, 5):
            total_path = root_path + parent_path + '/fold' + str(i)
            f = glob.glob(total_path + '/*.txt')
            for curr_path in f:
                with open(curr_path, 'r') as txt:
                    curr_text = txt.read()
                    token_String(curr_text, wb_all)
                    # token_shingling(curr_text, wb_all)
                    if "positive" in curr_path:
                        list_positive.append(curr_text.lower())
                    if "negative" in curr_path:
                        list_negative.append(curr_text.lower())
                    if "truthful" in curr_path:
                        list_truth.append(curr_text.lower())
                    if "deceptive" in curr_path:
                        list_deceptive.append(curr_text.lower())
    return wb_all, list_positive, list_negative, list_truth, list_deceptive


def calculate_update(list_data, label, weight, bias, time, converge):
    """
    Given x, w, b, y
    :param list_data: list of words count(words: features) --> After processing, length == d
    :param label: label of corresponded test data --> 1/-1
    :param weight: current weight --> length == d
    :param bias: current bias
    :param time: current time of iteration --> Used to calculate averaged parameters
    :param converge: Record time of converge
    :return: weight, bias, time+1
    """
    activation = 0
    for i in range(len(weight)):
        activation += list_data[i] * weight[i]
    activation += bias
    if label*activation <= 0:
        for i in range(len(weight)):
            weight[i] = weight[i] + label*list_data[i]
        bias += label
        converge = 0
    else:
        converge += 1
    return weight, bias, time+1, converge


def token_String(text, word_bag):
    """
    Token each document.
    Give string, split it into dictionary. --> {word:count}
    Convert uppercase to lowercase.
    :param word_bag: store the word bag already loaded from text file before
    :param text: String
    :return: word-bag generated by text --> Dictionary
    """
    rest_text = text.lower()

    # Store all words in given text --> {word:count}
    # word_bag = {}
    # Record current word
    tmp_word = ''
    for c in rest_text:
        if c.isalpha():
            tmp_word += c
        elif tmp_word.isalpha():
            if tmp_word in word_bag.keys():
                word_bag[tmp_word] += 1
            else:
                word_bag[tmp_word] = 1
            tmp_word = ''
        else:
            tmp_word = ''
    # print(word_bag)
    return word_bag


def token_shingling(text, word_bags):
    text = text.lower()
    for i in range(len(text) - letter):
        curr_token = text[i:i + letter]
        if curr_token in word_bags.keys():
            word_bags[curr_token] += 1
        else:
            word_bags[curr_token] = 1

    return word_bags


def generate_model(root_path):
    wb_all, list_positive, list_negative, list_truth, list_deceptive = openFolder(root_path)
    features = []
    feature_model = 'Features:\n'
    vanilla_model_p_n = 'Vanilla perceptron for positive or negative:\nWeight:\n'
    averaged_model_p_n = 'Averaged perceptron for positive or negative:\nWeight:\n'
    vanilla_model_t_d = 'Vanilla perceptron for truthful or deceptive:\nWeight:\n'
    averaged_model_t_d = 'Averaged perceptron for truthful or deceptive:\nWeight:\n'

    # Initialize parameters
    weight_p_n = [0] * count_features
    bias_p_n = 0
    converge_p_n = 0
    time_p_n = 0
    weight_t_d = [0] * count_features
    bias_t_d = 0
    converge_t_d = 0
    time_t_d = 0

    # Averaged Perceptron
    sum_w_p_n = [0] * len(list_positive)
    sum_b_p_n = 0
    sum_w_t_d = [0] * len(list_positive)
    sum_b_t_d = 0

    # delete stop word
    i = 0  # Record features' amount
    sort_l = sorted(wb_all.items(), key=lambda x: x[1], reverse=True)

    # Update features
    for w in sort_l[most_delete:]:
        w = list(w)
        if w[0] not in stop_word:
            if len(w[0]) <= 2:
                stop_word.append(w[0])
            else:
                features.append(w[0])
                feature_model += w[0] + ' '
                i += 1
        if i >= count_features:
            break

    # print("feature total:", len(features))
    # Cross update from two classes
    for i in range(len(list_positive)):
        list_x_p = []
        list_x_n = []
        list_x_t = []
        list_x_d = []

        # value of Xd in each example
        for f in features:
            list_x_p.append(list_positive[i].count(f))  # xd
            list_x_n.append(list_negative[i].count(f))
            list_x_t.append(list_truth[i].count(f))
            list_x_d.append(list_deceptive[i].count(f))

        weight_p_n, bias_p_n, time_p_n, converge_p_n = calculate_update(list_x_p, 1, weight_p_n, bias_p_n, time_p_n, converge_p_n)
        sum_w_p_n = [sum(z) for z in zip(sum_w_p_n, weight_p_n)]
        sum_b_p_n += bias_p_n

        weight_p_n, bias_p_n, time_p_n, converge_p_n = calculate_update(list_x_n, -1, weight_p_n, bias_p_n, time_p_n, converge_p_n)
        sum_w_p_n = [sum(z) for z in zip(sum_w_p_n, weight_p_n)]
        sum_b_p_n += bias_p_n

        weight_t_d, bias_t_d, time_t_d, converge_t_d = calculate_update(list_x_t, 1, weight_t_d, bias_t_d, time_t_d, converge_t_d)
        sum_w_t_d = [sum(z) for z in zip(sum_w_t_d, weight_t_d)]
        sum_b_t_d += bias_t_d

        weight_t_d, bias_t_d, time_t_d, converge_t_d = calculate_update(list_x_d, -1, weight_t_d, bias_t_d, time_t_d,
                                                                        converge_t_d)
        sum_w_t_d = [sum(z) for z in zip(sum_w_t_d, weight_t_d)]
        sum_b_t_d += bias_t_d

        if converge_p_n >= converge_time and converge_t_d >= converge_time:
            print(time_p_n, time_t_d)
            break

    for w in weight_p_n:
        vanilla_model_p_n += str(w) + ' '

    vanilla_model_p_n += ('\nbias:\n' + str(bias_p_n) + '\n')

    for w in sum_w_p_n:
        w = w / time_p_n
        averaged_model_p_n += str(w) + ' '
    averaged_model_p_n += ('\nbias:\n' + str(sum_b_p_n/time_p_n) + '\n')

    for w in weight_t_d:
        vanilla_model_t_d += str(w) + ' '
    vanilla_model_t_d += ('\nbias:\n' + str(bias_t_d) + '\n')
    for w in sum_w_t_d:
        w = w / time_t_d
        averaged_model_t_d += str(w) + ' '
    averaged_model_t_d += ('\nbias:\n' + str(sum_b_t_d/time_t_d) + '\n')

    model = [feature_model+'\n'+vanilla_model_p_n, feature_model+'\n'+averaged_model_p_n, vanilla_model_t_d, averaged_model_t_d]
    return model


def delete_stop_word(word_bag):
    """
    Process word_bag of each class.
    Delete top 10 most common words and add them into stop words.
    Delete stop words from word_bag.
    :param word_bag:
    :return: new word bag of each label
    """
    sort_l = sorted(word_bag.items(), key=lambda x: x[1], reverse=True)

    # Add most popular 10 words to stop word list
    most_word = sort_l[:most_delete]
    for w in most_word:
        stop_word.append(list(w)[0])
    set(stop_word)

    # Delete words in word bag according to stop words set
    new_word_bag = {}
    for k in word_bag.keys():
        if k not in stop_word:
            new_word_bag[k] = word_bag[k]
            # Record words into all words
            all_words.append(k)
    list(set(all_words))

    return new_word_bag


def writeOutput(output_name, train_model):
    complete_path = "/Users/jinkunluo/Downloads/op_spam_training_data" + '/' + output_name

    with open(complete_path, 'w') as f:
        f.write("")
    with open(complete_path, 'a') as f:
        f.write(train_model)


def main(argv):
    # For each file, read it
    # files = [''];
    # for file in files:
    #     readInput(file)
    # Open all
    root_path = "/Users/jinkunluo/Downloads/op_spam_training_data"
    # root_path = argv[1]
    vanilla_output_path = "vanillamodel.txt"
    averaged_output_path = "averagedmodel.txt"
    model = generate_model(root_path)  # Line4: weight; Line6: bias
    # for i in range(4):
    #     print(model[i])
    # "/Users/jinkunluo/Downloads/op_spam_training_data/vanillamodel.txt"
    # "/Users/jinkunluo/Downloads/op_spam_training_data/averagedmodel.txt"
    writeOutput(vanilla_output_path, model[0]+model[2])
    writeOutput(averaged_output_path, model[1]+model[3])
    # with open("/Users/jinkunluo/Downloads/op_spam_training_data/averagedmodel.txt", 'r') as f:
    #     d = f.readlines()
    # for i in range(len(d)):
    #     print(str(i) + "-------" + d[i])


if __name__ == "__main__":
    main(sys.argv)