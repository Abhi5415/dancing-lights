import requests

url = "https://shazam-core.p.rapidapi.com/v1/tracks/recognize"

headers = {
    "content-type": "multipart/form-data; boundary=---011000010111000001101001",
    "x-rapidapi-key": "f42136d023msh1c820c2920202f4p1b5b4ajsnc04e9452c380",
    "x-rapidapi-host": "shazam-core.p.rapidapi.com",
}

payload = """-----011000010111000001101001\r
Content-Disposition: form-data; name=\"file.wav\"\r
\r
\r
-----011000010111000001101001--\r
\r
"""


response = requests.request(
    "POST",
    url,
    data=payload,
    headers=headers,
    files={"file.wav": open("Test.wav", "rb")},
)

print(response.text)
