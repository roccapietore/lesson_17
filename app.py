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


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')

parser = reqparse.RequestParser()
parser.add_argument("director_id", type=int)
parser.add_argument("genre_id", type=int)


@movie_ns.route("/")
class MoviesView(Resource):
    @api.expect(parser)
    def get(self):
        movies_director = parser.parse_args()["director_id"]
        movies_genre = parser.parse_args()["genre_id"]

        if movies_director and movies_genre:                   # поиск фильмов по режиссеру и жанру
            filtered_movies = Movie.query.filter_by(director_id=movies_director, genre_id=movies_genre).all()

        elif movies_genre:                                    # поиск фильмов по жанру
            filtered_movies = Movie.query.filter_by(genre_id=movies_genre).all()

        elif movies_director:                                   # поиск фильмов по режиссеру
            filtered_movies = Movie.query.filter_by(director_id=movies_director).all()

        else:    # вывод всех фильмов по страницам
            query_parameters = request.args
            limit = query_parameters.get("limit", 5)
            start = query_parameters.get("start", 0)
            filtered_movies = Movie.query.limit(limit).offset(start).all()

        if not filtered_movies:
            return "", 404

        movies = movies_schema.dump(filtered_movies)
        return movies, 200


@movie_ns.route("/<id>")
class MoviesView(Resource):
    def get(self, id: int):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        get_movie = movie_schema.dump(movie)
        return get_movie, 200


if __name__ == '__main__':
    app.run(port=5009, debug=True)
