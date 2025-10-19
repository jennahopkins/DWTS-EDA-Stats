import requests
from bs4 import BeautifulSoup
import csv

url = "https://en.wikipedia.org/wiki/Dancing_with_the_Stars_(American_TV_series)_season_34"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36'
}

response = requests.get(url, headers=headers)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')

data_dict = {}


week_divs = soup.find_all('div', class_="mw-heading mw-heading3")
for week_header in week_divs:
    header = week_header.find("h3")
    if header:
        text_list = header.get_text(strip=True).split(" ")
        if text_list[0] == "Week":
            data_dict[int(text_list[1][0])] = {}

tables = soup.find_all("table", class_ = ["wikitable", "sortable", "jquery-tablesorter"])
week = 0
for k, table in enumerate(tables):
    headings = table.find_all("th")
    headings_text = [heading.get_text(strip=True) for heading in headings]
    if k < 2:
        continue
    week += 1
    rows = table.find_all("tr")[1:]
    for row in rows:
        if week > len(data_dict):
            break
        cols = row.find_all(['td', 'th'])
        col_text = [cell.get_text(strip=True) for cell in cols]
        couple = col_text[0]
        scores = col_text[1].split(" ")
        scores = [score.strip("(,)") for score in scores]
        if scores == [""]:
            data_dict.pop(week)
            break
        data_dict[week][couple] = scores

judges = {}
judges_p = soup.find_all("p")
used = 1
judge_names = []
for p in judges_p:
    text = p.get_text()
    if "Individual judges' scores" in text:
        judge_index = text.find(":")
        names = text[judge_index + 1:].strip(". \n").split(", ")
        judge_names.append(names)
for week_num, couples in data_dict.items():
    for couple, scores in couples.items():
        if len(scores) == 4:
            judges[week_num] = judge_names[0]
        else:
            judges[week_num] = judge_names[used]
            used += 1
        break

for week_num, couples in data_dict.items():
    judge_scores = {}
    for couple, scores in couples.items():
        for i, judge in enumerate(judges[week_num]):
            if judge not in judge_names[0]:
                judge = "Guest Judge"
            judge_scores[judge] = scores[i + 1]
        data_dict[week_num][couple] = judge_scores

with open('JudgeScores.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Week", "Couple", judge_names[0][0] + " Score", judge_names[0][1] + " Score", judge_names[0][2] + " Score", "Guest Judge Score"]) # Write headers
    for week, couples in data_dict.items():
        for couple, scores in couples.items():
            writer.writerow([week, couple, scores.get(judge_names[0][0], "N/A"), scores.get(judge_names[0][1], "N/A"), scores.get(judge_names[0][2], "N/A"), scores.get("Guest Judge", "N/A")])