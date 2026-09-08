from django.http import JsonResponse
from django.shortcuts import render
from suphasan.clickhouse import get_client


DEMO_MOVIES = [
    {'title': 'The Last Signal', 'year': 2024, 'genre': 'Sci-Fi', 'rating': 9.1, 'votes': 12840, 'poster': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=85'},
    {'title': 'Midnight in Kyoto', 'year': 2023, 'genre': 'Drama', 'rating': 8.8, 'votes': 9640, 'poster': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=85'},
    {'title': 'Northbound', 'year': 2024, 'genre': 'Adventure', 'rating': 8.6, 'votes': 8120, 'poster': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=85'},
    {'title': 'A Quiet Frequency', 'year': 2022, 'genre': 'Thriller', 'rating': 8.4, 'votes': 7350, 'poster': 'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=600&q=85'},
    {'title': 'Paper Moons', 'year': 2024, 'genre': 'Romance', 'rating': 8.2, 'votes': 6890, 'poster': 'https://images.unsplash.com/photo-1518568740560-333139a27e72?auto=format&fit=crop&w=600&q=85'},
]

POSTER_BY_GENRE = {
    'Sci-Fi': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=85',
    'Drama': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=85',
    'Adventure': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=85',
    'Thriller': 'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=600&q=85',
    'Romance': 'https://images.unsplash.com/photo-1518568740560-333139a27e72?auto=format&fit=crop&w=600&q=85',
}


def _demo_payload():
    return {
        'kpis': {'movies': 2486, 'votes': 184200, 'average': 7.8, 'top_genre': 'Drama'},
        'movies': DEMO_MOVIES,
        'genres': [
            {'name': 'Drama', 'count': 584, 'average': 7.9},
            {'name': 'Action', 'count': 412, 'average': 7.5},
            {'name': 'Comedy', 'count': 368, 'average': 7.4},
            {'name': 'Sci-Fi', 'count': 255, 'average': 8.1},
            {'name': 'Thriller', 'count': 221, 'average': 7.7},
        ],
        'trend': [
            {'month': 'Jan', 'average': 7.4}, {'month': 'Feb', 'average': 7.6},
            {'month': 'Mar', 'average': 7.5}, {'month': 'Apr', 'average': 7.8},
            {'month': 'May', 'average': 7.7}, {'month': 'Jun', 'average': 7.9},
        ],
        'source': 'demo',
    }


def _movie_payload():
    try:
        client = get_client()
        if not client.query("EXISTS TABLE movie_ratings").result_rows[0][0]:
            return _demo_payload()
        kpis = client.query('''
            SELECT countDistinct(movie_id), sum(vote_count), round(avg(rating), 1)
            FROM movie_ratings
        ''').result_rows[0]
        movies = client.query('''
            SELECT movie_title, release_year, genre, round(rating, 1), vote_count
            FROM movie_ratings ORDER BY rating DESC, vote_count DESC LIMIT 5
        ''').result_rows
        genres = client.query('''
            SELECT genre, countDistinct(movie_id), round(avg(rating), 1)
            FROM movie_ratings GROUP BY genre ORDER BY count() DESC LIMIT 5
        ''').result_rows
        trend = client.query('''
            SELECT formatDateTime(toStartOfMonth(rated_at), '%b'), round(avg(rating), 1)
            FROM movie_ratings GROUP BY toStartOfMonth(rated_at)
            ORDER BY toStartOfMonth(rated_at) DESC LIMIT 6
        ''').result_rows
        top_genre = client.query('''
            SELECT genre FROM movie_ratings GROUP BY genre ORDER BY avg(rating) DESC LIMIT 1
        ''').result_rows
        return {
            'kpis': {'movies': kpis[0], 'votes': kpis[1], 'average': kpis[2],
                     'top_genre': top_genre[0][0] if top_genre else '-'},
            'movies': [dict(dict(zip(('title', 'year', 'genre', 'rating', 'votes'), row)), poster=POSTER_BY_GENRE.get(row[2], POSTER_BY_GENRE['Drama'])) for row in movies],
            'genres': [dict(zip(('name', 'count', 'average'), row)) for row in genres],
            'trend': [dict(zip(('month', 'average'), row)) for row in reversed(trend)],
            'source': 'clickhouse',
        }
    except Exception:
        return _demo_payload()


def dashboard(request):
    return render(request, 'analytics/dashboard.html', {'dashboard': _movie_payload()})


def dashboard_data(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        genre = request.POST.get('genre', 'Drama').strip()
        year = int(request.POST.get('year', 2024))
        rating = float(request.POST.get('rating', 7.0))
        votes = int(request.POST.get('votes', 1))
        if not title or not 0 <= rating <= 10 or votes < 1:
            return JsonResponse({'error': 'Invalid movie rating'}, status=400)
        existing = next((movie for movie in DEMO_MOVIES if movie['title'].casefold() == title.casefold()), None)
        movie_id = existing.get('id', DEMO_MOVIES.index(existing) + 1) if existing else len(DEMO_MOVIES) + 1
        movie = {
            'id': movie_id, 'title': title, 'year': year, 'genre': genre,
            'rating': rating, 'votes': votes,
            'poster': POSTER_BY_GENRE.get(genre, POSTER_BY_GENRE['Drama']),
        }
        try:
            client = get_client()
            client.insert('movie_ratings', [[movie_id, title, year, genre, rating, votes]], column_names=[
                'movie_id', 'movie_title', 'release_year', 'genre', 'rating', 'vote_count',
            ])
        except Exception:
            # Local no-Docker mode keeps the newly submitted row in this process.
            pass
        if existing:
            existing.update(movie)
        else:
            DEMO_MOVIES.append(movie)
        return JsonResponse({'ok': True, 'movie': movie})
    return JsonResponse(_movie_payload())
