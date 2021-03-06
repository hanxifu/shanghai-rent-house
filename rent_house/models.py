from rent_house import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_abbr = db.Column(db.String(20), nullable=False)
    districts = db.relationship('District', backref='city', lazy=True)
    lines = db.relationship('Line', backref='city', lazy=True)

    def __str__(self):
        return f'{self.name}({self.name_abbr})'

    def __repr__(self):
        return f'{self.id} - {self.name}({self.name_abbr})\n' \
               f'{"/".join([str(district) for district in self.districts]) if self.districts else ""}\n' \
               f'{"/".join([str(line) for line in self.lines]) if self.lines else ""}'


bizcircle_districts_table = db.Table(
    'bizcircle_district_table',
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True),
    db.Column('district_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)

bizcircle_lines_table = db.Table(
    'bizcircle_line_table',
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True),
    db.Column('line_id', db.Integer, db.ForeignKey('line.id'), primary_key=True)
)

community_bizcircles_table = db.Table(
    'community_bizcircle_table',
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True),
    db.Column('bizcircle_id', db.Integer, db.ForeignKey('bizcircle.id'), primary_key=True)
)


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    name_zh = db.Column(db.String(20), nullable=False)

    # many-to-many District<->Bizcircle
    bizcircles = db.relationship('Bizcircle', secondary=bizcircle_districts_table, lazy='subquery',
                                 backref=db.backref('districts', lazy=True))

    def __str__(self):
        return f'{self.name}({self.name_zh})'

    def __repr__(self):
        return f'{self.id} - {self.name}({self.name_zh})\n' \
               f'{"/".join([str(bizcircle) for bizcircle in self.bizcircles]) if self.bizcircles else ""}'


class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    name = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)

    # many-to-many Line<->Bizcircle
    bizcircles = db.relationship('Bizcircle', secondary=bizcircle_lines_table, lazy='subquery',
                                 backref=db.backref('lines', lazy=True))

    def __str__(self):
        return f'{self.name}({self.name_zh})'

    def __repr__(self):
        return f'{self.id} - {self.name}({self.name_zh})\n' \
               f'{"/".join([str(bizcircle) for bizcircle in self.bizcircles]) if self.bizcircles else ""}'


class Bizcircle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    name = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)

    # many-to-many Bizcircle<->Community
    communities = db.relationship('Community', secondary=community_bizcircles_table, lazy='subquery',
                                  backref=db.backref('bizcircles', lazy=True))

    def __str__(self):
        return f'{self.name}({self.name_zh})'

    def __repr__(self):
        return f'{self.id} - {self.name}({self.name_zh})\n' \
               f'{"/".join([str(community) for community in self.communities]) if self.communities else ""}'


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    name = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    price = db.Column(db.Integer)
    flats = db.relationship('Flat', backref='community', lazy=True)

    def __str__(self):
        return f'{self.name}({self.name_zh}<{self.year}>)'

    def __repr__(self):
        nl = '\n'
        return f'{self.id} - {self.name}({self.name_zh})\n' \
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
