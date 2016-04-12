#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
#from os import time
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://yd2349:why?@w4111vm.eastus.cloudapp.azure.com/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
'''
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  #return render_template("index.html", **context)
  return render_template("Home.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/Change_gpa',methods=['GET', 'POST'])
def Change_gpa():
  if request.method == 'POST':
    gpa = request.form['gpa']
    student = request.form['Student_name']
    gpa = float(gpa)
    
    g.conn.execute("UPDATE student set gpa = %.2f where sname = '%s'" %(gpa,student))
    return redirect('/Change_gpa')
  else:
      cursor = g.conn.execute(""" select s2.sid, s2.sname,s2.gpa,s1.course_name from student_course s1, prof_course p1, professor p2, student s2
        where p1.course_name = s1.course_name and p2.pid = p1.pid and s1.sid = s2.sid and p2.prof_name = '%s'
        """%prof_name)
      sid = []
      prof_student = []
      gpa = []
      course = []
      for cur in cursor:
        sid.append(str(cur[0]))
        prof_student.append(str(cur[1]))
        gpa.append(str(cur[2]))
        course.append(str(cur[3]))

      context = {}
      context['data'] ='Dear %s'%prof_name
      context['sid'] = sid
      context['student'] = prof_student
      context['gpa'] = gpa
      context['course'] = course
      return render_template("change_gpa.html", **context)

@app.route('/Add_new_course',methods=['GET', 'POST'])
def add_new_course():
  if request.method == 'POST':
    course = request.form['coursename']
    g.conn.execute("INSERT into course(course_name) values ('%s')"%course)
    g.conn.execute("INSERT INTO prof_course(pid,course_name) values ('%s','%s')" %('p1',course))
    return redirect('/Add_new_course')
  else:
    context = {} 
    context['data'] ='Dear %s'%prof_name
    cursor = g.conn.execute("""select p1.course_name, p1.pid from prof_course p1, professor p2
      where p1.pid = p2.pid and p2.prof_name = '%s'"""%prof_name)
    course = []
    for cur in cursor:
      course.append(cur[0])
      pid = cur[1]
      
    context['pid'] = pid
    context['course'] = course
    return render_template("add_new_course.html", **context)


@app.route('/Update_new_TA',methods=['GET', 'POST'])
def update_new_ta():
  global ta_name
  cursor = g.conn.execute("select count(*) from ta")
  for cur in cursor:
    number = int(cur[0])+1

  if request.method == 'GET':
    context = {}
    context['data'] = 'Dear %s'%prof_name
    cursor = g.conn.execute("""select t2.tname,t2.tid from professor p1, ta_worksfor_prof t1, ta t2 
      where t1.pid = p1.pid and t1.tid = t2.tid and p1.prof_name = '%s'"""%prof_name)
    tid = []
    ta_name = []
    for cur in cursor:
      ta_name.append(str(cur[0]))
      tid.append(str(cur[1]))
    context['ta_name'] = ta_name
    context['tid'] = tid
    #end_title = 'End'
    context['End'] = title1
    return render_template("update_new_ta.html",**context)
  else:
    global title1
    taname = request.form['taname']
    action = request.form['action']
    if action == "Add":
      if taname in ta_name:
        print title1
        title1 = "The name has already been in the TA list"
        
      else:
        new_tid = 't%d'%number
        g.conn.execute("INSERT into ta(tid,tname) values ('%s','%s')"%(new_tid,taname))
        g.conn.execute("INSERT into ta_worksfor_prof(pid,tid) values ('%s','%s')" %('p1',new_tid))

        title1 = 'Successfully added'
    
    elif action == "Delete":
      if taname not in ta_name:
        title1 = "The name is not in the TA list"
      else:
        cursor = g.conn.execute("select tid from ta where tname = '%s'"%taname)
        for cur in cursor:
          delete_tid = cur[0]
        g.conn.execute("DELETE from ta_worksfor_prof where tid = '%s'"%delete_tid)
        g.conn.execute("DELETE from ta where tname = '%s'"%taname)
        
        title1 = 'Successfully Deleted'
      
    elif action == "Change":
      if taname not in ta_name:
        title1 = "The name is not in the TA list"
      else:
        ta_new_name = request.form['tanewname']
        g.conn.execute("update ta set tname = '%s' where tname = '%s'"%(ta_new_name,taname))
        title1 = "Successfully Changed"

    return redirect('/Update_new_TA')




@app.route('/professor')
def get():
  context = dict(data = "Welcome ...Professors you can look up all the information and update grades and arrange courses")
  #context = "Welcome ...Professors you can look up all the information and update grades and arrange courses"
  return render_template('Professor.html',**context)


# Example of adding new data to the database
@app.route('/prof_login', methods=['POST'])
def Login():
  global prof_name, title1
  title1 = "End"
  
  username = request.form['username']
  pwd = request.form['password']
  print username, pwd
  cursor = g.conn.execute("SELECT * FROM profe_login")
  for result in cursor:
    user, pwd_db = result
    #print user,pwd
    pwd = 'Brian, C.'
    if username in user and pwd in pwd_db:
      print True
      prof_name = username
      return redirect('/prof_update')
  print False
  context = dict(data = "Sorry Professor! Error, the password is wrong! or No such kind of user!")
  return render_template('Professor.html', **context)
  #g.conn.execute("INSERT INTO test(name) values ('%s')" %(name))

@app.route('/prof_update')
def prof_update():
  print prof_name,title1
  cursor = g.conn.execute("""select * from prof_course p1,professor p2 
    where p1.pid = p2.pid and p2.prof_name = '%s'"""%prof_name)
  for cur in cursor:
    pid = cur[0].rstrip(' ')
    coursename = cur[1]
    position = cur[4]
    oh = cur[5]

  cursor = g.conn.execute("""select t2.tname from professor p1, ta_worksfor_prof t1, ta t2 
    where t1.pid = p1.pid and t1.tid = t2.tid and p1.prof_name = '%s'"""%prof_name)
  ta_name = []
  for cur in cursor:
    ta_name.append(str(cur[0]))


  cursor = g.conn.execute(""" select s2.sname from student_course s1, prof_course p1, professor p2, student s2
    where p1.course_name = s1.course_name and p2.pid = p1.pid and s1.sid = s2.sid and p2.prof_name = '%s'
    """%prof_name)
  student_name = []
  for cur in cursor:
    student_name.append(str(cur[0]))

  cursor = g.conn.execute("""select s.dept_name,s.school_name 
    from professor p1, prof_works_dept p2, school_house_department s
    where p1.pid = p2.pid and p2.dept_name = s.dept_name and p1.prof_name ='%s'"""%prof_name)
  for cur in cursor:
    dept, school = cur

  context = {'data':'1:3333'}
  context1 = {'data': 'Dear %s'%prof_name, 'pid': pid, 'course': coursename, 'position':position, 'oh':oh}
  context1['ta_name'] = ta_name
  context1['student'] = student_name
  context1['dept'] = dept
  context1['school'] = school
  return render_template('professor_update.html', ** context1)

@app.route('/student')
def student():
  context = dict(data = "Welcome ...Students you can look up all the related information")
  return render_template('student.html', **context)

@app.route('/stud_login', methods = ['POST'])
def stud_login():
  global stud_name
  username = request.form['username']
  pwd = request.form['password']
  pwd = 'Jacobs, T.'
  cursor = g.conn.execute("select * from stu_login")
  for cur in cursor:
    if username in cur[0] and pwd in cur[1]:
      print True
      stud_name = username
      return redirect('/stu_update')
  print False
  context = dict(data = '"Sorry Studnets! Error! the password is wrong! or No such kind of user!" ')
  return redirect('student.html', **context)


@app.route('/stu_update')
def stu_update():
  context = {}
  context['data'] = 'Dear %s'%stud_name
  cursor = g.conn.execute("select * from student where student.sname = '%s'" %stud_name)
  for cur in cursor:
    sid = cur[0]
    gpa = cur[2]
    age = cur[3]
  context['sid'] = sid
  context['gpa'] = gpa
  context['age'] = age
  return redirect('student_update.html', **context)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """
    debug = True
    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  #app.debug = True
  run()
  #app.run()
