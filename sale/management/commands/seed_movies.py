from django.core.management.base import BaseCommand
from suphasan.clickhouse import get_client


MOVIES = [
    (1, 'The Last Signal', 2024, 'Sci-Fi', 9.1, 12840),
    (2, 'Midnight in Kyoto', 2023, 'Drama', 8.8, 9640),
    (3, 'Northbound', 2024, 'Adventure', 8.6, 8120),
    (4, 'A Quiet Frequency', 2022, 'Thriller', 8.4, 7350),
    (5, 'Paper Moons', 2024, 'Romance', 8.2, 6890),
    (6, 'The Orchard House', 2021, 'Drama', 8.1, 6010),
    (7, 'After the Applause', 2023, 'Comedy', 7.9, 5800),
    (8, 'Gravity Season', 2022, 'Sci-Fi', 8.0, 5420),
]


class Command(BaseCommand):
    help = 'Adds demo movie ratings to ClickHouse when the table is empty'

    def handle(self, *args, **options):
        client = get_client()
        client.command('''
            CREATE TABLE IF NOT EXISTS movie_ratings (
                movie_id UInt64, movie_title String, release_year UInt16,
                genre LowCardinality(String), rating Float32, vote_count UInt32,
                rated_at DateTime DEFAULT now()
            ) ENGINE = ReplacingMergeTree(rated_at)
            ORDER BY (movie_id, rated_at)
        ''')
        if client.query('SELECT count() FROM movie_ratings').result_rows[0][0]:
            self.stdout.write('Movie ratings already contain data; skipped.')
            return
        client.insert('movie_ratings', MOVIES, column_names=[
            'movie_id', 'movie_title', 'release_year', 'genre', 'rating', 'vote_count',
        ])
        self.stdout.write(self.style.SUCCESS(f'Inserted {len(MOVIES)} movie ratings.'))