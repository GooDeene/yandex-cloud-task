import os
import ydb
from flask import Flask, request, jsonify
import uuid

UPSERT_DATA_QUERY = """
    UPSERT INTO comments (id, username, comment) VALUES (
        "{id}", "{username}", "{comment}");"""

SELECT_DATA_QUERY = "SELECT * FROM comments"

app = Flask(__name__)


@app.route('/get_back_data', methods=['GET'])
def get_back_ver():
    version = os.getenv('BACKEND_VERSION')
    hostname = os.getenv('HOSTNAME')

    return jsonify({'version': version, 'hostname': hostname})


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()
    username = data.get('username')
    comment = data.get('comment')

    with ydb.Driver(endpoint=os.environ['YDB_ENDPOINT'],
                    database=os.environ['YDB_DATABASE'],
                    credentials=ydb.iam.ServiceAccountCredentials.from_file('./key.json'),
                    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        session = driver.table_client.session().create()
        session.transaction().execute(
            UPSERT_DATA_QUERY.format(
                id=str(uuid.uuid4()),
                username=username,
                comment=comment,
            ),
            commit_tx=True
        )

    return jsonify({'message': 'Data added successfully'})


@app.route('/get_data', methods=['GET'])
def get_data():
    with ydb.Driver(endpoint=os.environ['YDB_ENDPOINT'],
                    database=os.environ['YDB_DATABASE'],
                    credentials=ydb.iam.ServiceAccountCredentials.from_file('./key.json'),
                    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        session = driver.table_client.session().create()
        results = session.transaction(ydb.SerializableReadWrite()).execute(SELECT_DATA_QUERY, commit_tx=True, )
    data = []

    for result in results[0].rows:
        data.append(
            {
                'id': result[1].decode("utf-8"),
                'username': result[2].decode("utf-8"),
                'comment': result[0].decode("utf-8")
            }
        )

    return jsonify(data)


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
