from flask import Flask,request,render_template,redirect, jsonify,make_response
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import csv
import os
import dialogflow
import requests
import json
import pusher
import urllib
import logging


class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password),encrypted=False)
        self.session=self.driver.session(database="eventdb")
    def retour_Session(self):
        return self.session

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_event(self, title, date, heure, tarif, description, type1, lieu):
        with self.driver.session(database="eventdb") as session:
            # Write transactions allow the driver to handle retries and transient errors
            session.write_transaction(self._create_and_return_event, title, date, heure, tarif, description, type1, lieu)

    @staticmethod
    def _create_and_return_event(tx,title, date, heure, tarif, description, type1, lieu):
        tx.run ("CREATE (a:Event { title: $title, date: $date, heure: $heure, tarif: $tarif, description: $description, type: $type, lieu: $lieu })", title=title, date =date, heure=heure, tarif=tarif, description=description, type=type1, lieu =lieu)

    GOOGLE_APPLICATION_CREDENTIALS = "/Users/sirinekriaa/Desktop/coursiatic5/IATIC-5-PROJECT/bot-event-hwde-3d1d6fa8f360.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    @staticmethod
    def _list_intents(project_id):
        import dialogflow_v2 as dialogflow
        intents_client = dialogflow.IntentsClient()

        parent = intents_client.project_agent_path(project_id)

        intents = intents_client.list_intents(parent)

        for intent in intents:
            print('=' * 20)
            print('Intent name: {}'.format(intent.name))
            print('Intent display_name: {}'.format(intent.display_name))
            print('Action: {}\n'.format(intent.action))
            print('Root followup intent: {}'.format(
                intent.root_followup_intent_name))
            print('Parent followup intent: {}\n'.format(
                intent.parent_followup_intent_name))

            print('Input contexts:')
            for input_context_name in intent.input_context_names:
                print('\tName: {}'.format(input_context_name))

            print('Output contexts:')
            for output_context in intent.output_contexts:
                print('\tName: {}'.format(output_context.name))




app=Flask(__name__)

with open("cred.txt")as f1:
    data=csv.reader(f1,delimiter=",")
    for row in data:
        url=row[0]
        id=row[1]
        pwd=row[2]
    f1.close()



a = App(url,id,pwd)
x = a.retour_Session()
k= a._list_intents("bot-event-hwde")

# default route
@app.route('/')
def index():
    return 'Hello World'

# function for responses
def results():
    # build a request object
    ListOfReturnedMsg = []
    req = request.get_json(force=True)

    # fetch action from json
    #action = req.get('queryResult').get('action')
    for i in range(len(req.get('queryResult').get('fulfillmentMessages'))):
        returnMsg1 = req.get('queryResult').get('fulfillmentMessages')[i]
        ListOfReturnedMsg.append(returnMsg1)
    print('--------- sortie -----------')
    print(req.get('queryResult').get('queryText'))
    #self._create_event("event_test", "event_type_test", "event_description_test", "event_date_test", "event_heure_test", "event_lieu_test", "event_tarif_test")

        #bot-event-hwde

        # return a fulfillment response
    return {'fulfillmentText':ListOfReturnedMsg}

    # create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

@app.route("/listeOfevent")
def listeOfevent():
    query="""
    MATCH(a:Event)
    return a.title as title ,a.date as date, a.lieu as lieu
    """
    results=x.run(query)
    listeOfevent=[]
    for result in results:
        dc={}
        title=result["title"]
        date=result["date"]
        lieu=result["lieu"]
        dc.update({"Title":title,"Date":date, "Lieu":lieu})
        listeOfevent.append(dc)
    return jsonify ({
        'listeOfevent': listeOfevent
        })


@app.route('/create', methods=['GET'])
def create():
    title_test2 = request.args.get('title')
    date_test2= request.args.get('date')
    heure_test2= request.args.get('heure')
    tarif_test2= request.args.get('tarif')
    desc_test2= request.args.get('desc')
    genre_test2= request.args.get('genre')
    lieu_test2= request.args.get('lieu')
    a.create_event(title_test2, date_test2, heure_test2, tarif_test2, desc_test2, genre_test2, lieu_test2)
    return 'Done', 201

@app.route("/detailsOfOneEvent",methods=["GET","POST"])
def detailsOfOneEvent():
    title=request.form["title"]
    query="""
    MATCH(a:Event{title:$title})
    return a.title as title, a.date, a.heure, a.tarif, a.description, a.type, a.lieu
    """
    parameter={"title":title}
    results=x.run(query,parameter)
    detailsOfOneEvent=[]
    for result in results:
        ParamsEvents={}
        title=result["title"]
        lieu=result["lieu"]
        date=result["date"]
        heure=result["heure"]
        tarif=result["tarif"]
        description=result["description"]
        typeOf=result["type"]
        ParamsEvents.update({"Title":title,"Date":date, "Lieu":lieu,"Heure":heure, "Tarif":tarif, "Description":description,"Type":typeOf})
        detailsOfOneEvent.append(ParamsEvents)
    return jsonify ({
        'detailsOfOneEvent': detailsOfOneEvent
        })

if __name__=='__main__':
    app.run(port=5000, debug="False")
