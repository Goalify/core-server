from flask import Flask, request, make_response, jsonify
from flask_mysqldb import MySQL
import yaml
import time
import datetime
import os


IP = '127.0.0.1'
PORT = 3001
app = Flask(__name__)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)


naming_dict_goals = {
    'user_id': 'user_id',
    'goal_id': 'id',
    'title': 'name',
    'description': 'description',
    'deadline': 'deadline',
    'created_on': 'dateCreated',
    'complete_status': 'state',
    'publish_status': 'published',
    'date_finished': 'dateFinished'
}

naming_dict_goals_rev = {val: key for key, val in naming_dict_goals.items()}

naming_dict_milestones = {
    'milestone_id': 'id',
    'goal_id': 'goal_id',
    'title': 'name',
    'complete_status': 'state',
}

naming_dict_milestones_rev = {val: key for key, val in naming_dict_milestones.items()}


def show_table(table_name):
    """
    a helper function to show a table given its name.
    :param table_name:
    :return: None.
    """
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(f'''SELECT * FROM {table_name};''')
        res = cur.fetchall()
        print(res)
        cur.close()


@app.route('/get-goals', methods=['POST'])
def get_goals():
    """
    a method used to fetch all goals for some user.
    :return: a list of goals.
    """
    if request.method == 'POST':
        user_id = request.form['user_id']
        command = f'''SELECT * FROM goals WHERE user_id = "{user_id}"'''
        cur = mysql.connection.cursor()
        try:
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        columns = [naming_dict_goals[col[0]] for col in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        for row in rows:
            command = f'''SELECT * FROM milestones WHERE goal_id = "{row['id']}"'''
            try:
                cur.execute(command)
                mysql.connection.commit()
            except:
                mysql.connection.rollback()
                return make_response("Server Error", 500)
            columns = [naming_dict_milestones[col[0]] for col in cur.description]
            milestones = [dict(zip(columns, row)) for row in cur.fetchall()]
            row['milestones'] = milestones
        rows = {'list': rows}
        return make_response(jsonify(rows), 200)


@app.route('/add-goal', methods=['POST'])
def add_goal():
    """
    a method to create a new goal for some user.
    :return: the new goal id or error code.
    """
    if request.method == 'POST':
        goal_details = request.form
        user_id = goal_details[naming_dict_goals['user_id']]
        publish_status = goal_details[naming_dict_goals['publish_status']]
        created_on = goal_details[naming_dict_goals['created_on']]
        title = goal_details[naming_dict_goals['title']]
        description = goal_details[naming_dict_goals['description']]
        complete_status = goal_details[naming_dict_goals['complete_status']]
        deadline = goal_details[naming_dict_goals['deadline']]
        date_finished = goal_details[naming_dict_goals['date_finished']]
        cur = mysql.connection.cursor()
        # command = '''INSERT INTO goals(user_id, publish_status, created_on, title, description, complete_status, deadline,
        #                                date_finished) VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''
        command = f'''INSERT INTO goals(user_id, publish_status, created_on, title, description, complete_status, 
        deadline, date_finished) VALUES ("{user_id}", "{publish_status}", "{created_on}", "{title}", "{description}", "{complete_status}", "{deadline}", "{date_finished}");'''
        try:
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        id = cur.lastrowid
        return make_response(jsonify({'id': id}), 200)


@app.route('/add-milestone', methods=['POST'])
def add_milestone():
    """
    a method responsible for adding a new milestone to some goal.
    :return: the new milestone id or error code.
    """
    if request.method == 'POST':
        print(request.form)
        milestone_details = request.form
        goal_id = milestone_details[naming_dict_milestones['goal_id']]
        title = milestone_details[naming_dict_milestones['title']]
        complete_status = milestone_details[naming_dict_milestones['complete_status']]
        cur = mysql.connection.cursor()
        # command = '''INSERT INTO milestones(goal_id, title, complete_status)
        #     VALUES (?, ?, ?);'''
        command = f'''INSERT INTO milestones(goal_id, title, complete_status) 
             VALUES ("{goal_id}", "{title}", "{complete_status}");'''
        try:
            # cur.execute(command, [goal_id, title, complete_status])
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        id = cur.lastrowid
        cur.close()
        return make_response(jsonify({'id': id}), 200)


@app.route('/remove-goal', methods=['POST'])
def remove_goal():
    """
    a method responsible for removing a goal and its milestones.
    :return: response http code.
    """
    if request.method == 'POST':
        print(request.form)
        goal_details = request.form
        goal_id = goal_details['id']
        cur = mysql.connection.cursor()
        # command = '''DELETE FROM goals where goal_id = ?'''
        command = f'''DELETE FROM goals where goal_id = "{goal_id}"'''
        try:
            cur.execute(command)
            # command = '''DELETE FROM milestones where goal_id = ?'''
            command = f'''DELETE FROM milestones where goal_id = "{goal_id}"'''
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        cur.close()
        return make_response("OK", 200)


@app.route('/remove-milestone', methods=['POST'])
def remove_milestone():
    """
    a method responsible for removing a milestone in some goal.
    :return: response http code.
    """
    if request.method == 'POST':
        print(request.form)
        milestone_details = request.form
        milestone_id = milestone_details['id']
        cur = mysql.connection.cursor()
        # command = '''DELETE FROM milestones where milestone_id = ?'''
        command = f'''DELETE FROM milestones where milestone_id = "{milestone_id}"'''
        try:
            # cur.execute(command, [milestone_id])
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        cur.close()
        return make_response("OK", 200)


@app.route('/edit-goal', methods=['POST'])
def edit_goal():
    """
    a method responsible for editing a goal.
    :return: response http code.
    """
    if request.method == 'POST':
        goal_details = request.form
        goal_id = goal_details[naming_dict_goals['goal_id']]
        user_id = goal_details[naming_dict_goals['user_id']]
        publish_status = goal_details[naming_dict_goals['publish_status']]
        created_on = goal_details[naming_dict_goals['created_on']]
        title = goal_details[naming_dict_goals['title']]
        description = goal_details[naming_dict_goals['description']]
        complete_status = goal_details[naming_dict_goals['complete_status']]
        deadline = goal_details[naming_dict_goals['deadline']]
        date_finished = goal_details[naming_dict_goals['date_finished']]
        cur = mysql.connection.cursor()
        # command = '''UPDATE goals SET publish_status = ?, created_on = ?, title = ?, description = ?,
        # complete_status = ?, deadline = ?, date_finished = ? WHERE goal_id = ?;'''
        command = f'''UPDATE goals SET publish_status = "{publish_status}", created_on = "{created_on}", title = "{title}", description = "{description}", 
                complete_status = "{complete_status}", deadline = "{deadline}", date_finished = "{date_finished}" WHERE goal_id = "{goal_id}";'''
        try:
            # cur.execute(command, [publish_status, created_on, title, description, complete_status, deadline, date_finished, goal_id])
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        cur.close()
        return make_response("OK", 200)


@app.route('/edit-milestone', methods=['POST'])
def edit_milestone():
    """
    a method responsible for editing a milestone.
    :return: response http code.
    """
    if request.method == 'POST':
        print(request.form)
        milestone_details = request.form
        milestone_id = milestone_details[naming_dict_milestones['milestone_id']]
        goal_id = milestone_details[naming_dict_milestones['goal_id']]
        title = milestone_details[naming_dict_milestones['title']]
        complete_status = milestone_details[naming_dict_milestones['complete_status']]
        cur = mysql.connection.cursor()
        # command = '''UPDATE milestones SET title = ?, complete_status = ? WHERE milestone_id = ?;'''
        command = f'''UPDATE milestones SET title = "{title}", complete_status = "{complete_status}" WHERE milestone_id = "{milestone_id}";'''
        try:
            # cur.execute(command, [title, complete_status, milestone_id])
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response("Server Error", 500)
        cur.close()
        return make_response("OK", 200)


@app.route('/discover', methods=['POST'])
def discover():
    """
    a method responsible for finding the last public goals.
    :return: the last public goals
    """
    if request.method == 'POST':
        num_rows = request.form.get('num_rows', 5)
        # command = '''SELECT * FROM goals LIMIT ?'''
        command = f'''SELECT * FROM goals LIMIT "{num_rows}"'''
        cur = mysql.connection.cursor()
        try:
            # cur.execute(command, [num_rows])
            cur.execute(command)
            mysql.connection.commit()
        except:
            mysql.connection.rollback()
            return make_response(400)
        res = cur.fetchall()
        cur.close()
        return make_response(jsonify(res), 200)


def init_db():
    """
    the main method for initializing the database.
    :return: None
    """
    with app.app_context():
        cur = mysql.connection.cursor()
        command = '''CREATE TABLE IF NOT EXISTS `goals` (
                          `goal_id` int PRIMARY KEY AUTO_INCREMENT,
                          `user_id` int,
                          `publish_status` varchar(255),
                          `created_on` varchar(63),
                          `title` varchar(255),
                          `description` varchar(1023),
                          `complete_status` varchar(255),
                          `deadline` varchar(63),
                          `date_finished` varchar(63));'''
        cur.execute(command)
        mysql.connection.commit()

        command = '''CREATE TABLE IF NOT EXISTS `milestones` (
                      `milestone_id` int PRIMARY KEY AUTO_INCREMENT,
                      `goal_id` int,
                      `complete_status` varchar(255),
                      `title` varchar(255));'''
        cur.execute(command)
        mysql.connection.commit()

        command = '''ALTER TABLE `milestones` ADD FOREIGN KEY (`goal_id`) REFERENCES `goals` (`goal_id`);'''
        cur.execute(command)
        mysql.connection.commit()
        cur.close()
    show_table("goals")
    show_table("milestones")


if __name__ == '__main__':
    init_db()
    app.run(host=IP, port=PORT)
