from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'Data' / 'ecdict.csv'
URL = 'https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv'

def main():
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists() and RAW.stat().st_size > 10_000_000:
        print(f'Using {RAW} ({RAW.stat().st_size} bytes)')
        return
    with requests.get(URL, stream=True, timeout=120) as response:
        response.raise_for_status()
        with open(RAW.with_suffix('.part'), 'wb') as out:
            for chunk in response.iter_content(1024 * 1024):
                out.write(chunk)
    RAW.with_suffix('.part').replace(RAW)
    print(f'Downloaded {RAW} ({RAW.stat().st_size} bytes)')

if __name__ == '__main__': main()
