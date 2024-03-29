# -*- coding: utf-8 -*-
"""종합 코드.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fmbU6K9HqFKkg8GXHfIuujzb_t983XFB

### 데이터 전처리(필터링) 및 복합불량 데이터 생성
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import cv2
import networkx as nx
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.cluster import DBSCAN

from sklearn.metrics import confusion_matrix,f1_score

# %matplotlib inline

df=pd.read_pickle('/content/drive/MyDrive/LSWMD.pkl/LSWMD.pkl')
df.info()

def make_test_array(df,column,num):
 test_array=np.array(df[column][num])

 new_test_array=np.where(test_array<=1,0,test_array)

 return new_test_array,test_array

def make_testimg(df,column,num,shape1,shape2):
  test_array=make_test_array(df,column,num)[1]
  x=[]
  x.append(make_test_array(df,column,num)[0])

  sw = np.ones((1, shape1, shape2))

  for i in range(len(x)):
    # skip null label
    sw = np.concatenate((sw, x[i].reshape(1, shape1, shape2)))

  y = sw[1:]

  new_x = np.zeros((len(y), shape1, shape2, 3))

  for w in range(len(y)):
    for i in range(shape1):
        for j in range(shape2):
          if y[w,i,j]==0:
            new_x[w, i, j, int(y[w, i, j])] = 0
          else:
            new_x[w, i, j, int(y[w, i, j])] = shape1

  new_x=new_x.astype(np.uint8)

  return new_x,test_array


def filter(df,num,shape1,shape2,threshold):
  dst=cv2.filter2D(df.waferMap[num],-1,kernel)
  new_dst=dst/(sum_kernel*2)
  filter_img=np.where(new_dst>threshold,1,0)

  ###test sample 만들기
  test_sample=np.where(df.waferMap[num]<2,0,2)


  ### 값 변환

  f_list=[]
  for i in range(shape1):
    for j in range(shape2):
      if filter_img[i][j]==0:
        f_list.append(filter_img[i][j])
      elif test_sample[i][j]==2 and filter_img[i][j]==1:
        f_list.append(filter_img[i][j])
      else:
        f_list.append(0)

  im=np.array(f_list)
  im=im.reshape(shape1,shape2)

  ### 실제 이미지로 변환
  n_list=[]
  for i in range(shape1):
    for j in range(shape2):
      if im[i][j]==0 and df['waferMap'][num][i][j]==0:
        n_list.append(0)
      elif im[i][j]==0 and df['waferMap'][num][i][j]==1:
        n_list.append(1)
      elif im[i][j]==1 and df['waferMap'][num][i][j]==2:
        n_list.append(2)
      else :
        n_list.append(1)

  image=np.array(n_list)
  image=image.reshape(shape1,shape2)

  return image

def make_wafer(a,b,shape1,shape2):
  n_list=[]
  for i in range(shape1):
    for j in range(shape2):
      if a[i][j]==0 and b[i][j]==0:
        n_list.append(0)
      elif a[i][j]==1 and b[i][j]==1:
        n_list.append(1)
      elif a[i][j]==1 and b[i][j]==2:
        n_list.append(2)
      elif a[i][j]==2 and b[i][j]==1:
        n_list.append(2)
      elif a[i][j]==2 and b[i][j]==2:
        n_list.append(2)
      else :
        n_list.append(1)

  image=np.array(n_list)
  image=image.reshape(shape1,shape2)
  return image

def make_test_list(df,i):
  x,y=make_testimg(df,'filter_waferMap',i,shape1,shape2)
  return x

def dfs(graph, start_node):
    ## 기본은 항상 두개의 리스트를 별도로 관리해주는 것
    need_visited, visited = list(), list()

    ## 시작 노드를 시정하기
    need_visited.append(start_node)

    ## 만약 아직도 방문이 필요한 노드가 있다면,
    while need_visited:
        ## 그 중에서 가장 마지막 데이터를 추출 (스택 구조의 활용)
        node = need_visited.pop()

        ## 만약 그 노드가 방문한 목록에 없다면
        if node not in visited:

            ## 방문한 목록에 추가하기
            visited.append(node)

            ## 그 노드에 연결된 노드를
            need_visited.extend(graph[node])
    #visited = visited[:12]

    return visited

def make_adj_matrix(num, shape_1,shape_2,df,threshold):
  filter_data=df.iloc[num]
  filter_wbm = filter_data['waferMap']
  filter_index = []
  adj_matrix = []

  for shape1 in range(shape_1):
    for shape2 in range(shape_2):
        if filter_data['waferMap'][shape1,shape2]==2:
            filter_index.append([shape1,shape2])

  #print(len(filter_index))

  for i in range(len(filter_index)):
      possible_way = []

      first_i_index = filter_index[i][0]
      second_i_index = filter_index[i][1]


      #print("---------------", i ,"----------------")
      #print("i", [first_i_index, second_i_index])


      if (first_i_index != 0) and (second_i_index != 0):
          possible_way_1 = [first_i_index, second_i_index + 1]
          possible_way_2 = [first_i_index + 1, second_i_index]
          possible_way_3 = [first_i_index - 1, second_i_index ]
          possible_way_4 = [first_i_index, second_i_index -1]

      elif (first_i_index == 0):

          possible_way_1 = [first_i_index, second_i_index + 1]
          possible_way_2 = [first_i_index + 1, second_i_index]
          possible_way_3 = [first_i_index , second_i_index ]
          possible_way_4 = [first_i_index, second_i_index -1]

      elif (second_i_index == 0):

          possible_way_1 = [first_i_index, second_i_index + 1]
          possible_way_2 = [first_i_index + 1, second_i_index]
          possible_way_3 = [first_i_index -1, second_i_index]
          possible_way_4 = [first_i_index, second_i_index ]

      possible_way.extend([possible_way_1,possible_way_2, possible_way_3, possible_way_4])
      #possible_way = np.array(possible_way).reshape(4,2)
      #print("possible way", possible_way)
      for j in range(len(filter_index)):
            first_j_index = filter_index[j][0]
            second_j_index = filter_index[j][1]
            j_index = [first_j_index, second_j_index]

          #print("j_index", j_index)
          #print("possible way", possible_way)

          #print(j_index in possible_way)

            if j_index in possible_way:
                matrix_value = 1
            else:
                matrix_value = 0

          #print("matrix_value", matrix_value)
            adj_matrix.append(matrix_value)

  adj_matrix = np.array(adj_matrix).reshape(len(filter_index),len(filter_index))


  for i in range(len(filter_index)):
    for j in range(len(filter_index)):
      if i ==j:
        adj_matrix[i,j] = 0



      graph = nx.Graph(adj_matrix)

      dfs_root = []

      for i in range(len(filter_index)):
        temp_root = dfs(graph,i)
        dfs_root.append(temp_root)

      dfs_root_over_12 = []
      for i in dfs_root:
        if len(i) < threshold:
          i = 0
        else:
          i = 1
        dfs_root_over_12.append(i)



      for i in range(len(filter_index)):
        # 12 넘는지 안넘는지. 넘으면 1 아니면 0
        over_12_or_not = dfs_root_over_12[i]
        first_fail_index = filter_index[i][0]
        second_fail_index = filter_index[i][1]

        fail_index = filter_wbm[first_fail_index,second_fail_index]

          #print("first", first_fail_index)
          #print("second", second_fail_index)
          #print(fail_index)


        if over_12_or_not == 0:
          filter_wbm[first_fail_index,second_fail_index] = 1



      return filter_wbm

def make_sub_df(shape1,shape2):
  sub_df = df_withlabel.loc[df_withlabel['waferMapDim'] == (shape1, shape2)]
  sub_df.reset_index(inplace=True)

  return sub_df

df = df.drop(['waferIndex'], axis = 1)
def find_dim(x):
    dim0=np.size(x,axis=0)
    dim1=np.size(x,axis=1)
    return dim0,dim1
df['waferMapDim']=df.waferMap.apply(find_dim)
df.sample(5)

df['failureNum']=df.failureType
df['trainTestNum']=df.trianTestLabel
mapping_type={'Center':0,'Donut':1,'Edge-Loc':2,'Edge-Ring':3,'Loc':4,'Random':5,'Scratch':6,'Near-full':7,'none':8}
mapping_traintest={'Training':0,'Test':1}
df=df.replace({'failureNum':mapping_type, 'trainTestNum':mapping_traintest})

df_withlabel = df[(df['failureNum']>=0) & (df['failureNum']<=6) & (df['failureNum']!=5)]
df_withlabel =df_withlabel.reset_index()

df_test=df_withlabel[df_withlabel['trainTestNum']==1]

df_test

shape1=54
shape2=71
sub_df=make_sub_df(shape1,shape2)

sub_df.drop(['level_0','index','dieSize','lotName'],axis=1,inplace=True)

reset_df=sub_df.reset_index()
for i in range(len(sub_df)):
  if (2 in reset_df['waferMap'][i]) == False:
    reset_df.drop(index=i,inplace=True)
  elif (1 in reset_df['waferMap'][i]) == False:
    reset_df.drop(index=i,inplace=True)
print(len(reset_df)/len(sub_df))

def make_filtering_list(i,len_list,len_filter,shape1,shape2):
  filtering_list=[]
  for size in range(len_list):
    filtering_list.append(make_adj_matrix(size,shape1,shape2,reset_df[reset_df['failureNum']==i],len_filter))

  return filtering_list

"""## 'Center':0,'Donut':1,'Edge-Loc':2,'Edge-Ring':3,'Loc':4,'Random':5 'Scratch':6,'Near-full':7,'none':8"""

