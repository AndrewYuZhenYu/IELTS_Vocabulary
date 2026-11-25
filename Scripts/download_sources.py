from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'Data' / 'ecdict.csv'
URL = 'https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv'
REFERENCES = {
    'oxford3000.pdf':'https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf',
    'oxford5000.pdf':'https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf',
}

def download(url,path,min_size):
    if path.exists() and path.stat().st_size>=min_size:
        print(f'Using {path} ({path.stat().st_size} bytes)');return
    path.parent.mkdir(parents=True,exist_ok=True)
    with requests.get(url,stream=True,timeout=120) as response:
        response.raise_for_status()
        with open(path.with_suffix('.part'),'wb') as out:
            for chunk in response.iter_content(1024*1024):out.write(chunk)
    path.with_suffix('.part').replace(path)
    if path.stat().st_size<min_size:raise ValueError(f'Unexpectedly small source: {path}')
    print(f'Downloaded {path} ({path.stat().st_size} bytes)')

def main():
    download(URL,RAW,10_000_000)
    for name,url in REFERENCES.items():
        # Oxford permits downloading its PDF for offline consultation; keep it
        # local and exclude Data/References from redistributed archives.
        download(url,ROOT/'Data'/'References'/name,50_000)

if __name__ == '__main__': main()
