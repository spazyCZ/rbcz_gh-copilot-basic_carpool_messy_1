from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'badsecret'  # bad practice

PARKING_FILE = 'parking_data.json'

def getd():
    try:
        with open(PARKING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def saved(d):
    with open(PARKING_FILE, 'w') as f:
        json.dump(d, f)

def check_login():
    return session.get('u') == 'admin'

@app.route('/', methods=['GET', 'POST'])
def h():
    if request.method == 'POST':
        if request.form.get('u') == 'admin' and request.form.get('p') == 'admin':
            session['u'] = 'admin'
            return redirect(url_for('h'))
    if not check_login():
        return '''<form method="post">User: <input name="u"> Pass: <input name="p" type="password"><input type="submit"></form>'''
    d = getd()
    html = '<h1>Parking</h1><a href="/logout">Logout</a><ul>'
    for k in d:
        html += f'<li>{k}: {d[k].get("name", "?")} <a href="/del/{k}">del</a> <a href="/edit/{k}">edit</a></li>'
    html += '</ul><a href="/add">Add</a>'
    return html

@app.route('/logout')
def logout():
    session.pop('u', None)
    return redirect(url_for('h'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not check_login(): return redirect(url_for('h'))
    if request.method == 'POST':
        d = getd()
        pl = request.form.get('pl')
        nm = request.form.get('nm')
        if pl in d:
            return 'Already reserved! <a href="/">back</a>'
        d[pl] = {'name': nm}
        saved(d)
        return redirect(url_for('h'))
    return '''<form method="post">Place: <input name="pl"> Name: <input name="nm"><input type="submit"></form>'''

@app.route('/edit/<pl>', methods=['GET', 'POST'])
def edit(pl):
    if not check_login(): return redirect(url_for('h'))
    d = getd()
    if pl not in d:
        return 'Not found! <a href="/">back</a>'
    if request.method == 'POST':
        nm = request.form.get('nm')
        d[pl]['name'] = nm
        saved(d)
        return redirect(url_for('h'))
    return f'''<form method="post">Place: {pl} Name: <input name="nm" value="{d[pl]['name']}"><input type="submit"></form>'''

@app.route('/del/<pl>')
def delete(pl):
    if not check_login(): return redirect(url_for('h'))
    d = getd()
    if pl in d:
        del d[pl]
        saved(d)
    return redirect(url_for('h'))

# API endpoints (still messy)
@app.route('/list', methods=['GET'])
def l():
    return jsonify(getd())

@app.route('/create', methods=['POST'])
def c():
    d = getd()
    r = request.json
    if r['place'] in d:
        return jsonify({'error': 'Place already reserved'}), 400
    d[r['place']] = r
    saved(d)
    return jsonify({'message': 'Reservation created'})

@app.route('/update', methods=['PUT'])
def u():
    d = getd()
    r = request.json
    if r['place'] not in d:
        return jsonify({'error': 'Reservation not found'}), 404
    d[r['place']] = r
    saved(d)
    return jsonify({'message': 'Reservation updated'})

@app.route('/delete', methods=['DELETE'])
def dlt():
    d = getd()
    pl = request.json['place']
    if pl not in d:
        return jsonify({'error': 'Reservation not found'}), 404
    del d[pl]
    saved(d)
    return jsonify({'message': 'Reservation deleted'})

if __name__ == '__main__':
    app.run(debug=True,  port=5010)  # specify port explicitly