sub_df['failureNum'].value_counts()

new_filter_donut=[filter_donut[0],filter_donut[1],filter_donut[13],filter_donut[14],filter_donut[15],filter_donut[16]]
for i in range(len(new_filter_donut)):
  plt.imshow(new_filter_donut[i])
  plt.show()

filter_center=make_filtering_list(0,12,12,shape1,shape2)
filter_donut=make_filtering_list(1,17,12,shape1,shape2)
filter_edge_loc=make_filtering_list(2,4,12,shape1,shape2)
filter_loc=make_filtering_list(4,2,12,shape1,shape2)
filter_scratch=make_filtering_list(6,2,12,shape1,shape2)

def make_multi(filter1,filter2,shape1,shape2):
  multi_data=[]
  for i in range(len(filter1)):
    for j in range(len(filter2)):
      multi_data.append(make_wafer(filter1[i], filter2[j],shape1,shape2))

  return multi_data

center_donut=make_multi(filter_center,new_filter_donut,shape1,shape2)
center_edge_loc=make_multi(filter_center,filter_edge_loc,shape1,shape2)
center_loc=make_multi(filter_center,filter_loc,shape1,shape2)
center_scratch=make_multi(filter_center,filter_scratch,shape1,shape2)
donut_edge_loc=make_multi(new_filter_donut,filter_edge_loc,shape1,shape2)
donut_loc=make_multi(new_filter_donut,filter_loc,shape1,shape2)
donut_scratch=make_multi(new_filter_donut,filter_scratch,shape1,shape2)
donut_loc=make_multi(new_filter_donut,filter_loc,shape1,shape2)

