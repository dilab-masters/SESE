# SESE : ScEne SEarch
> SESE is a video scene storing & searching module uses video scene caption to find a specified scene that user wants to retrieve.
<br/>

<-- 비디오 삽입 -->

 
   
We often face the complex scene in the real world and video also contain that kind of scenes. Therefore, we need a proper way to deal with complex scene just to improve the quality of the video scene retreival.

<img src = "https://private-user-images.githubusercontent.com/142645709/262647639-0ac61292-892f-4956-ac1b-cbc7f07f6ea2.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTEiLCJleHAiOjE2OTI3ODg2ODUsIm5iZiI6MTY5Mjc4ODM4NSwicGF0aCI6Ii8xNDI2NDU3MDkvMjYyNjQ3NjM5LTBhYzYxMjkyLTg5MmYtNDk1Ni1hYzFiLWNiYzdmMDdmNmVhMi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMwODIzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMDgyM1QxMDU5NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jYWIxODJjZWQ5NmM3NmZiNjM0MTQ0OGNiMjc3ZTI2ZWQ1N2U3NGQ2MTYyZmU4YzQ1MzQ0ZmY5MWU2MzI0NGI3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.J5ktGpvBqL-5BSa3j5gBO36RIPuLEqJsOrgCwBFti0E" width='90%'></img>

Three main ideas of our approach are 
 - Parse scene graph from simplified caption
 - Use two types of database (RDB & GraphDB)
 - Expand the keyword if there is no matched result



## Scene Graph Parsing
If you want to make your own DB to search with video caption dataset, use our Scene graph parsing LLM (: Fine-tuned Vicuna 7B) in Docker container, or you just use our parsed Activitynet Captions dataset, just skip this step.

First you need to put your raw dataset (csv file) in the data/raw folder and the column name of captions should be 'en_captions'

~~~cd ./scene-graph_parsing
./build.sh
./run.sh
./bash.sh
python caption-to-scene-graph.py
~~~

Then you can find your parsed dataset ./data/scene_graph.csv and object dictionary ./data/object.csv.


## Usage of SESE
import SESE as sese

### Search function
- get_spo()
  : A function that specifies subject, predicate, object to search a scene.

- get_keyword()
  : A function that specifies keyword to search a scene.

- get_keyword_video()
  : A function that specifies video and keyword to search a scene.


### Create
 - add_object(df) <br/>
  : A function that upload object dictionary on GraphDB

    + Argument
     *'df'* pandas dataframe of object dictionary
    + e.g., act_obj_df = pd.read_csv('activitynet_object_graphDB.csv') <br/>
   sese.add_object(df = act_obj_df)

 - add_spo(df)
   : A function that upload scene graph on GraphDB

   + Argument *'df'* pandas dataframe which contains scene graph (subject, predicate, object)
   + e.g., act_spo = pd.read_csv('activitiynet_indexing_graphDB.csv’) <br/>sese.add_spo(act_spo)

 - add_table(mariadb_database, csv_file)
   : A function that upload caption (csv file) on RDB

   + Argument *'mariadb_database'* RDB name <br/>*'csv_file'* video-caption dataset (csv file)
     + e.g., db.add_table(mariadb_database, 'activitynet_dataset.csv')


### Etc
 - get_description()
   : A function that prints information of objects and predicates on the GraphDB <br/>
(average, minimum, and maximum counts...)
   + e.g., sese.get_description()

 - get_object_list()
   : A function that prints unique list of objects on the GraphDB
   + e.g., sese.get_object_list()

  - get_object(object)
    : A function that prints information of specified object node
    + Argument *'object'* : The object that wants to know
    + e.g., sese.get_object(object='man')


 - get_predicate_list()
   : A function that prints unique list of predicates on the GraphDB




