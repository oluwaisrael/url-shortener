import random
import string
import validators

from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///links.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    short_url = db.Column(db.String(20), unique=True, nullable=False)

    long_url = db.Column(db.Text, nullable=False)

    clicks = db.Column(db.Integer, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# Generate random short code
def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        long_url = request.form["long_url"]
        custom_alias = request.form.get("custom_alias", "").strip()

        # Validate URL
        if not validators.url(long_url):
            return render_template(
                "index.html",
                error="Please enter a valid URL.",
                long_url=long_url,
                custom_alias=custom_alias
            )

        # Custom alias
        if custom_alias:

            existing = Link.query.filter_by(
                short_url=custom_alias
            ).first()

            if existing:
                return render_template(
                    "index.html",
                    error="Alias already exists.",
                    long_url=long_url,
                    custom_alias=custom_alias
                )

            short_url = custom_alias

        else:

            short_url = generate_short_url()

            while Link.query.filter_by(
                short_url=short_url
            ).first():
                short_url = generate_short_url()

        # Save to database
        link = Link(
            short_url=short_url,
            long_url=long_url
        )

        db.session.add(link)
        db.session.commit()

        return render_template(
            "index.html",
            short_url=request.url_root + short_url,
            clicks=link.clicks
        )
    links = Link.query.order_by(Link.created_at.desc()).all()

    return render_template(
        "index.html",
        short_url=request.url_root + short_url,
        clicks=link.clicks,
        links=links
    )


@app.route("/<short_url>")
def redirect_url(short_url):

    link = Link.query.filter_by(
        short_url=short_url
    ).first()

    if link:

        link.clicks += 1
        db.session.commit()

        return redirect(link.long_url)

    return "URL not found", 404

@app.route("/stats/<short_url>")
def stats(short_url):

    link = Link.query.filter_by(
        short_url=short_url
    ).first()

    if not link:
        return "URL not found", 404

    return render_template(
        "stats.html",
        link=link,
        short_url=request.url_root + short_url
    )


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )