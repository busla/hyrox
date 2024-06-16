from typing import Any, Dict
import requests
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


def fix_wrong_category(value: Dict) -> Dict:
    if "Hreindýrabollan".lower() in value["Team"].lower():
        print(f"Fixing wrong category {value['Category']} for {value['Team']}")
        value["Category"] = value["Category"].replace("OPEN", "PRO")
        print(f"Fixed category: {value['Category']}")
    return value


def convert_time_to_seconds(time_str):
    try:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0  # Return 0 if time is invalid


def scrape_category(url):
    print(f"Scraping URL: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        main_table = soup.find("table")

        if not main_table:
            print(f"No table found on {url}")
            return []

        # Extract the category name from the <h3> tag
        category_name = soup.find("h3").get_text(strip=True)
        print(f"Category: {category_name}")

        teams = []

        for row in main_table.find_all("tr")[1:]:
            columns = row.find_all("td")
            bib = columns[1].get_text(strip=True)
            team_name = columns[2].get_text(strip=True)

            # Extract members correctly using <br> as delimiter
            members_html = columns[3]
            members = [
                br.previous_sibling.strip()
                for br in members_html.find_all("br")
                if br.previous_sibling and br.previous_sibling.strip()
            ]
            if members_html.contents and members_html.contents[-1].strip():
                members.append(members_html.contents[-1].strip())

            club = columns[4].get_text(strip=True)

            # Extract the last two <td> for the Time array
            total_time = columns[-1].get_text(strip=True)
            second_last_time = columns[-2].get_text(strip=True)

            splits = []
            split_text = columns[5].get_text(strip=True)
            split_items = split_text.split(")")
            split_counter = {}

            for i, item in enumerate(split_items):
                if "(" in item:
                    label_time = item.split("(")
                    time = label_time[0].strip()
                    label = label_time[1].strip()
                    label = re.sub(r"[0-9.]", "", label).strip()
                    splits.append({"label": label, "time": time, "order": i + 1})
            result = {
                "BIB": bib,
                "Team": team_name,
                "Members": members,
                "Club": club,
                "Time": [second_last_time, total_time],
                "Splits": splits,
                "Category": category_name,
            }
            result = fix_wrong_category(result)
            teams.append(result)

        return teams

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def get_category_urls(base_url):
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        links = soup.find_all("a")

        if not links:
            print("No links found in the document")
            return []

        for link in links:
            print(f"Found link: {link.get('href')}")

        category_urls = [
            urljoin(base_url, link.get("href").replace("&amp;", "&"))
            for link in links
            if link.get("href") and "urslit" in link.get("href")
        ]
        print(f"Constructed category URLs: {category_urls}")
        return category_urls

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def main():
    base_url = "https://timataka.net/hyrox-06-2024/"
    category_urls = get_category_urls(base_url)

    all_teams = []
    for url in category_urls:
        teams = scrape_category(url)
        all_teams.extend(teams)

    # Group teams by category
    categories = {}
    for team in all_teams:
        category = team["Category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(team)

    # Calculate ranks for each category
    for category, teams in categories.items():
        for team in teams:
            time_seconds = [convert_time_to_seconds(t) for t in team["Time"]]
            team["AverageTimeInSeconds"] = sum(time_seconds) / len(time_seconds)

        # Sort teams by average time and assign ranks
        teams.sort(key=lambda x: x["AverageTimeInSeconds"])
        for i, team in enumerate(teams):
            team["Rank"] = i + 1

    # Flatten the categorized teams back into a single list
    all_teams = [team for teams in categories.values() for team in teams]

    # Output the result as JSON and save to file
    result_json = json.dumps(all_teams, indent=2, ensure_ascii=False)
    with open("hyrox_results.json", "w", encoding="utf-8") as f:
        f.write(result_json)


if __name__ == "__main__":
    main()
