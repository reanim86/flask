from flask import Flask, jsonify

app = Flask('app')


def hello_world():

    return jsonify({'hello': 'world'})


app.add_url_rule('/hello/', view_func=hello_world, methods=['GET'])


# if __name__ == '__mail__':
app.run()