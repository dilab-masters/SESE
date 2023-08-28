# SESE : ScEne SEarch
> SESE is a video scene storing and searching module uses video scene caption to find a specified scene that user wants to retrieve.



 

Two main ideas of our approach are 
 - Parse scene graph from simplified caption
    + To perform searches based on specified subject, predicate, and object
 - Expand the keyword if there is no matched result
   + To improve searching performance

## Requirements
- [neointerface](https://pypi.org/project/neointerface/) </br>
`pip install neointerface`  </br>
                    
   
- [neo4j](https://neo4j.com/docs/api/python-driver/current/) </br>
`pip install neo4j` </br>
  
- [py2neo](https://pypi.org/project/py2neo/) </br>
`pip install py2neo` </br>

            
- [mysql-connector](https://pypi.org/project/mysql-connector-python/) </br>
`pip install mysql-connector` </br>
                    
                    
- [pytube](https://pypi.org/project/pytube/v) </br>
`pip install pytube` </br>

- [pymysql](https://pypi.org/project/pymysql/) </br>
`pip install pymysql`</br></br>

## Scene Graph Parsing
>You can build your own database by using our Scene graph parsing LLM (: Fine-tuned Vicuna 7B) in Docker container. 
If you just want to use our parsed Activitynet Captions dataset, just skip this step.

</br>
First, you need to put your raw dataset (csv file) in the `data/raw` folder.
Your data should include 

~~~cd ./scene-graph_parsing
./build.sh
./run.sh
./bash.sh
python caption-to-scene-graph.py
~~~

Then you can find your parsed dataset on `data/scene_graph.csv`.
</br></br>

## Usage of SESE
### DB Connect & Module Load
~~~
from SESE import SESE as db

neo4j_url = "YOUR NEO4J URL"
neo4j_user = "YOUR NEO4J USER NAME"
neo4j_password = "YOUR NEO4J PASSWORD"
mariadb_user = "YOUR MARIADB USER NAME"
mariadb_password = "YOUR MARIADB PASSWORD"
mariadb_host = "YOUR HOST IP" 
maridb_database = "YOUR MARIADB DATABASE NAME"

sese = db(neo4j_url, neo4j_user, neo4j_password, 
          mariadb_user, mariadb_host, mariadb_database)
~~~
</br>

- Example 
~~~
from SESE import SESE as db

neo4j_url = "neo4j://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "testtest"
mariadb_user = "dilab"
mariadb_password = "1111"
mariadb_host = "127.0.0.1"
maridb_database = "mydb"

sese = db(neo4j_ur, neo4j_user, neo4j_password, 
          mariadb_user, mariadb_host, mariadb_database)
~~~
</br>

### Create
- `add_df(mariadb_database, csv_file)`
: A function that uploads data (csv file) on DB

   + *mariadb_database* : RDB name 
    *csv_file* : video-caption-scene-graph dataset (csv file)
   + e.g., `db.add_table(mariadb_database, './data/activitynet_10_sg.csv')` </br></br>

### Search
- `get_spo()`
: A function that specifies subject, predicate, object to search a scene. </br></br>
![image](https://github.com/dilab-masters/SESE/assets/142645709/3582d652-688f-409d-915b-b161b2fc75ec)

- `get_keyword()`
: A function that specifies keyword to search a scene. </br></br>
![image](https://github.com/dilab-masters/SESE/assets/142645709/68c8a477-06c6-4f21-858a-3527286065c6)


### Etc
- `get_description()`
: A function that prints information of objects and predicates on the GraphDB 
e.g., average, minimum, and maximum counts... </br></br>
- `get_object_list()`
: A function that prints unique list of objects on the GraphDB </br></br>

- `get_object(object)`
: A function that prints information of specified object node
    + *object* : The object that wants to know
    + e.g., `sese.get_object(object='man')`  </br></br>

- `get_predicate_list()`
: A function that prints unique list of predicates on the GraphDB

