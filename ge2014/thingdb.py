"""ThingDB.

Simplified verson of ThingDB, an idea by Aaron Swartz, used in Reddit and Infogami.
"""
import sys
import web
import json

@web.memoize
def get_db():
    params = web.config.get("db_parameters") or dict(dbn="postgres", db="ge2014")
    return web.database(**params)

class Thing(web.storage):
    def __init__(self, key, type, info, id=None):
        self.key = key
        self.type = type
        self.info = info
        self.id = id

    def url(self):
        return "/" + self.key

    @property
    def code(self):
        return self.key.split("/")[-1]

    @staticmethod
    def new(key, type, info):
        thing = Thing(key, type, info)
        thing.save()

    @staticmethod
    @web.memoize
    def find(key):
        result = get_db().select("thing", where="key=$key", vars=locals())
        if result:
            row = result[0]
            return Thing(id=row.id, key=row.key, type=row.type, info=json.loads(row.info))

    @staticmethod
    @web.memoize
    def find_by_id(id):
        result = get_db().select("thing", where="id=$id", vars=locals())
        if result:
            row = result[0]
            return Thing(id=row.id, key=row.key, type=row.type, info=json.loads(row.info))
            
    def save(self):
        info = dict(self.info)
        info['key'] = self.key
        info['type'] = self.type
        print "save", self.key
        
        db = get_db()
        with db.transaction():
            if self.id is None:
                self.id = db.insert("thing", key=self.key, type=self.type, info=json.dumps(info))
            else:
                db.update("thing", type=self.type, info=json.dumps(info), where="key=$key", vars={"key": self.key})
            db.delete("properties", where="thing_id=$self.id", vars=locals())
            db.multiple_insert("properties", [dict(thing_id=self.id, name=name, value=value) for name, value in self._get_refs()])

    def _get_refs(self):
        for k, v in self.info.items():
            if isinstance(v, dict) and 'key' in v:
                t = Thing.find(v['key'])
                if t:
                    yield k, t.id

    def get_references(self, type):
        return Thing.get_references0(self.id, type)

    @staticmethod
    @web.memoize
    def get_references0(thing_id, type):
        result = get_db().query("SELECT thing_id FROM properties, thing WHERE properties.thing_id=thing.id and thing.type=$type and value=$thing_id", vars=locals())
        return [Thing.find_by_id(row.thing_id) for row in result]
            
    def __getattr__(self, name):
        if name in ["id", "key", "type", "info"]:
            return web.storage.__getattr__(self, name)

        value = self.info[name]
        if isinstance(value, dict) and 'key' in value:
            return Thing.find(value['key'])
        else:
            return value

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return "<Thing#%s %s>" % (self.id, self.info)
        
