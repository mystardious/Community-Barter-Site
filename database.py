
import sqlite3
import hashlib
import string
import secrets
import datetime


# The database name
DATABASE_NAME = 'comp4050.db'

def password_hash(db, password, user):
    """Return a one-way hashed version of the password suitable for
    storage in the database, checks if a user name an password is provided,
    salts the password and returns it"""
    if len(user) > 0 and len(password) > 6:
        check = True
    else:
        check = False
    if check:
        salt = return_salt(db, user)
        if salt:
            return hashlib.sha256((password + salt).encode()).hexdigest()
        else:
            return False

def firstPassword_hash(password, salt):
    """Return a one-way hashed version of the password suitable for
    storage in the database, salts password and returns,
    used in database table initilisation """

    return hashlib.sha256((password + salt).encode()).hexdigest()

def return_salt(db, user):
    """returns a salt value for a user, could move this to users module but cbbs"""
    cursor = db.cursor()

    sql = """SELECT rand FROM users WHERE username=?"""
    cursor.execute(sql,(user,))
    data = cursor.fetchone()
    if data is None:
        return False
    else:
        return data[0]

def create_tables(db):
    """Create and initialise the database tables. Will ovewrite
    on each call"""

    sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username text,
    password text,
    userID integer unique primary key autoincrement,
    name test,
    suburb text,
    rand text,
    avatar text
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
    sessionid text unique primary key,
    user text,
    FOREIGN KEY(user) REFERENCES users(username)
);

DROP TABLE IF EXISTS jobListing;
CREATE TABLE jobListing (
    jobID integer unique primary key autoincrement,
    timestamp text default CURRENT_TIMESTAMP,
    owner text,
    title text,
    location text, 
    description text,
    FOREIGN KEY(owner) REFERENCES users(username)
);
"""

    db.executescript(sql)
    db.commit()


def generate_salt():
    """returns a random 8 character value consisting of
    upper and lower case characters  and single digits"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password

def add_user(db, password, email, name, suburb):
    """"Adds a user to the database , ensures username is not already in use"""
    cursor = db.cursor()
    #check username is not in use
    sql = "SELECT 1 FROM users WHERE username=?"
    data = cursor.execute(sql,(email,))
    if data.fetchone():
        return False
    else:
        salt = generate_salt()
        sql = "INSERT INTO users (username, password, name, suburb, rand) VALUES (?,?,?,?,?)"
        cursor.execute(sql, [email, firstPassword_hash(password, salt), name, suburb, salt])
        db.commit()
        return True


def print_users(db):
    """printing users table for troubleshooting"""
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    for row in data:
        print(row[0])
        print(row[1])
        print(row[2])
        print(row[3])
        print(row[4])
        print(row[5])


def add_jobListing(db, postOwner, title, location, description):
    """CHANGE THIS LATER Add a new job post to the database.
    The date of the post will be the current time and date.

    Return True if the record was added, False if not."""
    cursor = db.cursore()
    sql = """INSERT INTO jobListing (owner, title, location, description) VALUES (?, ?, ?, ?)"""
    cursor.execute(sql, [postOwner, title, location, description])
    db.commit()

    return True


def get_listing(db, id):
    """Return the details of the position with the given id
    or None if there is no position with this id

    Returns a tuple (id, timestamp, owner, title, location, company, description)

    """

    cursor = db.cursor()
    sql = "SELECT * FROM jobListing WHERE id=?"
    data = cursor.execute(sql,(id,))
    return data.fetchone()#fetchone only works only once unless you make data.fetchone returns list if it exists doesnt otherwise

def delete_jobListing(db, id):
    """CHANGE LATER, Delete a joblisting"""

    cursor = db.cursor()
    sql = "DELETE FROM jobListing WHERE jobID=?"
    cursor.execute(sql,(id,))


def position_list(db, limit=10):
    """Return a list of jobs ordered by date
    db is a database connection
    return at most limit positions (default 10)

    Returns a list of tuples  (id, timestamp, owner, title, location, company, description)
    """
    sql="SELECT * FROM jobListing ORDER BY timestamp DESC LIMIT ?"
    cursor = db.cursor()
    data = cursor.execute(sql,(limit,))
    return list(data)


if __name__=='__main__':

    """need to call this directly to intilise tables / clear tables"""
    db = sqlite3.connect(DATABASE_NAME)
    create_tables(db)

