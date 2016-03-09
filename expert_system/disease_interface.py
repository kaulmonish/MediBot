#!usr/bin/python
# Owner :Jaideep Kekre
# _author_ = Jaideep Kekre
# _info_   =  Disease interface

"""
This module populates the buckets from symptom_validity_table.
This module contains funtions to interact with diseases .

"""
import heapq

from disease import Disease
from disease_signatures import Disease_Signature
from symptom_validity_table import symptom_validity_table


CRITICAL = 20
IMPORTANT= 10
OPTIONAL = 5

"""
Critical symptom : 20 #Disease can't be characterized without this .
Important symptom: 10 #Important symptoms , common to multiple diseases.
Optional symptoms: 5  #Symptoms which the patient may not exhibit .


"""

class Buckets:
    def __init__(self):
        self.bucket  = dict()

        # for algo1
        self.symptom_score = dict()
        # for algo2
        self.symptom_critical_count = dict()
        #for algo3
        self.top_value_bucket_symptoms = dict()

        self.disease_score = dict()
        self.disease_fraction_done = dict()



        self.removed_questions_list = list()
        self.finished_diseases_list = list()
        # stores the symptom that is not True / False
        self.symptom_signature_needed = ['fever']

        self.diseases_object = Disease()
        self.disease_signature_object = Disease_Signature()

        self.populate_diseases()
        self.disease_top_score = dict(self.disease_score)


    """
    <------------------------PUBLIC METHODS TO BY CALLED BY OUTSIDE MODULES----------------->
    """

    def get_avg_fraction(self):
        for disease_name in self.bucket.keys():
            self.calculate_fraction(disease_name)
            number = 0
            fraction = float(0)
        for fractions in self.disease_fraction_done.values():
            number = number + 1
            fraction = fraction + fractions
        return fraction / float(number)




    """
    get_top_symptoms()
    returns a ordered list of symptom(s) with the highest score across all diseases
    for algo1
    """

    def get_popular_symptoms(self, number_of_symptoms=1):
        top_symptoms = heapq.nlargest(number_of_symptoms, self.symptom_score, key=self.symptom_score.get)
        return top_symptoms

    """
    get_top_critical_symptoms()
    returns a ordered list of symptom(s) with the highest critical count across all diseases
    for algo2
    """

    def get_top_critical_symptoms(self, number_of_symptoms=1):
        top_symptoms = heapq.nlargest(number_of_symptoms, self.symptom_critical_count,
                                      key=self.symptom_critical_count.get)
        return top_symptoms

    """
    get_buckets_top_symptom()

    returns a list of the top symptom in each  bucket
    for algo3
    """

    def get_buckets_top_symptom(self, number_of_symptoms=1):
        self.calculate_highest_symptom()
        # print self.top_value_bucket_symptoms
        list_symptom = top_symptoms = heapq.nlargest(number_of_symptoms, self.top_value_bucket_symptoms,
                                                     key=self.top_value_bucket_symptoms.get)
        return list_symptom


    '''
    remove_disease()
    removes disease and it's score from all dicts
    '''
    def remove_disease(self, name):
        if name in self.bucket.keys():
            diseases_dict = self.diseases_object.get_disease()
            for specific_disease_name in diseases_dict.keys():
                if name == specific_disease_name:
                    disease_dict = diseases_dict[specific_disease_name]
                    for symptom in disease_dict.keys():
                        if symptom in self.removed_questions_list:
                            pass
                        else:
                            self.remove_symptom_score(symptom, disease_dict)
                    self.bucket.pop(disease_dict['name'])
                    self.disease_score.pop(disease_dict['name'])

        pass

    """
    question_asked()
    removes symptom from all diseases in symptom_validity_table objects
    removes symptom from all scores
    re-calculates score for all disease buckets
    """

    def remove_question_asked(self, symptom):

        for table_disease_object in self.bucket.values():
            table_disease_object.set_score(symptom, 0)
            table_disease_object.set(symptom, False)
        if symptom in self.symptom_score.keys():
            self.symptom_score.pop(symptom)
        if symptom in self.top_value_bucket_symptoms.keys():
            self.top_value_bucket_symptoms.pop(symptom)
        if symptom in self.symptom_critical_count.keys():
            self.symptom_critical_count.pop(symptom)
        for disease_name in self.bucket.keys():
            self.calculate_current_score(disease_name)
        self.removed_questions_list.append(symptom)





    """
    <---------------------------------------INTERNAL METHODS-------------------------------->
    """

    def get_score_by_symptom(self, symptom):
        if symptom in self.removed_questions_list:
            return None
        elif symptom in self.symptom_score.keys():
            return self.symptom_score[symptom]
        else:
            return None

    def get_symptom_by_disease(self, symptom, disease):
        table = symptom_validity_table
        table = self.bucket[disease]
        return table.get(symptom)
    def get_score_by_disease(self, disease_name):
        if disease_name in self.bucket.keys():
            self.calculate_current_score(disease_name)
            return self.disease_score[disease_name]
        else:
            return None
        pass



    """
    calculate_highest_symptom()
    populates the top_value_bucket dict

    runs : get_highest_symptom
         : calculate_highest_symptom
    """

    def calculate_highest_symptom(self):
        for disease_name in self.bucket:
            symptom = self.get_highest_symptom(disease_name)
            #print symptom + "is highest"
            if symptom == None:
                pass
            else:

                score = self.bucket[disease_name].get_score(symptom)
                # print score
                self.update_top_value(symptom, score)

    '''
    updates the symptom top_value dict
    '''

    def update_top_value(self, symptom, score):
        if symptom in self.top_value_bucket_symptoms.keys():
            self.top_value_bucket_symptoms[symptom] = self.top_value_bucket_symptoms[symptom] + score
        else:
            self.top_value_bucket_symptoms[symptom] = score

    """
    get_highest_symptom()
    returns the highest symptom in a given disease
    """

    def get_highest_symptom(self, disease_name):
        diseases_name_dict = self.diseases_object.get_disease()
        disease_dict = diseases_name_dict[disease_name]
        name = None
        max = 0
        for symptom in disease_dict.keys():
            if symptom in self.removed_questions_list:
                pass
            elif symptom == 'name':
                pass
            else:
                score = disease_dict[symptom]
                if score > max:
                    max = score
                    name = symptom

        return name






    """
    calculate_current_score()
    calculates total score for the given disease
    """
    def calculate_current_score(self,disease_name):
        if disease_name in self.bucket.keys():
            list_disease_dict=self.diseases_object.get_disease()
            specific_disease_dict=list_disease_dict[disease_name]
            table_disease_object=self.bucket[disease_name]
            score=0
            for symptom in specific_disease_dict.keys():
                if symptom == 'name':
                    pass
                elif symptom in self.removed_questions_list:
                    pass
                else:
                    temp=table_disease_object.get_score(symptom)
                    score=score+temp
            self.disease_score[disease_name]=score

    """
    add_symptom_score()
    adds score across diseases by symptoms
    """
    def add_symptom_score(self,symptom,score):
        if symptom in self.symptom_score.keys():
            self.symptom_score[symptom]=self.symptom_score[symptom]+score
        else :
            self.symptom_score[symptom] = score

    """
    update_critical_count()
    increments the critical count of a critical symptom
    """
    def update_critical_count(self, symptom):
        if symptom in self.symptom_critical_count.keys():
            self.symptom_critical_count[symptom] = self.symptom_critical_count[symptom] + 1
        else:
            self.symptom_critical_count[symptom] = 1

    '''
    remove_symptom_score()
    removes symptom score from disease dict
    removes symptom count from critical_count_dict
    '''

    def remove_symptom_score(self,symptom,disease_dict):
        if disease_dict[symptom] == None : 
            print "symptom already asked , hence ignore"
        elif symptom == 'name':
            pass
        else:
            self.symptom_score[symptom]=self.symptom_score[symptom]-disease_dict[symptom]
            if disease_dict[symptom] == CRITICAL:
                self.symptom_critical_count[symptom] = self.symptom_critical_count[symptom] - 1

    """
    calculates the fractional completion of a disease

    """

    def calculate_fraction(self, disease_name):
        done = self.disease_top_score[disease_name] - self.disease_score[disease_name]
        todo = self.disease_top_score[disease_name]

        fractiondone = done / float(todo)
        self.disease_fraction_done[disease_name] = fractiondone









    """
    set_table():
    works on per symptom basis
    adds symptom score to total symptom score ie
    sets symptom to True in symptom validity table
    set symptom score in symptom validity table

    calls : add_symptom_score()
          : update_critical_count()
          : set_score()
          : set()

    called by
          : populate_diseases
    """

    def set_table(self, symptom, score, table_disease_object, disease_name, arg=True):
        table_disease_object.set_score(symptom, score)
        if symptom in self.symptom_signature_needed:
            table_disease_object.set(symptom, self.disease_signature_object.get_fever(disease_name))
        else:
            table_disease_object.set(symptom, arg)

        if table_disease_object.get_score(symptom) == CRITICAL:
            self.update_critical_count(symptom)
        self.add_symptom_score(symptom, score)

    """
    populate_diseases()
    poplulates diseases from db and sets in the symptom validity table
    also adds the sypmtom validity object to the bucket dict

    """
    def populate_diseases(self):
        
        diseases_dict=self.diseases_object.get_disease()
        for specific_disease_name in diseases_dict.keys():
            new_table_obj         = symptom_validity_table()
            specific_disease_dict = diseases_dict[specific_disease_name]
            for symptom in specific_disease_dict.keys():
                #print symptom
                if symptom == 'name':
                    print specific_disease_dict[symptom] + " : LOADED"

                else:
                    self.set_table(symptom, specific_disease_dict[symptom], new_table_obj, specific_disease_name)
            self.bucket[specific_disease_name]=new_table_obj
            self.calculate_current_score(specific_disease_dict['name'])

            


        





