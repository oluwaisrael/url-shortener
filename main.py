import random
import string
import json
import validators

from flask import Flask, render_template, redirect, request

app = Flask(__name__)
shortened_urls = {}

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    short_urls = "".join(random.choice(chars) for _ in range(length))
    return short_urls

def save_urls():
    with open("urls.json", "w") as f:
        json.dump(shortened_urls, f)

def load_urls():
    try:
        with open("urls.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}        

@app.route("/", methods=["GET", "POST"])
def index():
        
    if request.method == "POST":
        long_url = request.form['long_url']
        custom_alias = request.form["custom_alias"].strip()

        if not validators.url(long_url):
        
                return render_template(
                    "index.html",
                    error="Please enter a valid URL.",
                    long_url=long_url,
                    custom_alias=custom_alias
                )
        

        if custom_alias:

            if custom_alias in shortened_urls:
                return render_template(
                    "index.html",
                    error="Alias already exists.",
                    long_url=long_url,
                    custom_alias=custom_alias
                )

            short_url = custom_alias

        else:

            short_url = generate_short_url()

            while short_url in shortened_urls:
                short_url = generate_short_url()

        shortened_urls[short_url] = {
            "url": long_url,
            "clicks": 0
        }

        save_urls()
        
        return render_template(
            "index.html",
            short_url=request.url_root + short_url,
            clicks=shortened_urls[short_url]["clicks"]
        )   
    return render_template("index.html")


@app.route("/<short_url>")
def redirect_url(short_url):

    link = shortened_urls.get(short_url)

    if link:

        link["clicks"] += 1

        save_urls()

        return redirect(link["url"])

    return "URL not found", 404


if __name__ == "__main__":

    shortened_urls = load_urls()

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
