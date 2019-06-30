import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, exists, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer,  Sequence('user_seq'), primary_key=True)
    login = Column(String, nullable=False)
    password = Column(String)
    realname = Column(String)
    about_self = Column(String)
    start_date = Column(DateTime,default=datetime.datetime.now())
    end_date = Column(DateTime, default=datetime.datetime(year=2999,month=12,day=31))
    navi_date = Column(DateTime, default=datetime.datetime.now())


    def __init__(self, login, password, realname='', about_self=''):
        self.login = login
        self.realname = realname
        self.password = password
        self.about_self = about_self

    def __repr__(self):
        return "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (self.user_id, self.login, self.password, self.realname, self.about_self, self.start_date, self.end_date, self.navi_date)

class User_sessions(Base):
    __tablename__ = 'users_sessions'
    sesion_id = Column(Integer, Sequence('session_seq'), primary_key=True)
    login = Column(String, ForeignKey('users.login'))
    ip = Column(String)
    session_start_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, login, ip):
        self.login = login
        self.ip = ip

    def __repr__(self):
        return "'%s', '%s', '%s', '%s'" % (self.sesion_id, self.login, self.ip, self.session_start_date)

class User_contact_list(Base):
    __tablename__ = 'user_contact_list'
    list_rule_id =  Column(Integer, Sequence('list_rule_seq'), primary_key=True)
    owner_login = Column(String, ForeignKey('users.login'))
    in_list_login = Column(String, ForeignKey('users.login'))
    group = Column(String, default='General')

    def __init__(self, owner_login, in_list_login, group='General'):
        self.owner_login = owner_login
        self.in_list_login = in_list_login
        self.group = group

    def __repr__(self):
       return "'%s', '%s', '%s', '%s'" % (self.list_rule_id, self.owner_login, self.in_list_login, self.group)

if __name__ == "__main__":
    print('Now is ', datetime.datetime.now())
    #print(datetime.datetime.)
    #t = datetime.datetime(year=2999,month=12,day=31)
    #print(t.date())

    db_engine = create_engine('sqlite:///db.sqlite3')
    db_connection = db_engine.connect()
    Session = sessionmaker(bind=db_engine)
    session = Session()

    if not session.query(exists().where(User.login == 'Snegurka')).scalar():
        u = User('Snegurka','icecream')
        #u.__table__.create(db_engine)
        #u.__table__.drop(db_engine)
        us = User_sessions('Snegurka','127.0.0.1')
        #us.__table__.create(db_engine)
        #us.__table__.drop(db_engine)
        ucl = User_contact_list('Snegurka','Admin')
        #ucl.__table__.create(db_engine)
        #ucl.__table__.drop(db_engine)

        session.add(u)
        session.add(us)
        session.add(ucl)
        session.commit()


    if session.query(exists().where(User.login == 'Snegurka')).scalar():
            res1 = session.query(User).filter_by(login='Snegurka').first()
            print(res1)

    if bool(session.query(User_sessions).filter_by(login='Snegurka').count()):
        res2 = session.query(User_sessions).filter_by(login='Snegurka').first()
        print(res2)

    if bool(session.query(User_contact_list).filter_by(owner_login='Snegurka').count()):
        res2 = session.query(User_contact_list).filter_by(owner_login='Simper',in_list_login='Snegurka').delete()
        res3 = session.query(User_contact_list).filter_by(owner_login='Simper', in_list_login='Snegurka').all()
        print(res2)
        print(res3)
        session.commit()

    if session.query(exists().where(User.login == 'Admin')).scalar():
        #res3 = session.query(User).filter_by(login='Freeman').update({'password':'Half-Life 3'})
        res3 = session.query(User).all()
        print(res3)
        #session.commit()

    #u1 = User('Admin','qwerty123')
    #u1.__table__.drop(db_engine)
    #us = User_sessions('Admin', '127.0.0.1')
    #us.__table__.drop(db_engine)

    #u2 = User_contact_list('Admin', 'Admin')
    #u2.__table__.drop(db_engine)
    #session.commit()

    db_connection.close()
