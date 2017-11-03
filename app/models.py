import os
import json
from app import db

## Used to store target keys. kid references Project.targetKeys
class Key(db.Model):
    __tablename__ = 'Key'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    kid = db.Column(db.Integer, nullable = False)
    number = db.Column(db.Integer, nullable = False)
    keyword = db.Column(db.String(64), nullable = False)

    keys = db.relationship('Project')

    ## A "toString()" method that prints the object in a nice format.
    def __repr__(self):
       return '<Key id = %d, kid = %d, number = %d, keyword = %s>' % (self.id,self.kid,self.number,self.keyword)

## Used to store countries of a project. tcid references Project.targetCountries
class Country(db.Model):
    __tablename__ = 'Country'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    tcid = db.Column(db.Integer, nullable = False)
    country = db.Column(db.String(64), nullable = False)

    countries = db.relationship('Project')

    ## A "toString()" method that prints the object in a nice format.
    def __repr__(self):
       return '<Country id = %d, tcid = %d, country = %s>' % (self.id,self.tcid,self.country)

class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key = True)
    projectName = db.Column(db.String(128), nullable = False)
    creationDate = db.Column(db.DateTime, nullable = False)
    expiryDate = db.Column(db.DateTime, nullable = False)
    enabled = db.Column(db.Boolean, nullable = False)
    targetCountries = db.Column(db.Integer, db.ForeignKey(Country.tcid), unique = True, nullable = False)
    projectCost = db.Column(db.Float,nullable = False)
    projectUrl = db.Column(db.String(128), nullable = True)
    targetKeys = db.Column(db.Integer, db.ForeignKey(Key.kid), unique = True, nullable = False)

    ## A "toString()" method that prints the object in a nice format.
    def __repr__(self):
        return '<Project id = %d, projectName = %s, creationDate = %r, expiryDate = %r, enabled = %r, tcid = %d, ProjectCost = %.2f, ProjectUrl = %s, kid = %d>' % (self.id,self.projectName,self.creationDate.strftime('%m/%d/%Y %H:%M:%S'),self.expiryDate.strftime('%m/%d/%Y %H:%M:%S'),self.enabled,self.targetCountries,self.projectCost,self.projectUrl,self.targetKeys)

## ORM framework helps us call necessary queries to help us setup the 3 tables above.
def init_db():
    db.create_all()
