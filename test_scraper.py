# test_scraper.py
from scraper import AirdropScraper

def test_scraper():
    scraper = AirdropScraper()
    airdrops = scraper.get_active_airdrops()
    
    print("\nFound airdrops:")
    for airdrop in airdrops:
        print(f"\nName: {airdrop['name']}")
        print(f"Deadline: {airdrop['claim_deadline']}")
        print(f"Requirements: {airdrop['requirements']}")
        print(f"Reward: {airdrop['reward']}")
        print(f"Status: {airdrop['status']}")

if __name__ == "__main__":
    test_scraper()