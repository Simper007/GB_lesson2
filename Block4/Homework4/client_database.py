import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, exists, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Chat_histories(Base):
    __tablename__ = 'chat_histories'
    msg_id = Column(Integer,  Sequence('user_seq'), primary_key=True)
    history_owner = Column(String, nullable=False)
    message_owner = Column(String, nullable=False)
    message = Column(String)
    message_date = Column(DateTime,default=datetime.datetime.now())
    channel = Column(String)

    def __init__(self, user_login, msg_from, msg_to, msg):
        self.history_owner = user_login
        self.message_owner = msg_from
        self.message = msg
        self.channel = msg_to

    def __repr__(self):
        return "'%s', '%s', '%s', '%s', '%s', '%s'" % (self.msg_id, self.history_owner, self.message_owner, self.channel, self.message, self.message_date)

class User_contact_list(Base):
    __tablename__ = 'user_contact_list'
    list_rule_id =  Column(Integer, Sequence('list_rule_seq'), primary_key=True)
    owner_login = Column(String)
    in_list_login = Column(String)
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

    db_engine = create_engine('sqlite:///client_db.sqlite3')
    db_connection = db_engine.connect()
    Session = sessionmaker(bind=db_engine)
    session = Session()

    if not session.query(exists().where(Chat_histories.history_owner == 'Snegurka')).scalar():
        u = Chat_histories('Snegurka','Snegurka', 'Admin','Привет, Админ!')
        u.__table__.create(db_engine)
        #u.__table__.drop(db_engine)
        ucl = User_contact_list('Snegurka','Admin')
        ucl.__table__.create(db_engine)
        #ucl.__table__.drop(db_engine)
        session.add(u)
        session.add(ucl)
        session.commit()


    if session.query(exists().where(Chat_histories.history_owner == 'Snegurka')).scalar():
            res1 = session.query(Chat_histories).filter_by(history_owner='Snegurka').all()
            print(res1)

    if bool(session.query(User_contact_list).count()):
        #res2 = session.query(User_contact_list).filter_by(owner_login='Simper',in_list_login='Snegurka').delete()
        res3 = session.query(User_contact_list.in_list_login).all()
        #print(res2)
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
