import utils
import os
sheet = "workouts"

async def handleHevyWorkout(log):
    lines = log.splitlines()
    workout_name = lines[0]
    date = lines[1]
    url = lines[len(lines) - 1]
    workouts = lines[2:len(lines)-2]
    print(workouts)
    for i in workouts:
        if(i.startswith('Série')): 
            print(workout, i)
            await utils.appendRow(os.getenv("HEVY_SHEETS_ID"), sheet, ["as", "b"]) 
        if(i == ""):
            print('próximo exercicio')
        else:
            workout = i




