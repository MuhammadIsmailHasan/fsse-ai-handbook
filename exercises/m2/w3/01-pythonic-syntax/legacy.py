"""Working but un-Pythonic code. Don't edit — rewrite it in pythonic.py."""


def numbered_titles(jobs):
    list = []
    count = 0
    for i in range(len(jobs)):
        if jobs[i]["remote"] == True and jobs[i]["salary"] != None:
            count = count + 1
            list.append(str(count) + ". " + jobs[i]["title"])
    return list


def pair_scores(names, scores):
    if len(names) != len(scores):
        raise ValueError("lengths differ")
    dict = {}
    for i in range(len(names)):
        dict[names[i]] = scores[i]
    return dict


def initials(full_name):
    str = ""
    parts = full_name.split(" ")
    for i in range(len(parts)):
        if parts[i] != "":
            str = str + parts[i][0].upper()
    return str


def count_lines_with(path, word):
    f = open(path)
    count = 0
    for line in f.readlines():
        if word.lower() in line.lower():
            count = count + 1
    f.close()
    return count
