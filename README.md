# SESE : ScEne SEarch
SESE is a video scene storing & searching module uses video scene caption to find a specified scene that user wants to retrieve.

<-- Usage 영상 -->

We often face the complex scene in the real world and video also contain that kind of scenes. Therefore, we need a proper way to deal with complex scene just to improve the quality of the video scene retreival.

<-- 1.jpg -->

Two main ideas of our approach are 
 - Parse scene graph from simplified caption
 - Use two types of database (RDB & GraphDB)



## Scene Graph Parsing
If you want to make your own DB to search with video caption dataset, use our Scene graph parsing LLM (: Fine-tuned Vicuna 7B) in Docker container, or you just use our parsed Activitynet Captions dataset, just skip this step.

First you need to put your raw dataset (csv file) in the data/raw folder and the column name of captions should be 'en_captions'

cd ./scene-graph_parsing
./build.sh
./run.sh
./bash.sh
python caption-to-scene-graph.py

Then you can find your parsed dataset ./data/scene_graph.csv and object dictionary ./data/object.csv.


## Usage of SESE
import SESE as sese

### Search function
- ㅎㄷㅅ_네

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