len(center_donut)

"""### clustering으로 다중불량 이미지 하나씩 나누기"""

def segmented_by_dbscan(data,i, shape1,shape2):
  ### wafer데이터 복원을 위한 기본 틀 제작
  img = data[i]
  test_img=img.copy()
  test_wafer=np.where(test_img>=1,1,0)

  ### clustering을 위한 이미지 변환
  test_w=np.where(test_img<2,0,test_img)

  copy_w=[]
  for i in range(shape1):
    for j in range(shape2):
      if test_w[i][j]==2:
        copy_w.append((i,j))
      else:
        copy_w.append((0,0))


  ### clustering

  dbscan=DBSCAN(eps=1.5)
  clusters=dbscan.fit_predict(copy_w)
  ### cluster 잘 되었는지 확인
  print('cluster 결과')
  print(pd.DataFrame(clusters).value_counts())

  ### segmentation

  cluster_1=np.where(clusters==1,1,0)
  cluster_2=np.where(clusters==2,2,0)

  ### cluster별로 이미지 만들기
  new=test_wafer.reshape(shape1*shape2,)
  new_test_wafer1=new.copy()
  new_test_wafer2=new.copy()
  new_test_wafer1=np.where(cluster_1==1,2,new)
  new_test_wafer2=np.where(cluster_2==2,2,new)

  new_test_wafer1=new_test_wafer1.reshape(shape1,shape2)
  new_test_wafer2=new_test_wafer2.reshape(shape1,shape2)

  print('==============================cluster_1======================================')
  plt.imshow(new_test_wafer1)
  plt.show()

  print('==============================cluster_2======================================')
  plt.imshow(new_test_wafer2)
  plt.show()


  return new_test_wafer1, new_test_wafer2

