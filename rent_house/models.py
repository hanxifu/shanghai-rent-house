from rent_house import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    abbr_name = db.Column(db.String(20), nullable=False)
    districts = db.relationship('District', backref='city', lazy=True)
    lines = db.relationship('Line', backref='city', lazy=True)

    def __str__(self):
        return f'{self.full_name}({self.abbr_name})'

    def __repr__(self):
        return f'{self.id} - {self.full_name}({self.abbr_name})\n' \
               f'{"/".join([str(district) for district in self.districts]) if self.districts else ""}\n' \
               f'{"/".join([str(line) for line in self.lines]) if self.lines else ""}'


bizcircle_district_table = db.Table(
    'bizcircle_district_table',
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True),
    db.Column('district_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    name_zh = db.Column(db.String(20), nullable=False)
    bizcircles = db.relationship('Bizcircle', secondary=bizcircle_district_table, lazy='subquery',
                                 backref=db.backref('districts', lazy=True))

    def __str__(self):
        return f'{self.name}({self.name_zh})'

    def __repr__(self):
        return f'{self.id} - {self.name}({self.name_zh})\n' \
               f'{"/".join([str(bizcircle) for bizcircle in self.bizcircles]) if self.bizcircles else ""}'


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.id} - {self.name}\n' \
               f'{"/".join([str(bizcircle) for bizcircle in self.bizcircles]) if self.bizcircles else ""}'


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.id} - {self.name}\n' \
               f'{"/".join([str(community) for community in self.communities]) if self.communities else ""}'


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.DateTime)
    flats = db.relationship('Flat', backref='community', lazy=True)

    def __str__(self):
        return f'{self.name}({self.year})'

    def __repr__(self):
        nl = '\n'
        return f'{self.id} - {self.name}\n' \
               f'{nl.join([str(flat) for flat in self.flats]) if self.flats else ""}'


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

    def __str__(self):
        return f'{self.floor}/{self.floor_total} {self.size}m2 {self.rooms}rooms/{self.bathrooms}bathrooms ' \
               f'- {self.cost} - {"entire" if self.is_whole_rent else "share"}'

    def __repr__(self):
        community_instance = Community.query.get(self.community_id)
        return f'{community_instance}\n' \
               f'{self.__str__()}'
