from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, AdsTable

app = Flask('app')

def get_ads(ads_id: int, session: Session):
    ads = session.get(AdsTable, ads_id)
    return ads

class AdsView(MethodView):

    def get(self, ads_id):
        with Session() as session:
            ads = get_ads(ads_id, session)
            return jsonify({
                'id': ads.id,
                'head': ads.head,
                'description': ads.description,
                'creationdate': ads.creationdate,
                'user': ads.username
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            new_ads = AdsTable(**json_data)
            session.add(new_ads)
            session.commit()
            return jsonify({'id': new_ads.id})



app.add_url_rule('/ads/', view_func=AdsView.as_view('ads_new'), methods=['POST'])
app.add_url_rule('/ads/<int:ads_id>', view_func=AdsView.as_view('ads'), methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run()