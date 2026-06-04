from difflib import get_close_matches

class SearchService:
    """
    Real-time fuzzy search service for movie titles.
    """
    def __init__(self, movie_titles):
        self.movie_titles = movie_titles
        # Convert to list if series
        if not isinstance(self.movie_titles, list):
            self.movie_titles = self.movie_titles.tolist()

    def search(self, query, cutoff=0.6, n=5):
        """
        Finds close matches for the query string.
        """
        matches = get_close_matches(query, self.movie_titles, n=n, cutoff=cutoff)
        return matches
