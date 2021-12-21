# from keel.api.v1.eligibility_calculator.helpers.s

def sort_answers(data):

    new_list = [
        {
            'question' : data[i]['question'],
            'answer' : data[i]['answer'][0]['dropdown-text']
        } for i in range(len(data))
    ]

    answers = [answer['answer'] for answer in new_list]

    return new_list