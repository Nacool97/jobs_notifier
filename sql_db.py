from email.policy import default
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Boolean
import sqlalchemy
from hashlib import sha256

engine = create_engine('sqlite:///test_users.db?check_same_thread=False',echo=True)
connect = engine.connect()
meta = MetaData(bind=engine,reflect=True)
def create_table():
    users = Table(
        'test_user', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('username',String, unique=True),
        Column('password',String(100)),
        Column('name', String),
        Column('tel_chat_id', Integer),
        Column('email',String),
        Column('keyword_subs',String),
        Column('credits', Integer),
        Column('send_mail',Boolean, default=False)
    )
    meta.create_all(engine)
    print(users.columns.keys())
users = meta.tables['test_user']

def toggle_email(email):
    status = get_data(email)
    status1 = False
    if status:
        if not status[8]:
            status1 = True
        else:
            status1 = False
    query = sqlalchemy.update(users).values(send_mail=status1).where(users.columns.email==email)
    result = connect.execute(query)


def check_user_exists(chat_id=None, email=None):
    if chat_id:
        try:
            query = sqlalchemy.select([users]).where(users.columns.tel_chat_id==chat_id)
            check_result = connect.execute(query).fetchall()
        except Exception as e:
            print(e)
        print(check_result)
        if check_result:
            return True
    if email:
        try:
            query = sqlalchemy.select([users]).where(users.columns.email==email)
            check_result = connect.execute(query).fetchall()
        except Exception as e:
            print(e)
        print(check_result)
        if check_result:
            return True
    return False

def insert_values_in_users(name, username,chat_id, credits=2,password='12345'):
    user_check = check_user_exists(chat_id=chat_id)
    password = sha256(password.encode()).hexdigest()
    if not user_check:
        query = sqlalchemy.insert(users).values(
            name=name, tel_chat_id=chat_id,username=username, credits=credits,password=password)
        result = connect.execute(query)
        print(result)
        return result

def update_credits(credits, email=None,user_id=None,):
    if user_id:
        query = sqlalchemy.update(users).values(
            credits=credits).where(users.columns.tel_chat_id == user_id)
        result = connect.execute(query)
        
    if email:
        query = sqlalchemy.update(users).values(
            credits=credits).where(users.columns.email == email)
        result = connect.execute(query)
    return result

def update_keyword(keyword, user_id=None, email=None):
    rst = ""
    if user_id:
        query = sqlalchemy.select([users]).where(users.columns.tel_chat_id==user_id)
        result = connect.execute(query).fetchone()
        if result and result[6]:
            if result[6] != keyword:
                rst = result[6]+','+keyword
        elif result and not result[6]:
            rst = keyword
        else:
            return
        query = sqlalchemy.update(users).values(keyword_subs=rst).where(users.columns.tel_chat_id==user_id)
        connect.execute(query)
    if email:
        query = sqlalchemy.select([users]).where(users.columns.email==email)
        result = connect.execute(query).fetchone()
        if result and result[6]:
            if result[6] != keyword:
                rst = result[6]+','+keyword
        elif result and not result[6]:
            rst = keyword
        else:
            return
        query = sqlalchemy.update(users).values(keyword_subs=rst).where(users.columns.email==email)
        connect.execute(query)

def get_keywords(user_id=None, email=None):
    if user_id:
        query = sqlalchemy.select([users]).where(users.columns.tel_chat_id==user_id)
        result = connect.execute(query).fetchone()
        if result:
            if result[6]:
                return result[6]
        return
    if email:
        query = sqlalchemy.select([users]).where(users.columns.email==email)
        result = connect.execute(query).fetchone()
        if result:
            if result[6]:
                return result[6]
        return

def get_credit(user_id=None, email=None):
    if user_id:
        query = sqlalchemy.select([users]).where(users.columns.tel_chat_id==user_id)
        result = connect.execute(query).fetchone()
        if result:
            if result[7]:
                return result[7]
    if email:
        query = sqlalchemy.select([users]).where(users.columns.email==email)
        result = connect.execute(query).fetchone()
        if result:
            if result[7]:
                return result[7]
    return None
def insert_data(name,email,password,credit=2):
    user_check = check_user_exists(email=email)
    password = sha256(password.encode()).hexdigest()
    if not user_check:
        query = sqlalchemy.insert(users).values(
            name=name,
            password=password,
            email=email,
            credits=credit)
        print(connect.execute(query))

def get_data(email=None,chat_id=None):
    try:
        if email:
            query = sqlalchemy.select([users]).where(users.columns.email==email)
        elif chat_id:
            query = sqlalchemy.select([users]).where(users.columns.tel_chat_id==chat_id)        
    except Exception as e:
        print(e)
    
    result = connect.execute(query).fetchone()
    return result

def get_all_users():
    query = sqlalchemy.select([users])
    result = connect.execute(query).fetchall()
    return result

