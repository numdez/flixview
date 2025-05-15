import requests

TMDB_API_KEY = "e7966d4567c0cd53b4f09250c477d9d4"
TMDB_API_URL = "https://api.themoviedb.org/3"

def map_tmdb_movie_to_app_movie(movie):
    """Converte os dados do TMDb para o formato do app"""
    return {
        "id": movie.get("id"),
        "title": movie.get("title"),
        "posterUrl": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
        "rating": round(movie.get("vote_average", 0), 1),
        "year": int(movie["release_date"].split("-")[0]) if movie.get("release_date") else 0,
    }

def search_movies(query, page=1):
    """Busca filmes por palavra-chave"""
    try:
        url = f"{TMDB_API_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
            "query": query,
            "page": page,
            "include_adult": False
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = [map_tmdb_movie_to_app_movie(movie) for movie in data.get("results", [])]
        return {
            "page": data.get("page"),
            "total_results": data.get("total_results"),
            "total_pages": data.get("total_pages"),
            "results": results
        }
    except Exception as e:
        print("Erro na API do TMDB (search_movies):", e)
        raise

def get_trending_movies():
    """Retorna filmes em alta na semana"""
    try:
        url = f"{TMDB_API_URL}/trending/movie/week"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [map_tmdb_movie_to_app_movie(movie) for movie in data.get("results", [])]
    except Exception as e:
        print("Erro na API do TMDB (get_trending_movies):", e)
        raise

def get_recent_movies():
    """Retorna filmes em cartaz (recentes)"""
    try:
        url = f"{TMDB_API_URL}/movie/now_playing"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
            "page": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [map_tmdb_movie_to_app_movie(movie) for movie in data.get("results", [])]
    except Exception as e:
        print("Erro na API do TMDB (get_recent_movies):", e)
        raise

def get_top_rated_movies():
    """Retorna filmes mais bem avaliados"""
    try:
        url = f"{TMDB_API_URL}/movie/top_rated"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
            "page": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [map_tmdb_movie_to_app_movie(movie) for movie in data.get("results", [])]
    except Exception as e:
        print("Erro na API do TMDB (get_top_rated_movies):", e)
        raise
