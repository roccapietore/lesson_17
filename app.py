from flask import Flask, request
from flask_restx import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

parser = reqparse.RequestParser()
parser.add_argument("director_id", type=int)
parser.add_argument("genre_id", type=int)


# MOVIES

@movie_ns.route("/")
class MoviesView(Resource):
    @api.expect(parser)
    def get(self):
        movies_director = parser.parse_args()["director_id"]
        movies_genre = parser.parse_args()["genre_id"]

        if movies_director and movies_genre:  # поиск фильмов по режиссеру и жанру
            filtered_movies = Movie.query.filter_by(director_id=movies_director, genre_id=movies_genre).all()

        elif movies_genre:  # поиск фильмов по жанру
            filtered_movies = Movie.query.filter_by(genre_id=movies_genre).all()

        elif movies_director:  # поиск фильмов по режиссеру
            filtered_movies = Movie.query.filter_by(director_id=movies_director).all()

        else:  # вывод всех фильмов по страницам
            query_parameters = request.args
            limit = query_parameters.get("limit", 5)
            start = query_parameters.get("start", 0)
            filtered_movies = Movie.query.limit(limit).offset(start).all()

        if not filtered_movies:
            return "", 404

        movies = movies_schema.dump(filtered_movies)
        return movies, 200

    def post(self):
        req_json = request.json
        new_movies = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movies)
        return "", 201


@movie_ns.route("/<id>")
class MovieView(Resource):
    def get(self, id: int):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        get_movie = movie_schema.dump(movie)
        return get_movie, 200

    def put(self, id: int):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        req_json = request.json
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, id: int):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


# DIRECTORS

@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_movies = Director.query.all()
        if not all_movies:
            return "", 404
        movies = directors_schema.dump(all_movies)
        return movies, 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route("/<id>")
class DirectorView(Resource):
    def get(self, id: int):
        movie = Director.query.get(id)
        if not movie:
            return "", 404
        get_movie = director_schema.dump(movie)
        return get_movie, 200

    def put(self, id: int):
        director = Genre.query.get(id)
        if not director:
            return "", 404
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, id: int):
        movie = Director.query.get(id)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


# GENRES

@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        if not all_genres:
            return "", 404
        genres = genres_schema.dump(all_genres)
        return genres, 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route("/<id>")
class GenreView(Resource):
    def get(self, id: int):
        genre = Genre.query.get(id)
        if not genre:
            return "", 404
        get_genre = genre_schema.dump(genre)
        return get_genre, 200

    def put(self, id: int):
        genre = Genre.query.get(id)
        if not genre:
            return "", 404
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, id: int):
        genre = Genre.query.get(id)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(port=5009, debug=True)
