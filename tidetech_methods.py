import json


def print_json(item):
    print(json.dumps(item, indent=4, separators=(',', ': ')))


def save_file(response, out_file):
    if response.status_code != 200:
        print("Area request failed... Reason follows.")
        print(response.text)
    else:
        with open(out_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
