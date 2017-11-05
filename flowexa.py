#!/usr/bin/env python

"""
name: flowexa.py
autor: Florian Paul Hoberg <florian {at} hoberg.ch>
description: This inofficial Alexa Skill will provide your last activities for weightlifting,
             running, biking and swimming within the last 30 days. No API access is nessessary,
             usual login credentials will be enough. To get additional information like user 
             weight a patched FlowClient library for Python will be needed and can be obtained:
             https://github.com/florianpaulhoberg/flow-client/blob/patch-1/flow/client.py
note:        ATM this is only available in German.
"""

import datetime
from flow import FlowClient
from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

def sum_objects(object, sum_return=0.0):
    """ Generate sum of inputs from list entries if they are set """
    for float in object:
        if float is not None:
            sum_return = float + sum_return
    return sum_return

def get_workouts(username, password, weightlifting_duration=[], weightlifting_calories=[], running_duration=[], running_calories=[], running_distance=[], biking_duration=[], biking_calories=[], biking_distance=[], swimming_duration=[], swimming_calories=[], swimming_distance=[]):
    """ Get remote user and activities from Polar Flow service and group them """
    client = FlowClient()
    client.login(username, password)
    activity = client.activities()

    # Get global user information (will need patched FlowClient:
    # https://github.com/florianpaulhoberg/flow-client/blob/patch-1/flow/client.py )
    activity_count = len(activity)
    userweight = activity[0].weight()

    # Split activities and group them by kind of sport 
    for single_activity in activity:

        # Weightlifting = d1ce94078aec226be28f6c602e6803e1-2015-10-20_13_45_19
        if "d1ce94078aec226be28f6c602e6803e1-2015-10-20_13_45_19" in single_activity.iconUrl:
            weightlifting_duration.append(single_activity.duration)
            weightlifting_calories.append(single_activity.calories)

        # Treadmile = d039f159dd0b62dc0a1ca72d82af2f0b-2015-10-20_13_46_28
        # Running   = 808d0882e97375e68844ec6c5417ea33-2015-10-20_13_46_22 
        if "d039f159dd0b62dc0a1ca72d82af2f0b-2015-10-20_13_46_28" or "808d0882e97375e68844ec6c5417ea33-2015-10-20_13_46_22" in single_activity.iconUrl:
            running_duration.append(single_activity.duration)
            running_calories.append(single_activity.calories)
            running_distance.append(single_activity.distance)

        # Biking = 561a80f6d7eef7cc328aa07fe992af8e-2015-10-20_13_46_03
        if "561a80f6d7eef7cc328aa07fe992af8e-2015-10-20_13_46_03" in single_activity.iconUrl:
            biking_duration.append(single_activity.duration)
            biking_calories.append(single_activity.calories)
            biking_distance.append(single_activity.distance)

        # Swimming = f4197b0c1a4d65962b9e45226c77d4d5-2015-10-20_13_45_26
        if "f4197b0c1a4d65962b9e45226c77d4d5-2015-10-20_13_45_26" in single_activity.iconUrl:
            swimming_duration.append(single_activity.duration)
            swimming_calories.append(single_activity.calories)
            swimming_distance.append(single_activity.distance)
    return weightlifting_duration, weightlifting_calories, running_duration, running_calories, running_distance, biking_duration, biking_calories, biking_distance, swimming_duration, swimming_calories, swimming_distance, activity_count, userweight

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Du benoetigst fuer diesen Skill einen Polar Flow Account.'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    speech_text = 'Gehst du schon zum Sport? Viel Spass!'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('AMAZON.CacnelIntent')
def cancel():
    speech_text = 'Gehst du schon zum Sport? Viel Spass!'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('GetEventsIntent')
def main():
    """ Run the whole magic """
    # FlowLogin
    firstname ="YOUR-FRISTNAME"
    username = "YOUR-FLOW-EMAIL"
    password = "YOUR-PASSWORD"

    # Get global user information and workouts/activities
    weightlifting_duration, weightlifting_calories, running_duration, running_calories, running_distance, biking_duration, biking_calories, biking_distance, swimming_duration, swimming_calories, swimming_distance, activity_count, userweight = get_workouts(username, password)

    # Generate metrics for all groups
    weightlifting_duration_overall = sum_objects(weightlifting_duration)
    weightlifting_calories_overall = sum_objects(weightlifting_calories)

    running_duration_overall = sum_objects(running_duration)
    running_calories_overall = sum_objects(running_calories)
    running_distance_overall = sum_objects(running_distance)

    biking_duration_overall = sum_objects(biking_duration)
    biking_calories_overall = sum_objects(biking_calories)
    biking_distance_overall = sum_objects(biking_distance)

    swimming_duration_overall = sum_objects(swimming_duration)
    swimming_calories_overall = sum_objects(swimming_calories)
    swimming_distance_overall = sum_objects(swimming_distance)

    overall_time_min = (weightlifting_duration_overall + running_duration_overall + biking_duration_overall + swimming_duration_overall) / 1000 / 60
    overall_time_hours = int(overall_time_min) * 0.0166667
    overall_time_hours = int(overall_time_hours)
    overall_calories = weightlifting_calories_overall + running_calories_overall + biking_calories_overall + swimming_calories_overall

    # Rehashing output information for speech output
    skill_output_info = "Gratulation " + firstname + " ! Du hast in den letzten 30 Tagen " + str(activity_count) + " Trainingseinheiten in insgesamt " + str(overall_time_hours) + " Stunden absolviert "
    skill_output_weight = " Dein aktuelles Gewicht betraegt " + str(userweight) + " Kilogramm dabei hast du insgesamt " + str(int(overall_calories)) + " Kalorien verbrannt!"
    skill_output_weightlifting = "Beim Kraftsport bist du " + str(len(weightlifting_duration)) + " mal gewesen! "
    skill_output_running = " Laufen " + str(int(running_distance_overall)/1000) + " Kilometer! "
    skill_output_biking = " Radfahren " + str(int(biking_distance_overall)/1000) + " Kilometer! "
    skill_output_schwimming = " Schwimmen " + str(int(swimming_distance_overall)/1000) + " Kilometer! "
    skill_output_overall = skill_output_info + skill_output_weight + skill_output_weightlifting + skill_output_running + skill_output_biking + skill_output_schwimming 

    # Speech output for your Echo via Skill 
    speech_text = "<speak>\n"
    speech_text += str(skill_output_overall)
    speech_text += "</speak>"
    return statement(speech_text)

main()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
