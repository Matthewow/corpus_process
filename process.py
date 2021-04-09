import spacy
import glob
import json
import os
import re

nlp = spacy.load('zh_core_web_lg')


def read_data():
    oral_time = ""
    oral_date = ""
    oral_quantity = ""

    f = open("oral_time.txt", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        oral_time += "(" + line.strip() + ")" + "|"

    f = open("oral_date.txt", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        oral_date += "(" + line.strip() + ")" + "|"

    f = open("oral_quantity.txt", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        oral_quantity += "(" + line.strip() + ")" + "|"

    return(oral_time[:-1], oral_date[:-1], oral_quantity[:-1])


def rename():
    f2 = open("forRoger.txt", "a")
    filelist = glob.glob("/home/veserve/Matthew/210407_ner_corpus/data/telegram_group_chat/data_raw/*.json")
    for filename in filelist:
        f = open(filename, "r")
        raw = f.read()
        raw_json = json.loads(raw)
        new_name = raw_json["group_name"] + ".json"
        data = raw_json["data"]
        for line in data:
            f2.write(f"{line}\n")
        
        # f.close()
        # os.rename(r"{}".format(filename), r"{}".format(new_name))
        # print(new_name, type(data))


def process():
    count = 0
    # filelist = glob.glob("/home/veserve/Matthew/210407_ner_corpus/data/telegram_group_chat/data_raw/*.json")
    filelist = ["./telegram_full.txt"]
    for filename in filelist:
        f = open(filename, "r")
        data = f.readlines()
        f.close()

        oral_time, oral_date, oral_quantity = read_data()
        for line in data:
            if ner_tagging(line.strip(), oral_time, oral_date, oral_quantity):
                count = count + 1
    print("all data: ", len(data))
    print("useful sentence count: ", count)


def not_dulpicate(_tuple, _list):
    s = _tuple[0]
    e = _tuple[1]
    for pair in _list:
        if s < pair[1] and e > pair[0]:
            return False
    return True


def money_matching(line):

    money_position = list()
    
    money_rule1 = re.finditer("[$￥]?[一二三四五六七八九十\d\.]+[百千萬億MKBmkb]*[一二三四五六七八九十]?[美日港]?[元蚊]", line)
    money_rule2 = re.finditer("[$￥][一二三四五六七八九十\d\.]+[百千萬億MKBmkb]*[一二三四五六七八九十]?[美日港]?[元蚊]?", line)
    money_rule3 = re.finditer("[$￥]?[一二三四五六七八九十\d\.]+[百千萬億MKBmkb]*[一二三四五六七八九十]?[人民]?[台]?[港]?[幣]", line)
    money_rules = [money_rule1, money_rule2, money_rule3]

    for money_rule in money_rules:
        if money_rule:
            for rule in money_rule:
                if not_dulpicate(rule.span(), money_position):
                    money_position.append(rule.span())
    
    return money_position


def quantity_matching(line, oral_quantity):
    
    quantity_position = list()

    rule1 = "[\d第半幾百千萬億MKBmkb一二三四五六七八九十]{1,7}"+"("+oral_quantity+")"
    quantity_rule1 = re.finditer(r"{}".format(rule1), line)

    if quantity_rule1:
            for rule in quantity_rule1:
                if not_dulpicate(rule.span(), quantity_position):
                    quantity_position.append(rule.span())

    return quantity_position



def time_matching(line, oral_time):

    time_position = list()

    rule1 = "("+ oral_time +")?[\d一二三四五六七八九十]{1,2}[:：點時][踏搭傝]?[\d一二三四五六七八九十半幾]{0,3}[分]?[分鐘]?(個字)?([刻]|(刻鐘))?"
    rule2 = "(" + oral_time + ")?[\d一二三四五六七八九十]{1,2}[.]?[踏搭傝]?[\d一二三四五六七八九十半幾]{1,3}([分]|[分鐘]|(個字)|[刻]|(刻鐘))"
    time_rule1 = re.finditer(r"{}".format(rule1), line)
    time_rule2 = re.finditer(r"{}".format(rule2), line)
    time_rule3 = re.finditer(r"{}".format(oral_time), line)
    
    time_rules = [time_rule1, time_rule2, time_rule3]
    for time_rule in time_rules:
        if time_rule:
            for rule in time_rule:
                if not_dulpicate(rule.span(), time_position):
                    time_position.append(rule.span())
    
    return time_position


def date_matching(line, oral_date):

    date_position = list()

    rule1 = "([\d一二三四五六七八九十今明后]{1,4}[年月日]){1,3}"
    date_rule1 = re.finditer(r"{}".format(rule1), line)
    # time_rule2 = re.finditer(r"{}".format(rule2), line)
    date_rule2 = re.finditer(r"{}".format(oral_date), line)
    
    date_rules = [date_rule1, date_rule2]
    for date_rule in date_rules:
        if date_rule:
            for rule in date_rule:
                if not_dulpicate(rule.span(), date_position):
                    date_position.append(rule.span())
    
    return date_position


def ner_tagging(line, oral_time, oral_date, oral_quantity):

    money_position = money_matching(line)
    time_position = time_matching(line, oral_time)
    date_position = date_matching(line, oral_date)
    quantity_position = quantity_matching(line, oral_quantity)

    find = False
    
    # if len(money_position) >= 1:        
    #     print("{}, Money: {}".format(line, money_position))
    #     find = True

    # if len(time_position) >= 1:  
    #     print("{}, Time: {}".format(line, time_position))
    #     find = True
    
    # if len(date_position) >= 1:  
    #     print("{}, Date: {}".format(line, date_position))
    #     find = True

    if len(quantity_position) >= 1:  
        print("{}, Quantuty: {}".format(line, quantity_position))
        find = True

    return find

    # doc = nlp(line)
    # for ent in doc.ents:
    #     if ent.label_ in ["LOC", "GPE", "DATE", "TIME"]:
    #         print("doc: ", [token for token in doc])
    #         print("  Entities", ent.text, ent.label_, ent.start, ent.end)
    # if money_position:
    #     print("{}, Money: {}".format(line, money_position))
    


process()
