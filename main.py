from bottle import route, run, template, static_file, request
import random
import json
import pymysql


@route("/", method="GET")
def index():
    return template("adventure.html")


@route("/start", method="POST")
def start():
    username = request.POST.get("name")
    current_adv_id = request.POST.get("adventure_id")


    user_id = 0 #todo check if exists and if not create it
    print('Hello ')
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='adventure',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE name = '{}'".format(username)
        cursor.execute(sql)
        result = cursor.fetchall()
        #if user already exists get his info

        if len(result) > 0:
            current_adv_id = 1
            print("The user is already existing")
            user = result[0]
            id = user['id']
            name = user['name']
            questionId = user['last_current_question']

            sql = "SELECT * FROM questions WHERE id=(SELECT last_current_question FROM users WHERE id = '{}')".format(id)
            cursor.execute(sql)
            result1 = cursor.fetchall()
            # print(result1[0])
            # print(result1[0]['image'])
            # print(user['id'])
            # print(questionId)


            sql_options = "SELECT `target_question` AS `id`,`opt_text` AS `option_text` FROM options WHERE question_id=(SELECT last_current_question FROM users WHERE id = '{}')".format(id)
            cursor.execute(sql_options)
            result2 = cursor.fetchall()
            #print(result2['opt_text'])

            # [x['opt_text'] for x in result2]

            next_steps_results = result2
            print(user['id'])
            return json.dumps({"user": id,
                               "adventure": current_adv_id,
                               "current": questionId ,
                               "text": result1[0]['question'],
                               "image": result1[0]['image'],
                               "options": next_steps_results
                               })
            # print("The format of info you are sending is not good")


        #if user is new create user data
        else:
            print("you")

            current_adv_id = 1
            current_question_id = 1
            
            sql = "INSERT INTO users (name, last_current_question) VALUES (%s, %s)"
            cursor.execute(sql, (username, current_question_id))
            connection.commit()


            sql2 = "SELECT id FROM users WHERE name = '{}'".format(username)
            cursor.execute(sql2)
            print('Your are killing my brain')
            user_id = cursor.fetchone()



            sql3 = "SELECT id FROM questions WHERE id = '{}'".format(current_question_id)
            cursor.execute(sql3)
            current_story_id = cursor.fetchone()


            sql4 = "SELECT opt_text FROM options o LEFT JOIN questions q on o.question_id = q.id join users u on q.id=u.last_current_question and u.id='{}'".format(current_question_id)
            cursor.execute(sql4)
            option_text= cursor.fetchall()


            sql5 = "SELECT image FROM questions WHERE id=(SELECT last_current_question FROM users WHERE id = '{}')".format(current_question_id)
            cursor.execute(sql5)
            picture = cursor.fetchall()


            sql6 = "SELECT target_question FROM options WHERE question_id =(SELECT last_current_question FROM users WHERE id = '{}')".format(current_question_id)
            cursor.execute(sql6)
            next_steps_results = cursor.fetchall()
            print(option_text[0][0])
            return json.dumps({"user": user_id['id'],
                               "adventure": current_adv_id,
                               "current": current_story_id['id'],
                               "text": option_text,
                               "image": picture,
                               "options": next_steps_results
                               })



    # current_story_id = 0 #todo change
    # next_steps_results = [
    #     {"id": 1, "option_text": "I fight it"},
    #     {"id": 2, "option_text": "I give him 10 coins"},
    #     {"id": 3, "option_text": "I tell it that I just want to go home"},
    #     {"id": 4, "option_text": "I run away quickly"}
    #     ]

    #todo add the next step based on db

    connection.close



@route("/story", method="POST")
def story():
    user_id = request.POST.get("user")
    current_adv_id = request.POST.get("adventure")
    next_story_id = request.POST.get("next") #this is what the user chose - use it!



    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='adventure',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        opt1 = "SELECT target_question as `id` , opt_text as option_text FROM options WHERE question_id = (select last_current_question FROM users WHERE id ='{}'".format(user_id)
        cursor.execute(opt1)
        result = cursor.fetchall()
        print(json.dumps(result))

        next_steps_results =result
        print('hello')

        # next_steps_results = [
        #     {"id": 1, "option_text": result},
        #     {"id": 2, "option_text": "I hide!"},
        #     {"id": 3, "option_text": "I sleep!"},
        #     {"id": 4, "option_text": "I fight!"}
        # ]
        # random.shuffle(next_steps_results)  # todo change - used only for demonstration purpouses

    #todo add the next step based on db
    return json.dumps({"user": user_id,
                       "adventure": current_adv_id,
                       "text": "New scenario! What would you do?",
                       "image": "choice.jpg",
                       "options": next_steps_results
                       })




@route('/js/<filename:re:.*\.js$>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')

def main():
    run(host='localhost', port=9000)

if __name__ == '__main__':
    main()

