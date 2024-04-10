import io
from google.cloud import vision
from thefuzz import process
from collections import Counter
import os
import re
import math

def is_dollar(s):
    is_decimal = False
    for char in s:
        if char == "/" or char == ":" or char == "-":
            return False
        if char == ".":
            is_decimal = True
    if is_decimal:
        return re.match("\d+(?:\.\d+)?", s)
    '''if any(i.isdigit() for i in s):
        for i in range(len(s)):
            if s[i] == "$" or s[i] == ".":
                return True'''

def check_horizontal_distance(receipt_type_results, amount_results):
    # Magnitude
    # Check y difference for horizontality
    smallest_y_diff = math.inf
    pair = []

    for i in range(len(receipt_type_results)):
        type_vertices = receipt_type_results[i]["Bounding Poly"].vertices
        type_avg_y = 0
        for vertex in type_vertices:
            # TODO: Check if vertices are not extreme distance from each other
            type_avg_y += vertex.y
        type_avg_y /= 4
        #print(receipt_type_results[i]["Bounding Poly"].vertices[0])
        for j in range(len(amount_results)):
            amount_vertices = amount_results[j]["Bounding Poly"].vertices
            amount_avg_y = 0
            for vertex in amount_vertices:
                amount_avg_y += vertex.y
            amount_avg_y /= 4

            if abs(type_avg_y - amount_avg_y) < smallest_y_diff:
                smallest_y_diff = abs(type_avg_y - amount_avg_y)
                pair = [receipt_type_results[i], amount_results[j]]

    return pair

def check_neighbors(texts, split, text_idx, split_idx):
    DEPTH = 5
    for i in range(1, DEPTH+1):
        if text_idx-i < 0:
            break

        #if len(split) > 1:
        #    if process.extractOne(split[split_idx-i], ["Deposit", "Withdraw"])[1] > 80:
        #        print("FOUNDDD")
        
        text_neighbor_results = process.extractOne(texts[text_idx-i].description, ["Deposit", "Withdraw"])
        if text_neighbor_results[1] > 80:
            return text_neighbor_results


def predict(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    words = ["Deposit", "Withdraw"]
    banks = ["Chase", "PNC", "America", "Wells Fargo", "Truist", "Regions", "CapitalOne", "TD", "Northwest", "Centra", "Republic", "Citi", "Comerica", "Suncoast", "Liberty Federal", "Navy Federal"]
    receipt_type_results = []
    amount_results = []
    bank_results = []

    receipt_counter = Counter()
    bank_counter = Counter()
    amount_counter = Counter()

    for i, text in enumerate(texts):
        # Split string on new lines
        split = text.description.splitlines()
        for j, string in enumerate(split):
            # Result too short for any realistic output
            if len(string) <= 3:
                continue
            #print(f"{string}")
            # Levenshtein distance algorithm for string comparisons
            string_match = process.extractOne(string, words)
            bank_match = process.extractOne(string, banks)

            # Confidence threshold
            if string_match[1] > 80:
                print(split)
                receipt_type_results.append({"Bounding Poly": text.bounding_poly, "String": string, "Match": string_match[0], "Confidence": string_match[1]})
            if bank_match[1] > 80:
                bank_results.append({"String": string, "Match": bank_match[0], "Confidence": bank_match[1]})

            if is_dollar(string):
                amount_results.append({"Bounding Poly": text.bounding_poly, "String": string})
                neighbors_result = check_neighbors(texts, split, i, j)
                if neighbors_result:
                    receipt_counter[neighbors_result[0]] += 10
                    amount_counter[string] += 10
                    print("FOUND")
    
    check_horizontal_distance(receipt_type_results, amount_results)
    
    for i in range(len(receipt_type_results)):
        receipt_counter[receipt_type_results[i]["Match"]] += 1

    for i in range(len(bank_results)):
        bank_counter[bank_results[i]["Match"]] += 1

    for i in range(len(amount_results)):
        amount_counter[amount_results[i]["String"]] += 1

    with open('results.txt', 'a', encoding="utf-8") as f:
        f.write(image_path)
        f.write("\n")
        for i, count in receipt_counter.most_common():
            f.write(f"{i}, {round(count/len(receipt_type_results)*100.0, 2)}   ")
        f.write("\n")
        for i, count in bank_counter.most_common():
            f.write(f"{i}, {round(count/len(bank_results)*100.0, 2)}  ")
        f.write("\n")
        for i, count in amount_counter.most_common():
            f.write(f"{i}, {round(count/len(amount_results)*100.0, 2)}  ")
        f.write("\n\n")

def loop_images():
    directory = "coded2"

    for file in os.scandir(directory):
        predict(file.path)

loop_images()