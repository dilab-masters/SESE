# SESE : ScEne SEarch
> SESE is a video scene storing & searching module uses video scene caption to find a specified scene that user wants to retrieve.

<-- Usage 영상 -->

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
  : 특정 subject, predicate, object를 지정하여 원하는 장면을 찾는

- get_keyword()
  : keyword를 통해 원하는 장면을 찾고자 할 때 사용하는 함수

- get_keyword_video()
  : 특정 video를 지정한 후, keyword를 통해 원하는 장면을 찾고자 할 때 사용하는 함


### Create
 - add_object(df)
: neo4j에 등록하고자 하는 object 정보가 포함된 csv 파일을 업로드하는 함수

  + Argument
     *'df'* object 정보가 포함된 pandas dataframe
   e.g., act_obj_df = pd.read_csv('activitynet_object_graphDB.csv')
db.add_object(df = act_obj_df)

 - add_spo(df)
   neo4j에 등록하고자 하는 spo정보가 포함된 csv 파일을 업로드하는 함수
Argument *'df'* df spo(subject-predicate-object) 정보가 포함된 pandas dataframe
e.g., act_spo = pd.read_csv('activitiynet_indexing_graphDB.csv’)
db.add_spo(act_spo)

 - add_table(mariadb_database, csv_file)
   MariaDB의 database에 table로 등록하고자 하는 csv 파일을 업로드하는 함수
   Argument *'mariadb_database'* user가 지정한 database의 이름
*'csv_file'* caption정보가 포함된 csv파일
e.g., db.add_table(mariadb_database, 'activitynet_dataset.csv')


### Etc
 - get_description()
 현재 neo4j에 저장되어 있는 object와 predicate 정보를 보여주는 함수
Object와 predicate의 average, minimum, and maximum counts 정보와 여타 통계 정보들을 확인 가능
 e.g., sese.get_description()

 - get_object_list()
 database에 저장되어 있는 object들의 고유 list를 확인할 수 있는 함수
 e.g., sese.get_object_list()

  - get_object(object)
  원하는 object의 node 정보를 확인할 수 있는 함수
  Argument *'object'* : database에서 확인하고 싶은 object 선택
  e.g., sese.get_object(object='man')

<-- 2.jpg -->

 - get_predicate_list()
 DB에 저장되어 있는 predicate들의 고유 list를 확인할 수 있는 함수