cluster_1=[]
cluster_2=[]
for i in range(len(center_donut)):
  cluster1,cluster2 =segmented_by_dbscan(center_donut,i,shape1,shape2)
  cluster_1.append(cluster1)
  cluster_2.append(cluster2)

df_list=[center_donut,center_edge_loc,center_loc,center_scratch,donut_edge_loc,donut_loc,donut_scratch,donut_loc]
cluster_1=[]
cluster_2=[]
for i in df_list:
  cluster1,cluster2=segmented_by_dbscan(i,1,shape1,shape2)
  cluster_1.append(cluster1)
  cluster_2.append(cluster2)

def save_cluster(cluster,i):
  plt.imshow(cluster)
  plt.savefig("/content/drive/MyDrive/guide_test_resize/"+str(i)+".jpg")

clusters=[]
for i in range(len(cluster_1)):
  clusters.append(cluster_1[i])
  clusters.append(cluster_2[i])

for i in range(len(clusters)):
  save_cluster(clusters[i],i)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content
!git clone https://github.com/ultralytics/yolov5.git

#yolov5를 위한 패키지 설치
# %cd /content/yolov5/
! pip install -r requirements.txt

!python detect.py --weights /content/drive/MyDrive/yolov5/best.pt  --source /content/drive/MyDrive/guide_test_resize --save-txt

"""39,73,107,109,111,113,117,141,143"""

import numpy as np
label_list=[]
for num in range(144):
  if num in [39,73,107,109,111,113,117,141,143]:
    label_list.append(100)
  else:
    gt = np.loadtxt('/content/yolov5/runs/detect/exp2/labels/'+str(num)+'.txt', delimiter = ' ')
    label_list.append(gt[0])

label_txt_list=[]
for i in label_list:
  if int(i) == 0:
    label_txt_list.append("center")
  elif int(i) == 1:
    label_txt_list.append("donut")
  elif int(i) == 2:
    label_txt_list.append("edge_loc")
  elif int(i) == 3:
    label_txt_list.append("loc")
  elif int(i) == 4:
    label_txt_list.append("scratch")
  else :
    label_txt_list.append("no_pattern")

final_label=[]
for i in range(len(label_txt_list)):
  if i%2 ==0:
    final_label.append([label_txt_list[i],label_txt_list[i+1]])

'no_pattern' in final_label[19]

check_list=[]
for i in range(len(final_label)):
  if 'no_pattern' in final_label[i]:
    check_list.append(0)
  else:
    check_list.append(1)

check_list2=[]
for i in range(len(final_label)):
  if final_label[i]==['donut','center']:
    check_list2.append(1)
  else:
    check_list2.append(0)

sum(check_list)/len(check_list)

len(check_list)-sum(check_list)

sum(check_list2)/len(check_list2)

len(check_list2)-sum(check_list2)

sum(check_list2)

final_label

for i in df_list:
  plt.imshow(i[1])
  plt.show()

def f1_score(a,b):
  x1=a*b
  x2=a+b
  f1=2*(x1/x2)

  return f1

precision=[1,0.981,0.78,0.818,0.956]
recall=[0.997,0.975,0.885,0.886,0.825]
defect=['center','donut','edge_loc','loc','scratch']

for i in range(len(precision)):
  print(defect[i],':',round(f1_score(precision[i],recall[i]),3))

