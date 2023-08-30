# SESE : ScEne SEarch
> SESE is a video scene storing and searching module uses video scene caption to find a specified scene that user wants to retrieve.

</br></br>



</br>

Two main ideas of our approach are 
 - Parse scene graph from simplified caption
    + To perform searches based on specified subject, predicate, and object
 - Expand the keyword if there is no matched result
   + To improve searching performance
  
</br>

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
Here's the column names that your dataset should have.
</br> </br>

| video_id | begin_frame | end_frame | captions |
|----------|-------------|-----------|----------|    

*video_id* : the id of video  </br>
*begin_frame* : the starting point of the scene </br>
*end_frame* : the ending point of the scene </br>
*captions* : the description of the scene  </br>
</br>  

After that, run the code below.  

~~~cd ./scene-graph_parsing
./build.sh
./run.sh
./bash.sh
python caption-to-scene-graph.py
~~~

Then you can get your parsed dataset on `data/scene_graph.csv`.
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
![get_spo](https://github.com/dilab-masters/SESE/assets/142645709/4a7f5034-3e46-410b-9af0-c690612cbf06)


- `get_keyword()`
: A function that specifies keyword to search a scene. </br></br>
![get_keyword](https://github.com/dilab-masters/SESE/assets/142645709/0531f61d-661f-4e44-82ac-463d2593e8a9)



### Etc
- `get_description()`
: A function that prints information of objects and predicates on the GraphDB 
e.g., average, minimum, and maximum counts... </br></br>
- `get_object_list()`
: A function that prints unique list of objects on the GraphDB </br></br>

- `get_object(object)`
: A function that prints information of specified object node
    + *object* : The object that wants to get information
    + e.g., `sese.get_object(object='man')`  </br></br>

- `get_predicate_list()`
: A function that prints unique list of predicates on the GraphDB

