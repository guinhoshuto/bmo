import utils
import os
import re

sheet = "workouts"

def handleHevyWorkout(log):
    lines = log.splitlines()
    workout_name = lines[0]
    date = lines[1]
    url = lines[len(lines) - 1]
    exercises = lines[2:len(lines)-2]
    for line in exercises:
        if(line.startswith('Série')): 
            print(workout_name, line)
            serie = handleSeries(line)
            print(serie)
            utils.appendRow(
                os.getenv("HEVY_SHEETS_ID"), 
                sheet, 
                [date, workout_name, exercise_name, serie["serie"], serie["reps"], serie["dur"], url]
            ) 
        if(line == ""):
            print('próximo exercicio')
        else:
            exercise_name = line


def handleSeries(serie):
    tmp = serie.split(":")
    dict = {}
    dict["dur"] = 0
    dict["reps"] = 0
    dict["serie"] = tmp[0].split(" ")[1]
    if("reps" in tmp[1]):
        dict["reps"] = extract_number(tmp[1])
    else: 
        dict["dur"] = minutesToSeconds(tmp[1])
    return dict    

def minutesToSeconds(dur):
    seconds = 0
    for t in dur.split(" "):
        if("min" in t):
            seconds += extract_number(t)*60
        if("s" in t):
            seconds += extract_number(t)
    return seconds
def extract_number(time):
    return int(re.findall(r'\d+', time)[0])