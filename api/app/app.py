# app.py - a minimal flask api using flask_restful

import flask
from flask import request, jsonify
from flask_cors import CORS # add this line to overcome "No 'Access-Control-Allow-Origin' header is present on the requested resource." issue
import psycopg2
import psycopg2.extras
from config import config
from gevent.pywsgi import WSGIServer

app = flask.Flask(__name__)
CORS(app) # add this line to overcome "No 'Access-Control-Allow-Origin' header is present on the requested resource." issue # look into security configuraiton

@app.route('/api/v1/categories', methods = ['GET'])
def get_categories():
    """ Get all categories """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        SELECT id AS cid, CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category FROM categories
        """)
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/users', methods = ['GET'])
def get_users():
    """ Get user data """
    conn = None
    if not 'email' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'email'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        SELECT id AS uid, first, last, email FROM person
        WHERE email='{}' AND person.deleted = 'f'""".format(request.args['email']))
        ans = cur.fetchone()
        if ans is None:
            return jsonify({'code':204, 'name':'No Content', 'key':'id'})
        return jsonify( dict(ans) )
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/groups', methods = ['GET'])
def get_groups():
    """ Get user group(s) """
    conn = None
    if not 'email' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'email'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        SELECT exp_group.id AS gid, name FROM exp_group
        INNER JOIN
          (SELECT * FROM user_group) AS gid ON exp_group.id = gid.gid
        INNER JOIN
          (SELECT id as uid, email, deleted FROM person WHERE email = '{}') AS person ON gid.uid = person.uid
        WHERE exp_group.deleted = 'f' AND person.deleted = 'f'""".format(request.args['email']))
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content', 'key':'gid'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/group_members', methods = ['GET'])
def get_group_members():
    """ Get group members """
    conn = None
    if not 'gid' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'gid'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        SELECT user_group.uid, people.first, people.last, user_group.admin FROM user_group
        INNER JOIN
            (SELECT * FROM person) AS people ON user_group.uid = people.id
        WHERE gid='{}'""".format(request.args['gid']))
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content', 'key':'gid'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/users_new', methods = ['GET'])
def get_users_new():
    """ Create new user """
    conn = None
    if not 'email' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'email'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        INSERT INTO person(email) VALUES ('{}') RETURNING id AS uid, first, last, email
        """.format(request.args['email']))
        ans = cur.fetchone()
        conn.commit()
        if ans is None:
            return jsonify({'code':204, 'name':'No Content', 'key':'id'})
        return jsonify({'uid':ans[0], 'first':ans[1], 'last':ans[2], 'email':ans[3]})
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/group_new', methods = ['GET'])
def get_group_new():
    """ Create new group """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
        INSERT INTO exp_group(deleted) VALUES('f') RETURNING id AS gid, name
        """)
        ans = cur.fetchone()
        conn.commit()
        if ans is None:
            return jsonify({'code':204, 'name':'No Content', 'key':'id'})
        return jsonify({'gid':ans[0], 'name':ans[1]})
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/expenses/new_user_group', methods = ['GET'])
def user_group_new():
    """ Link new user to new group """
    conn = None
    fault = []
    if not 'uid' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'uid'})
    if not 'gid' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'gid'})
    if (len(fault) > 0):
        return jsonify(fault)
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO user_group(uid, gid, admin) VALUES ('{}', '{}', 't')""".format(
            request.args['uid'],
            request.args['gid']))
        conn.commit()
        return jsonify([{'code':201, 'name': 'Created'}])
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()
# edit user

@app.route('/api/v1/expenses', methods=['GET'])
def get_expenses():
    """ return all expenses for user group id """
    conn = None
    if not 'gid' in request.args:
        return jsonify({'code':400, 'name':'Bad Request', 'key':'gid'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT expenses.id as id, date, person.id AS uid, person.first AS who, expenses.amount, cat.id AS cid, cat.category, stores.id AS sid, stores.name AS store, expenses.notes, expenses.root_id
            FROM expenses
            LEFT JOIN person
            ON expenses.who = person.id
            LEFT JOIN
                (SELECT id, CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category FROM categories) AS cat
            ON expenses.category = cat.id
            LEFT JOIN stores
            ON expenses.store = stores.id
            WHERE expenses.gid='{}' AND expenses.deleted='f'
            ORDER BY expenses.date DESC""".format(request.args['gid']))
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content', 'key':'gid'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/expenses/new', methods = ['GET'])
def expenses_new():
    """ Write new expense """
    conn = None
    fault = []
    if not 'gid' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'gid'})
    if not 'amount' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'amount'})
    if not 'date' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'date'})
    if not 'uid' in request.args:
        fault.append({'code': 400, 'name': 'Bad Request', 'key': 'uid'})
    if (len(fault) > 0):
        return jsonify(fault)
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expenses (gid, amount, date, who, category, store, notes, root_id, mod_user)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(
                request.args['gid'],
                request.args['amount'],
                request.args['date'],
                request.args['uid'],
                request.args['cid'] if 'cid' in request.args else '$NULL$',
                request.args['store'] if 'store' in request.args else '$NULL$',
                request.args['notes'] if 'notes' in request.args else '$NULL$',
                request.args['root_id'] if 'root_id' in request.args else '$NULL$',
                request.args['mod_user'] if 'mod_user' in request.args else '$NULL$').replace("'$NULL$'","NULL"))
        conn.commit()
        return jsonify([{'code':201, 'name': 'Created'}])
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/expenses/remove', methods = ['GET'])
def expenses_remove():
    """ Remove expense """
    conn = None
    if not 'rid' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'rid'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("UPDATE expenses SET deleted = 't' WHERE id='%s'" % request.args['rid'])
        conn.commit()
        return jsonify({'code':200, 'name': 'OK'})
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/months/person', methods=['GET'])
def get_months_person():
    """ return all expenses per person by month in group id (need to do error control)"""
    conn = None
    if not 'gid' in request.args:
        return jsonify({'code':400, 'name':'Bad Request', 'key':'gid'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT SUBSTR(cast(expenses.date AS text), 1, 6) AS month, person.first AS person, sum(expenses.amount)
            FROM expenses
            LEFT JOIN person ON expenses.who = person.id
            WHERE expenses.gid = '{}' AND expenses.deleted ='f'
            GROUP BY month, person.first
            ORDER BY month""".format(request.args['gid']))
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content', 'key':'gid'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

@app.route('/api/v1/months/category', methods=['GET'])
def get_months_category():
    """ return all expenses per category by month in group id (need to do error control)"""
    conn = None
    if not 'gid' in request.args:
        return jsonify({'code':400, 'name':'Bad Request', 'key':'gid'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT SUBSTR(cast(expenses.date AS text), 1, 6) AS month, cat.category, sum(expenses.amount)
            FROM expenses
            LEFT JOIN
                (SELECT id, CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category FROM categories) AS cat
            ON expenses.category = cat.id
            WHERE expenses.gid = '{}' AND expenses.deleted ='f'
            GROUP BY month, cat.category
            ORDER BY month""".format(request.args['gid']))
        ans = cur.fetchall()
        if (len(ans) == 0):
            return jsonify({'code':204, 'name':'No Content', 'key':'gid'})
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

# add category

# edit category

@app.route('/api/v1/stores', methods = ['GET'])
def get_stores():
    """ Get store(s) by dynamic search on store name, entity and city """
    conn = None
    if not 'words' and not 'id' in request.args:
        return jsonify({'code': 400, 'name': 'Bad Request', 'key': 'words or id'})
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        if 'id' in request.args:
            cur.execute("""SELECT id, name, city, entity FROM stores WHERE id='{}'""".format(request.args['id']))
        else:
            cur.execute("""
            SELECT id, name, city, entity
            FROM stores
            WHERE to_tsvector('english', coalesce(name,'') || ' ' || coalesce(city,'') || ' ' || coalesce(entity,'')) @@ to_tsquery('{}')
                AND stores.deleted = 'f'""".format(request.args['words'].strip().replace(' ', ' & ')))
        ans = cur.fetchall()
        ans1 = []
        for row in ans:
            ans1.append(dict(row))
        return jsonify(ans1)
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=False, host='0.0.0.0', port='5000', threaded=True)
    # Production
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
