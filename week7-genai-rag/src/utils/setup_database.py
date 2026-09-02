import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS sales;
    DROP TABLE IF EXISTS albums;
    DROP TABLE IF EXISTS artists;

    CREATE TABLE artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

    CREATE TABLE albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES artists(id)
    );

    CREATE TABLE sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        album_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (album_id) REFERENCES albums(id)
    );
    """)

    artists = [
        ("Arijit Singh",),
        ("Shreya Ghoshal",),
        ("A.R. Rahman",),
        ("Sonu Nigam",)
    ]

    cursor.executemany(
        "INSERT INTO artists (name) VALUES (?)",
        artists
    )

    albums = [
        ("Soulful Hits", 1),
        ("Melody Collection", 2),
        ("Timeless Classics", 3),
        ("Golden Voice", 4),
        ("Romantic Nights", 1),
        ("Musical Journey", 2)
    ]

    cursor.executemany(
        """
        INSERT INTO albums (title, artist_id)
        VALUES (?, ?)
        """,
        albums
    )

    sales = [
        (1, 120, 199.0, "2023-01-15"),
        (1, 85, 199.0, "2023-03-12"),
        (2, 100, 179.0, "2023-02-10"),
        (2, 140, 179.0, "2023-07-18"),
        (3, 90, 249.0, "2023-04-22"),
        (3, 110, 249.0, "2023-11-05"),
        (4, 75, 189.0, "2023-05-09"),
        (4, 95, 189.0, "2023-09-14"),
        (5, 130, 219.0, "2023-06-17"),
        (5, 105, 219.0, "2024-01-20"),
        (6, 115, 209.0, "2023-08-11"),
        (6, 125, 209.0, "2024-03-25")
    ]

    cursor.executemany(
        """
        INSERT INTO sales (
            album_id,
            quantity,
            unit_price,
            sale_date
        )
        VALUES (?, ?, ?, ?)
        """,
        sales
    )

    connection.commit()
    connection.close()

    print(f"Database created successfully at: {DB_PATH}")


if __name__ == "__main__":
    create_database()