# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 10:54:48 2023

@author: DILab
"""

import neointerface
from neo4j import GraphDatabase
from py2neo import Graph
import pandas as pd
import time
import mysql.connector
import pandas as pd
from gensim.models import KeyedVectors
from IPython.display import YouTubeVideo
from tabulate import tabulate
import scipy.io
import csv
import pymysql

pd.set_option('display.max_colwidth', None)

###################
## 1. connection ##
###################

class SESE:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, mariadb_user, mariadb_password, mariadb_host, mariadb_database):

        self.neo = neointerface.NeoInterface(host=neo4j_uri , credentials=(neo4j_user, neo4j_password))        
        self.graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        sql = mysql.connector.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host)
        sqlcnx = sql.cursor()
        sqlcnx.execute("CREATE DATABASE IF NOT EXISTS {}".format(mariadb_database))    
        
        self.cnx = mysql.connector.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
        
        q = "CALL dbms.components() YIELD name, versions"
        session = self.driver.session()
        result = session.run(q)
        
        print("-- Successfully connected! --")
        print("connection neo4j, mariadb user name : {}, {}".format(neo4j_user, mariadb_user))
        print("current neo4j version ", result.data()[0]['versions'][0])
        
                
    def close(self):
        self.neo.close()

    ###############
    ## 2. create ##
    ###############
    
    def add_object(self, df):
        
        start_time = time.time()
        result = self.neo.load_df(df, label = 'object')
        end_time = time.time()

        print("total time elapsed: ", end_time-start_time)
        print( )
        print(f"Load the {df.shape[0]} objects successfully.")
    
    def add_spo(self, df):

        session = self.driver.session()
        
        def add_sub_spo(self, video_id, subject, object, predicate, properties):
            cypher_rel_props, cypher_dict = self.neo.dict_to_cypher(properties)
            cypher_rel_props = cypher_rel_props.replace('`', '')
            cypher_dict = {**cypher_dict}

            q = f"""
                MATCH (s:object), (o:object) 
                WHERE s.video_id='{video_id}' and o.video_id='{video_id}' and s.object = '{subject}' and o.object = '{object}'
                CREATE (s)-[r:`{predicate}`  {cypher_rel_props}]->(o)
                RETURN s.video_id as video_id, s.video_path as video_path, properties(r).begin_frame as begin_frame, properties(r).end_frame as end_frame, properties(r).captions as captions, s.object as subject, type(r) as predicate, o.object as object;
                """
                
            result = session.run(q, cypher_dict)
            return result.data()

        start_time = time.time()
        for i, row in df.iterrows():
            prop = row[['video_id', 'video_path', 'begin_frame', 'end_frame', 'captions']].to_dict()
            add_sub_spo(self, video_id = row['video_id'], subject = row['subject'], object = row['object'], predicate = row['predicate'], properties = prop )
        end_time = time.time()
        
        print("total time elapsed: ", end_time-start_time)
        print( )
        print(f"Load the {df.shape[0]} spos successfully.")
        
    def add_table(self, mariadb_database, csv_file):
        cursor = self.cnx.cursor()
        
        cursor.execute('DROP TABLE IF EXISTS activitynet')

        cursor.execute('''
        CREATE TABLE `activitynet` (
        	`video_id` VARCHAR(20) NOT NULL COLLATE 'utf8mb4_general_ci',
        	`video_path` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_general_ci',
        	`begin_frame` DECIMAL(20,6) NULL,
        	`end_frame` DECIMAL(20,6) NOT NULL,
        	`captions` MEDIUMTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
        	`subject` VARCHAR(20) NULL COLLATE 'utf8mb4_general_ci',
        	`predicate` VARCHAR(20) NULL COLLATE 'utf8mb4_general_ci',
        	`object` VARCHAR(20) NULL COLLATE 'utf8mb4_general_ci'
        )

        COLLATE='utf8mb4_general_ci'
        ENGINE=InnoDB
        ''')

        cursor.execute('''
        LOAD DATA LOCAL INFILE '{}' 
        REPLACE INTO TABLE `{}`.`activitynet` 
        CHARACTER SET euckr 
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"' 
        ESCAPED BY '"' 
        LINES TERMINATED BY '\r\n' 
        IGNORE 1 LINES 
        (`video_id`, `video_path`, @ColVar2, @ColVar3, `captions`, `subject`, `predicate`, `object`) 
        SET `begin_frame` = REPLACE(REPLACE(@ColVar2, ',', ''), '.', '.'), 
        `end_frame` = REPLACE(REPLACE(@ColVar3, ',', ''), '.', '.')
        '''.format(csv_file, mariadb_database))
        
        print("MariaDB Load Successfully!")
        
    def add_db(self, mariadb_database, csv_file):
            
        self.add_table(mariadb_database, csv_file)
            
        df = pd.read_csv(csv_file, encoding='cp949')
            
        df_sub = df[['subject', 'video_id']]
        df_sub.columns = ['object', 'video_id']
    
        df_pre = df[['predicate', 'video_id']]
        df_pre.columns = ['object', 'video_id']
    
        df_obj = df[['object', 'video_id']]
        df_obj.columns = ['object', 'video_id']
    
        obj_df = pd.concat([df_sub, df_pre, df_obj], axis=0)
            
        self.add_object(obj_df)
        self.add_spo(df) 
       
    ################
    ##  3. search ##
    ################
    
    ## rdb using part    
        
    def get_keyword(self):
        quote = []
        quote = list(map(str, input("Enter the keyword you want to search for. Separate multiple entries with a comma(,). : ").split(',')))
        query = self.make_quotes(quote)
        start = time.time()
        cursor = self.cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns = ['video', 'starts', 'ends', 'captions'])
        df["count"] = self.count(quote, df)
        df = df.sort_values(by=["count"], ascending=False)
        df = df.reset_index(drop=True)
        print("Search Keywords : {}".format(quote))
        
        try:
            # Keyword Expansion
            if len(df) == 0:
                keywords = self.w2v(quote)
                query2 = self.make_quotes_w2v(keywords)
                cursor.execute(query2)
                result2 = cursor.fetchall()
                df = pd.DataFrame(result2, columns = ['video', 'starts', 'ends', 'captions'])
                df["count"] = self.count(quote, df)
                df = df.sort_values(by=["count"], ascending=False)
                df = df.reset_index(drop=True)
                print("There are no scenes searched by the keyword you entered.")
                print("We will proceed with the search including similar words.")
                print("Search & Extension Keywords : {}".format(keywords))
        except:
           df = ""
           print("We can't found the appropriate keyword for your search.")
                
        end = time.time()        
        print(f"The time required : {end - start:.5f} sec")
        print("Number of result values : ", len(df))
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

        if len(df) !=0:            
            video = self.embed_video(df["video"].loc[0])   
        else:
            video = "No appropriate scene found."

        return video

    def make_quotes(self, ls):
        quote = "SELECT video_path, begin_frame, end_frame, captions FROM activitynet WHERE captions LIKE '%{}%'".format(ls[0])
        if len(ls) > 1:
            for idx, word in enumerate(ls):
                if idx > 0:
                    special_token = " OR captions LIKE '%{}%'".format(ls[idx])
                    quote += special_token
        return quote

    def make_quotes_w2v(self, ls):
        quote = "SELECT video_path, begin_frame, end_frame, captions FROM activitynet WHERE (captions LIKE '%{}%'".format(ls[0])
        if len(ls)>1:
            for idx, word in enumerate(ls):
                if idx > 0:
                    if idx %2 != 0:
                        special_token = " OR captions LIKE '%{}%')".format(ls[idx])
                    if idx %2 == 0 :
                        special_token = " AND (captions LIKE '%{}%'".format(ls[idx])
                    quote += special_token
        return quote
        
    def w2v(self, query):
        n = 1
        result = []
        model = KeyedVectors.load_word2vec_format("activity_w2v")
            
        for word in query:
            similar = []
            result.append(word)
            similar.append(model.most_similar(word))
            for j in similar:
                for num in range(n):
                    result.append(j[num][0])
        return result
        
    def embed_video(self, url):
        embed_url = url
        embed_id = embed_url[32:]
        video = YouTubeVideo(embed_id, width=400)
        return video    

    def count(self, ls, df):
        num = 0
        for word in ls:
            if word != "":
                num += df["captions"].str.count(word)
            else:
                num += 0
        return num

    ## graphdb using part
    def get_description(self):
        
        ## first: count of nodes and relationships in DB ##
        query = f"""
            MATCH (n)
            RETURN count(n) as node_count
            """
        session = self.driver.session()
        result = session.run(query)
        result = result.data()
        df_result1 = pd.DataFrame(result)
    
        query = f"""
            MATCH ()-->() RETURN count(*) as relationship_count; 
            """
        session = self.driver.session()
        result = session.run(query)
        result = result.data()
        df_result2 = pd.DataFrame(result)
        out1 = pd.concat([df_result1, df_result2], axis=1)

        ## second: information in DB ##
        ## What kind of nodes exist
        ## Sample some nodes, reporting on property and relationship counts per node.
        query = f"""
            MATCH (n) WHERE rand() <= 0.1
            RETURN
            DISTINCT labels(n) as node_label,
            count(*) AS SampleSize,
            avg(size(keys(n))) as Avg_PropertyCount,
            min(size(keys(n))) as Min_PropertyCount,
            max(size(keys(n))) as Max_PropertyCount,
            avg(size( (n)-[]-() ) ) as Avg_RelationshipCount,
            min(size( (n)-[]-() ) ) as Min_RelationshipCount,
            max(size( (n)-[]-() ) ) as Max_RelationshipCount
            """
        session = self.driver.session()
        result = session.run(query)
        result = result.data()
        out2 = pd.DataFrame(result)
        
        print('----node and relation count----')
        print(out1)
        print('\n')
        print('----Information for property and relationship----')
        print(out2)
        return out1, out2
                
    def get_object_list(self):
                
        query = f"""
            MATCH (n:object)
            RETURN distinct n.object as object;
            """
        session = self.driver.session()
        result = session.run(query)
        df_result = pd.DataFrame(result)
        result = list(df_result[0])
        result = list(set(result))
        return result

    def get_object(self, object = False):

        q_match = f"MATCH (n) "
        
        q_with = f"WITH *"
           
        if object:
            obj = object.split(',')
            for i, ob in enumerate(obj):
                ob = ob.replace(' ', '')
                if i == 0:
                    q_obj = f"n.object = '{ob}'"
                else:
                    q_obj = q_obj + f" or n.object = '{ob}' "
            q_obj = "(" + q_obj +")"

        else:
            q_obj = ''

        if object:
            q_where = f"WHERE "+ q_obj + '\n'
        else:
            q_where = '\n'

        q_return = f"RETURN n.object as object, n.video_id as video_id, n.object_id as object_id;"

        query = q_match + '\n'+ q_with + '\n'+ q_where + '\n' + q_return
        start_time = time.time()
        
        session = self.driver.session()                    
        result = session.run(query)
        
        end_time = time.time()
        out = result.data()
        df_result = pd.DataFrame(out)   

        print("total time elapsed: ", end_time-start_time)
        return df_result

    def get_predicate_list(self):
        """
        A function that outputs a unique list of predicates stored in the database.
        """
        query = f"""
            CALL db.relationshipTypes()
            """
        session = self.driver.session()
        result = session.run(query)
        df_result = pd.DataFrame(result)
        results = list(df_result[0])        
        return results

    def get_spo(self, subject = False, sp_link = False, object = False, po_link = False, so_link = False, predicate = False):
        """
        A function that extracts SPOs with a specific subject, object, or predicate.

        :param subject:    An argument that extracts spos with a specific subject.
        :param predicate:  An argument that extracts spos with a specific predicate.
        :param object:     An argument that extracts spos with a specific object.

        :param sp_link:    An argument that specifies how to extract specific subjects and predicates. When given the 'or' option, it outputs spos that match either the designated subject or predicate. When given the 'and' option, it outputs spos where both the designated subject and predicate match.
        
        :param po_link:    An argument that specifies how to extract specific predicates and objects. When given the 'or' option, it outputs spos that match either the designated predicates or objects. When given the 'and' option, it outputs spos where both the designated predicates and objects match.
        
        :param so_link:    An argument that specifies how to extract specific subjects and objects. When given the 'or' option, it outputs spos that match either the designated subject or objects. When given the 'and' option, it outputs spos where both the designated subject and objects match.
        """
    
        # print("subject:")
        subject = input("Enter the 'subject' you want to search for. Separate multiple entries with a comma(,).: ")
        # print(subject)
        
        if subject == '':
            subject = False
                        
        # print("object:")
        object = input("Enter the 'object' you want to search for. Separate multiple entries with a comma(,).: ")
        # print(object)

        if object == '':
            object = False

        # print("predicate:")
        predicate = input("Enter the 'predicate' you want to search for. Separate multiple entries with a comma(,).: ")
        # print(predicate)

        if predicate == '':
            predicate = False
        
        if subject and object:
            print("How to link subjects and and objects?")
            print("If you use AND, the spo satisfying both subject and object is searched. If you use OR, the spo satisfying either the subject or the object is searched.")
            so_link = input("so_link : ")
            # print(so_link)

        if subject and predicate:
            print("How to link subjects and and predicates?")
            print("If you use AND, the spo satisfying both subject and predicates is searched. If you use OR, the spo satisfying either the subject or the predicates is searched.")
            sp_link = input("sp_link : ")
            # print(sp_link)
            
        if predicate and object:
            print("How to link predicates and and objects?")
            print("If you use AND, the spo satisfying both predicates and objects is searched. If you use OR, the spo satisfying either the predicates or the objects is searched.")
            po_link = input("po_link : ")
            # print(po_link)

        
        
        if subject and predicate:
            if sp_link == False:
                sp_link = ' and '
            else:
                sp_link = sp_link
        elif predicate == False or object == False:
            sp_link = ''

        #
        if predicate and object:
            if po_link == False:
                po_link = ' and '
            else:
                po_link = po_link
        elif object == False or subject == False:
            po_link = ''

        #
        if subject and object:
            if so_link == False:
                so_link = ' and '
            else:
                so_link = so_link
        elif subject == False or predicate == False:
            so_link = ''


        match = f"MATCH (s:object)-[r]->(o:object) "
        
        if subject == False:
            s_where = ' '
        else:
            subj = subject.split(', ')
            for i, sub in enumerate(subj):
                # sub = sub.replace(' ', '')
                if i == 0:
                    s_where = f" (startNode(r).object = '{sub}' "
                else:
                    s_where = s_where + f" or startNode(r).object = '{sub}' "
            s_where = s_where + ") "
            # s_where = f" startNode(r).object IN {subject} "
        
        if object == False:
            o_where = ' '
        else:
            obj = object.split(', ')
            for i, ob in enumerate(obj):
                # sub = sub.replace(' ', '')
                if i == 0:
                    o_where = f" (endNode(r).object = '{ob}' "
                else:
                    o_where = o_where + f" or endNode(r).object = '{ob}' "
            o_where = o_where + ") "            
            # o_where = f" endNode(r).object IN {object} "
            
        if predicate == False:
            p_where = ' '
        else:
            pred = predicate.split(', ')
            for i, prd in enumerate(pred):
                # sub = sub.replace(' ', '')
                if i == 0:
                    p_where = f" (type(r) = '{prd}' "
                else:
                    p_where = p_where + f" or type(r) = '{prd}' "
            p_where = p_where + ") "        
            # p_where = f" type(r) IN {predicate} "
        

        #
        if subject and object and predicate == False:
            where = "WHERE (" + s_where + so_link + o_where + ")"
        elif so_link == 'and' and po_link == 'or':
            where = "WHERE (" + s_where + so_link + o_where + po_link + p_where + ")"
        else:
            where = "WHERE (" + s_where + sp_link + p_where + po_link + o_where + ")"

        #    
        if subject == False and object == False and predicate == False:
            where = ' '

        
        with_q = "WITH r.video_path AS video_path, r.captions AS captions, properties(r) AS prop_r, type(r) AS predicate, startNode(r) AS startNode, endNode(r) AS endNode, [startNode(r).object, type(r), endNode(r).object] AS spo, [properties(r).begin_frame, properties(r).end_frame] AS frame"
        
        if subject:
            with_s = " COLLECT(DISTINCT startNode.object) as sub_cond "
        else:
            with_s = ''
            
        if object:
            with_o = "COLLECT(DISTINCT endNode.object) as ob_cond"
        else:
            with_o = ''
        
        if predicate:
            with_p = "COLLECT(DISTINCT predicate) as pred_cond "
        else:
            with_p = ''
        
        with_spo = ''
        if subject:
            if predicate == False and object == False:
                with_spo = ', ' + with_s
            if predicate and object == False:
                with_spo = ', ' + with_s + ', ' + with_p
            if predicate == False and object:
                with_spo = ', ' + with_s + ', ' + with_o
            if predicate and object:
                with_spo = ', ' + with_s + ', ' + with_p + ', ' + with_o
        elif subject == False:
            if predicate and object == False:
                with_spo = ', ' + with_p
            elif predicate == False and object:
                with_spo = ', ' + with_o
            elif predicate and object:
                with_spo = ', ' + with_p + ', ' + with_o
        
        with_q = with_q + '\n' + "WITH video_path, captions, collect(DISTINCT spo) as spo, collect(frame) as frame" + with_spo

                
        return_q = "RETURN video_path, captions, spo, frame"
        
        query = match + '\n' + where + '\n' + with_q + '\n' + return_q
        
        session = self.driver.session()                    
        result = session.run(query)
        end_time = time.time()
        out = result.data()
        out = pd.DataFrame(out) 
        
        print(tabulate(out, headers='keys', tablefmt='psql', showindex=False))
        
        if len(out) !=0:            
            video = self.embed_video(out["video_path"][0])   
        else:
            video = "No appropriate scene found."
        
        if len(out) == 0:
    
            if subject == False:
                s_where = ' '
            else:
                subj = subject.split(', ')
                subj_w2v = self.w2v(subj)
                for i, sub in enumerate(subj_w2v):
                    if i == 0:
                        s_where = f" (startNode(r).object = '{sub}' "
                    else:
                        s_where = s_where + f" or startNode(r).object = '{sub}' "
                s_where = s_where + ") "
                
            if object == False:
                o_where = ' '
            else:
                obj = object.split(', ')
                obj_w2v = self.w2v(obj)
                for i, ob in enumerate(obj_w2v):
                    # sub = sub.replace(' ', '')
                    if i == 0:
                        o_where = f" (endNode(r).object = '{ob}' "
                    else:
                        o_where = o_where + f" or endNode(r).object = '{ob}' "
                o_where = o_where + ") "            
                # o_where = f" endNode(r).object IN {object} "
        
            if predicate == False:
                p_where = ' '
            else:
                pred = predicate.split(', ')
                pred_w2v = self.w2v(pred)
                for i, prd in enumerate(pred_w2v):
                    if i == 0:
                        p_where = f" (type(r) = '{prd}' "
                    else:
                        p_where = p_where + f" or type(r) = '{prd}' "
                p_where = p_where + ") "        
        
            #
            if subject and object and predicate == False:
                where = "WHERE (" + s_where + so_link + o_where + ")"
            elif so_link == 'and' and po_link == 'or':
                where = "WHERE (" + s_where + so_link + o_where + po_link + p_where + ")"
            else:
                where = "WHERE (" + s_where + sp_link + p_where + po_link + o_where + ")"
        
            #    
            if subject == False and object == False and predicate == False:
                where = ' '
        
            query = match + '\n' + where + '\n' + with_q + '\n' + return_q
        
            session = self.driver.session()                    
            result = session.run(query)
            end_time = time.time()
            out = result.data()

            out = pd.DataFrame(out) 
            print("")
            print("There are no scenes searched by the keyword you entered.")
            print("We will proceed with the search including similar words.")
            print("Subject - Search & Extension Keywords : {}".format(subj_w2v))
            print("Object - Search & Extension Keywords : {}".format(obj_w2v))
            print("Predicate - Search & Extension Keywords : {}".format(pred_w2v))
            print("")
            print(tabulate(out, headers='keys', tablefmt='psql', showindex=False))
            
            #video
            if len(out) !=0:            
                video = self.embed_video(out["video_path"][0])   
            else:
                video = "No appropriate scene found."
        
        return video
        # return out
