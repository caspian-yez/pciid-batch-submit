#!/usr/bin/env python3

import requests
import bs4
import json

submit_data = [
    # {"id": "a323", "name": "300/C240 Series Chipset Family SMBus"},
]


def html_parse(str_html: str):
    soup = bs4.BeautifulSoup(str_html, "html.parser")

    name = soup.find("div", class_="name")
    text = name.get_text().split(":")[1].strip().replace("\r", "").replace("\n", "")
    print(text)
    return text


def http_request(
    session,
    req_method: str,
    req_url: str,
    req_data=None,
    req_json: dict = None,
    req_cookie: str = None,
):
    print("{} URL: {}".format(req_method, req_url))
    if req_data is not None:
        print("request body: {}".format(req_data))
    if req_json is not None:
        print("request body: {}".format(json.dumps(req_json, indent=4, sort_keys=True)))

    response = session.request(
        method=req_method,
        url=req_url,
        data=req_data,
        json=req_json,
        cookies=req_cookie,
        timeout=25,
        verify=False,
    )

    if isinstance(response, requests.Response):
        print(
            "request headers: {}".format(
                json.dumps(dict(response.request.headers), indent=4, sort_keys=True)
            )
        )

        print("status_code: {}".format(response.status_code))
        print(
            "response headers: {}".format(
                json.dumps(dict(response.headers), indent=4, sort_keys=True)
            )
        )
        print("response body: {}".format(response.text))

    return response


def get_cookie() -> dict:
    f = open("cookie.json", "r")
    data = f.read()
    f.close()
    return json.loads(data)


def main():
    domain = "admin.pci-ids.ucw.cz"
    http_session = requests.sessions.session()
    cookie = get_cookie()

    for item in submit_data:
        print("----------------------Processing: {}".format(json.dumps(item, indent=4)))
        pciid_url = "https://{}/read/PC/8086/{}".format(domain, item["id"])
        response = http_request(
            http_session, req_method="GET", req_url=pciid_url, req_cookie=cookie
        )
        if response.ok:
            # id exists
            name = html_parse(response.text)
            if item["name"] == name:
                continue
            else:
                # text=&name=&note=&subscribe=subscribe&submit=Submit
                update_url = "https://{}/read/PC/8086/{}?action=newhistory".format(
                    domain, item["id"]
                )
                http_request(
                    http_session,
                    req_method="POST",
                    req_url=update_url,
                    req_data={
                        "text": "",
                        "name": item["name"],
                        "note": "",
                        "subscribe": "subscribe",
                        "submit": "Submit",
                    },
                    req_cookie=cookie,
                )
        else:
            # create new
            new_url = "https://{}/mods/PC/8086?action=newitem".format(domain)
            # id=&name=&note=&discussion=&subscribe=subscribe&submit=Submit
            response = http_request(
                http_session,
                req_method="POST",
                req_url=new_url,
                req_data={
                    "id": item["id"].lower(),
                    "name": item["name"],
                    "note": "",
                    "discussion": "",
                    "subscribe": "subscribe",
                    "submit": "Submit",
                },
                req_cookie=cookie,
            )

    return 0


if __name__ == "__main__":
    # html_parse("")
    main()
