import os
import importlib
from pathlib import Path

def main():
    # Define the directory where your scraper scripts are located
    scraper_dir = Path(__file__).resolve().parent.joinpath('scraper')

    # List all python files in the scraper directory that match the scraper pattern
    scraper_scripts = [f for f in os.listdir(scraper_dir) if f.endswith('_scraper.py')]

    # Run the 'scraper' function from each scraper script
    for script_name in scraper_scripts:
        # Import the scraper module
        scraper_module_name = script_name[:-3]  # Remove the '.py' from the filename to get the module name
        scraper_module_path = f'scraper.{scraper_module_name}'
        try:
            scraper_module = importlib.import_module(scraper_module_path)

            # Run the 'scraper' function
            print(f"Running scraper from {script_name}...")
            scraper_module.scraper()
        except Exception as e:
            print(f"An error occurred while running {script_name}: {e}")

if __name__ == "__main__":
    main()
