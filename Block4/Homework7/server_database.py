import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, exists, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from binascii import hexlify
#import hashlib

Base = declarative_base()


class User(Base):
    """
    Класс описывающий таблицу пользователей. Содержит id пользователя, логин, хешированный пароль, настоящее имя, инфо о себе, даты действия записи и дату создания.
    """
    __tablename__ = 'users'
    user_id = Column(Integer, Sequence('user_seq'), primary_key=True)
    login = Column(String, nullable=False)
    password = Column(String)
    realname = Column(String)
    about_self = Column(String)
    start_date = Column(DateTime, default=datetime.datetime.now())
    end_date = Column(
        DateTime,
        default=datetime.datetime(
            year=2999,
            month=12,
            day=31))
    navi_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, login, password, realname='', about_self=''):
        self.login = login
        self.realname = realname
        self.password = password
        self.about_self = about_self

    def __repr__(self):
        return "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
            self.user_id, self.login, self.password, self.realname, self.about_self, self.start_date, self.end_date, self.navi_date)


class User_sessions(Base):
    """
    Класс описывающий таблицу с историей входов пользователей. Содержит id сессии, логин, ip адрес и дату сессии.
    """
    __tablename__ = 'users_sessions'
    sesion_id = Column(Integer, Sequence('session_seq'), primary_key=True)
    login = Column(String, ForeignKey('users.login'))
    ip = Column(String)
    session_start_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, login, ip):
        self.login = login
        self.ip = ip

    def __repr__(self):
        return "'%s', '%s', '%s', '%s'" % (
            self.sesion_id, self.login, self.ip, self.session_start_date)


class Users_online(Base):
    """
    Класс описывающий таблицу с информацией о подключенных в настоящий момент пользователях. Содержит логин, ip адрес и дату подключения.
    """
    __tablename__ = 'users_online'
    login = Column(String, ForeignKey('users.login'), primary_key=True)
    ip = Column(String)
    start_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, login, ip):
        self.login = login
        self.ip = ip

    def __repr__(self):
        return "'%s', '%s', '%s'" % (
            self.login, self.ip, self.start_date)


class User_contact_list(Base):
    """
    Класс описывающий таблицу списка контактов пользователя на сервере. Содержит владельца списка, контакт и группу.
    """
    __tablename__ = 'user_contact_list'
    list_rule_id = Column(Integer, Sequence('list_rule_seq'), primary_key=True)
    owner_login = Column(String, ForeignKey('users.login'))
    in_list_login = Column(String, ForeignKey('users.login'))
    group = Column(String, default='General')

    def __init__(self, owner_login, in_list_login, group='General'):
        self.owner_login = owner_login
        self.in_list_login = in_list_login
        self.group = group

    def __repr__(self):
        return "'%s', '%s', '%s', '%s'" % (
            self.list_rule_id, self.owner_login, self.in_list_login, self.group)


if __name__ == "__main__":
    print('Now is ', datetime.datetime.now())
    # print(datetime.datetime.)
    #t = datetime.datetime(year=2999,month=12,day=31)
    # print(t.date())

    db_engine = create_engine('sqlite:///db.sqlite3')
    db_connection = db_engine.connect()
    Session = sessionmaker(bind=db_engine)
    session = Session()

    if not session.query(exists().where(User.login == 'Snegurka')).scalar():
        u = User('Snegurka', 'icecream')
        # u.__table__.create(db_engine)
        # u.__table__.drop(db_engine)
        us = Users_online('Snegurka', '127.0.0.1')
        us.__table__.create(db_engine)
        # us.__table__.drop(db_engine)
        ucl = User_contact_list('Snegurka', 'Admin')
        # ucl.__table__.create(db_engine)
        # ucl.__table__.drop(db_engine)

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

    if bool(
            session.query(User_contact_list).filter_by(
            owner_login='Simper').count()):
        #res2 = session.query(User_contact_list).filter_by(
            #owner_login='Simper', in_list_login='Snegurka').delete()
        res3 = session.query(User_contact_list).filter_by(
            owner_login='Simper').all()
        #print(res2)
        print('cl',res3)
        session.commit()

    if session.query(exists().where(User.login == 'Admin')).scalar():
        #res3 = session.query(User).filter_by(login='Freeman').update({'password':'Half-Life 3'})
        res3 = session.query(Users_online).all()
        print(res3)
        # session.commit()

    #user = session.query(User).filter_by(login='Simper').all()
    user = [session.query(User.login,User.password).all()][0]
    print('first',user)
    print(user[0][0])
    #pwd_hash = hashlib.pbkdf2_hmac('sha256', 'qwerty'.encode('utf-8'),
    #                                      'Admin'.encode('utf-8'), 1000)
    #print(pwd_hash)
    #print(hexlify(pwd_hash))
    #print(hexlify(pwd_hash).decode('utf-8'))

    #session.query(User).filter_by(login='Admin').update({'password': hexlify(pwd_hash).decode('utf-8')})
    #session.commit()
    #user[0][1] = hexlify(pwd_hash).decode('utf-8')

    user = [session.query(User.login, User.password).filter_by(login='Freeman').all()][0]
    print('second',user)

    #us = Users_online('Snegurka', '127.0.0.1')
    # us.__table__.create(db_engine)
    #u1 = User('Admin','qwerty123')
    # u1.__table__.drop(db_engine)
    #us = User_sessions('Admin', '127.0.0.1')
    # us.__table__.drop(db_engine)

    #u2 = User_contact_list('Admin', 'Admin')
    # u2.__table__.drop(db_engine)
    # session.commit()

    db_connection.close()
