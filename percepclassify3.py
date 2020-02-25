import os
import sys


def readInput(root_path_data):
    """
    According to root path, return all file paths
    :param root_path_data:
    :return: List of file paths
    """
    all_input_path = []
    for filename in os.walk(root_path_data):
        filename = list(filename)
        if len(filename[1]) == 0:
            for f2 in filename[2]:  # filename[2] is a list of .txt file name
                all_input_path.append(filename[0] + '/' + f2)
    return all_input_path


def readModel(model_path):
    """

    :param root_path: "/Users/jinkunluo/Downloads/op_spam_training_data"
    :param model_path: "vanillamodel.txt" / "averagedmodel"
            "/Users/jinkunluo/Downloads/op_spam_training_data/nbmodel.txt"
    :return:
    """
    file_path = model_path
    with open(file_path, 'r') as model:
        data = model.readlines()

    # Analyse model
    features = data[1].strip().split(' ')  # features --> words list

    weight_p_n = data[4].strip().split(' ')
    print("1-----", data[4])
    for ind in range(len(weight_p_n)):
        if weight_p_n[ind][0] == '-':
            weight_p_n[ind] = -1 * float(weight_p_n[ind][1:])
        else:
            try:
                weight_p_n[ind] = float(weight_p_n[ind])
            except ValueError:
                print("invalid input %d" % ind)
    bias_p_n = float(data[6])

    weight_t_d = data[9].strip().split(' ')
    for ind in range(len(weight_t_d)):
        if weight_t_d[ind][0] == '-':
            weight_t_d[ind] = -1 * float(weight_t_d[ind][1:])
        else:
            try:
                weight_t_d[ind] = float(weight_t_d[ind])
            except ValueError:
                print("invalid input %d" % ind)
    bias_t_d = float(data[11])

    model = [features, weight_t_d, bias_t_d, weight_p_n, bias_p_n]\

    # print(model_dict)
    return model


def classify_data(text_path, model):
    """
    Classify data according to model
    :param text_path: path of document for classify
    :param model: list --> [features, weight_t_d, bias_t_d, weight_p_n, bias_p_n]
    :return: output String
    """
    with open(text_path, 'r') as input_data:
        text = input_data.read()

    features, weight_t_d, bias_t_d, weight_p_n, bias_p_n = model[0], model[1], model[2], model[3], model[4]
    score1 = 0
    score2 = 0

    for i in range(min(len(weight_t_d), len(weight_p_n), len(features))):
        c = text.count(features[i])
        score1 += c*weight_t_d[i]
        score2 += c*weight_p_n[i]
    score1 += bias_t_d
    score2 += bias_p_n
    label1 = 'truthful' if score1 > 0 else 'deceptive'
    label2 = 'positive' if score2 > 0 else 'negative'

    result = label1 + '\t' + label2 + '\t' + text_path + '\n'
    return result


def main(argv):
    # argv[1] : model path
    # argv[2] : test data path
    root_path = "/Users/jinkunluo/Downloads/op_spam_training_data"
    # model_path = argv[1]
    # root_path = argv[2]
    model_vanilla_path = "/Users/jinkunluo/Downloads/op_spam_training_data/vanillamodel.txt"
    model_averaged_path = "/Users/jinkunluo/Downloads/op_spam_training_data/averagedmodel.txt"

    output_name = "percepoutput.txt"
    file = open(output_name, 'w')
    root_path_data = root_path
    test_paths = readInput(root_path_data)  # List of .txt path
    model1 = readModel(model_vanilla_path)
    model2 = readModel(model_averaged_path)
    for p in test_paths:
        result = classify_data(p, model1)
        file.write(result)

    file.close()


if __name__ == "__main__":
    main(sys.argv)
