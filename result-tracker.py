import json
from collections import Counter
import requests
import argparse

def current_votes(county):
    return sum([candidate["voteNum"] for candidate in county["candidates"]])

def total_county_votes(county):
    percent_reporting = county["percentReporting"]/100
    curr_votes = current_votes(county)
    return curr_votes / percent_reporting
    
def remaining_votes(county):
    total_votes = total_county_votes(county)
    curr_votes = current_votes(county)
    return (total_votes - curr_votes)
    
def projected_votes(county):
    outstanding_votes = remaining_votes(county)
    curr_votes = current_votes(county)
    proj_votes = Counter({candidate["lastName"]: outstanding_votes*(candidate["voteNum"]/curr_votes) for candidate in county["candidates"]})
    return proj_votes
    
def county_votes_by_candidate(county):
    return Counter({candidate["lastName"]: candidate["voteNum"] for candidate in county["candidates"]})
    
def current_votes_by_candidate(counties):
    return sum([county_votes_by_candidate(county) for county in counties], Counter())
    
def projected_votes_by_candidate(counties):
    return sum([projected_votes(county) for county in counties], Counter())
    
def remaining_votes_in_state(counties):
    return sum([remaining_votes(county) for county in counties])
    
def projected_result(counties):
    curr_votes_by_candidate = current_votes_by_candidate(counties)
    proj_votes_by_candidate = projected_votes_by_candidate(counties)
    
    return curr_votes_by_candidate + proj_votes_by_candidate
    
def process_results(projection):
    total_votes = sum([value for value in projection.values()])
    winner = max(projection, key=projection.get)
    win_percentage = projection[winner] / total_votes
    
    print(f'{winner} is projected to win with {win_percentage*100}% of the vote.')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--stateCode", type=str, help="two letter state code")
    
    args = parser.parse_args()
    
    request_url = f'https://politics.api.cnn.io/results/county-races/2022-SG-{args.stateCode}.json'
    res = requests.get(request_url)
    county_results = json.loads(res.text)

    #result_file = "GA-results.json"

    #with open(result_file, "r") as f: county_results = json.load(f)

    projection = projected_result(county_results)
    process_results(projection)
        
    