from rent_house import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    abbr_name = db.Column(db.String(20), nullable=False)
    districts = db.relationship('District', backref='city', lazy=True)
    lines = db.relationship('Line', backref='city', lazy=True)


bizcircle_district_table = db.Table(
    'bizcircle_district_table',
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True),
    db.Column('district_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    bizcircles = db.relationship('Bizcircle', secondary=bizcircle_district_table, lazy='subquery',
                                 backref=db.backref('districts', lazy=True))


bizcircle_line_table = db.Table(
    'bizcircle_line_table',
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True),
    db.Column('line_id', db.Integer, db.ForeignKey('line.id'), primary_key=True)
)


class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    name = db.Column(db.String(100), nullable=False)
    bizcircles = db.relationship('Bizcircle', secondary=bizcircle_line_table, lazy='subquery',
                                 backref=db.backref('lines', lazy=True))


community_bizcircle_table = db.Table(
    'community_bizcircle_table',
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True),
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True)
)


class Bizcircle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    communities = db.relationship('Community', secondary=community_bizcircle_table, lazy='subquery',
                                  backref=db.backref('bizcircles', lazy=True))


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.DateTime)
    flats = db.relationship('Flat', backref='community', lazy=True)


class Flat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    floor = db.Column(db.Integer)
    floor_total = db.Column(db.Integer)
    size = db.Column(db.Float, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer)
    cost = db.Column(db.Integer, nullable=False)
    is_whole_rent = db.Column(db.Boolean, nullable=False)
