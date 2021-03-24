import socket
from flask import Flask, render_template, request, json, url_for, flash, redirect
from werkzeug.exceptions import abort
from waitress import serve
from flask_mysqldb import MySQL
import mysql.connector

# MySQL configurations
app = Flask(__name__)

app.config['MYSQL_HOST'] = '192.168.50.10'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'vg-toor'
app.config['MYSQL_DB'] = 'blog'

mysql = MySQL(app)
app.config['SECRET_KEY'] = 'your secret key'

def get_post(post_id):
    conn = mysql.connection.cursor()
    post = conn.execute('SELECT * FROM posts WHERE id = %s',
                        (post_id,))
    # post = 1
    post = conn.fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM posts')
    posts = conn.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/hello')
def hello():
    # return 'Hello, World!'
    internal_ip_output = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
        s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
        socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return render_template('hello.html', internal_ip=internal_ip_output)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = mysql.connection.cursor()
            conn.execute('INSERT INTO posts (title, content) VALUES (%s, %s)',
                         (title, content))
            mysql.connection.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = mysql.connection.cursor()
            conn.execute('UPDATE posts SET title = %s, content = %s'
                         ' WHERE id = %s',
                         (title, content, id))
            mysql.connection.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = mysql.connection.cursor()
    conn.execute('DELETE FROM posts WHERE id = %s', (id,))
    mysql.connection.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post[0]))
    return redirect(url_for('index'))


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == "POST":
        details = request.form
        title = details['title']
        content = details['content']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts(title, content) VALUES (%s, %s)", (title, content))
        mysql.connection.commit()
        cur.close()

        return 'success'
    return render_template('test.html')

if __name__ == "__main__":
   #app.run() ##Replaced with below code to run it using waitress
   #serve(app, host='0.0.0.0', port=5000) # there is a bug when run with sudo
   app.run(debug=True, port=5000) #run with python app.py
  # app.run(port=5000) #run with python app.py