if __name__ == '__main__':
    bucketlist = Buckets()
    print "Contents of Bucket are :" + str((bucketlist.bucket))
    print bucketlist.get_symptom_by_disease('fever', 'hepA')
    print(bucketlist.symptom_score)
    #bucketlist.get_score_by_disease('dengue')

    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))
    print "*******************************"
    # bucketlist.question_asked('fever')
    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))

    # bucketlist.get_score_by_symptom('fever')
    # bucketlist.remove_disease('dengue')
    # bucketlist.remove_disease('dengue')
    #bucketlist.remove_disease('dengue')
    #bucketlist.get_score_by_disease('dengue')
    #bucketlist.get_score_by_disease('hepA')
    # print "Contents of Bucket are :" + str((bucketlist.bucket))
    # print(bucketlist.symptom_score)
    # print (bucketlist.disease_score)
    lista = bucketlist.get_top_critical_symptoms()
    listb = bucketlist.get_popular_symptoms()
    liste = bucketlist.get_buckets_top_symptom()
    print bucketlist.get_symptom_by_disease('fever', 'hepA')
    print listb
    print lista
    print liste

    # bucketlist.remove_disease('hepA')
    bucketlist.remove_question_asked('fever')
    print "*****************"
    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))
    print(bucketlist.get_avg_fraction())

    bucketlist.remove_question_asked('fatigue')
    print "*****************"
    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))
    print(bucketlist.get_avg_fraction())

    bucketlist.remove_question_asked('joint_pain')
    print "*****************"
    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))
    print(bucketlist.get_avg_fraction())

    bucketlist.remove_question_asked('body_pain')
    bucketlist.remove_question_asked('clay_coloured_bowels')
    bucketlist.remove_question_asked('yellow_eyes')
    bucketlist.remove_question_asked('pain_behind_eyes')
    bucketlist.remove_question_asked('body_pain_muscles')
    bucketlist.remove_question_asked('rash')
    print "*****************"
    print(bucketlist.get_score_by_disease('hepA'))
    print(bucketlist.get_score_by_disease('dengue'))
    print(bucketlist.get_avg_fraction())

    print "*****************"
    listc = bucketlist.get_top_critical_symptoms()
    listd = bucketlist.get_popular_symptoms()
    listf = bucketlist.get_buckets_top_symptom()
    print listd
    print listc
    print listf
    print bucketlist.disease_fraction_done

    # print bucketlist.symptom_critical_count
    # print bucketlist.symptom_score
