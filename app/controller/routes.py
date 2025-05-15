from app.controller.tmdb_api import get_trending_movies, get_recent_movies, get_top_rated_movies
from flask_login import logout_user, login_user, login_required, current_user
from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify, flash, send_file, make_response
from datetime import timedelta, datetime
from io import BytesIO
from pandas import DataFrame
import pandas as pd
from app import app, lm

# Fallbacks
fallback_movies = [
    {
        "id": 1,
        "title": "Duna: Parte 2",
        "posterUrl": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?...",
        "rating": 4.7,
        "year": 2024,
    },
    # ... outros filmes ...
]

recently_added_movies = [
    {
        "id": 10,
        "title": "Tudo em Todo Lugar",
        "posterUrl": "https://images.unsplash.com/photo-1582562124811-c09040d0a901?...",
        "rating": 4.7,
        "year": 2022,
    },
    # ... outros filmes ...
]

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        trending_movies = get_trending_movies()
    except:
        trending_movies = fallback_movies

    try:
        recent_movies = get_recent_movies()
    except:
        recent_movies = recently_added_movies

    try:
        top_rated_movies = get_top_rated_movies()
    except:
        top_rated_movies = fallback_movies

    return render_template("index.html",
                    trending_movies=trending_movies,
                    recent_movies=recent_movies,
                    top_rated_movies=top_rated_movies)

