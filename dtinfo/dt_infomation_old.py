import numpy as np
from graphviz import Digraph
import pandas as pd

def find_elements(list, value):
    """valueと同じ値を持つlistの要素番号を返す(一番最初の要素のみ)"""
    for i in range(len(list)):
        if value==list[i]:
            return i
        
class DTinfo:
    """決定木の情報をノードi(i=0,1,2...n_nodes)ごとに格納
    """  
    def __init__(self):
        
        self.n_nodes=0 #(int):全ノード数
        self.avef=-10000 #(float)特徴量数平均（葉ノードまでの特徴量数の平均) -10000=None
        self.feature=None #(ndarray):i番目のノードの分割に用いられる特徴量は何番目の特徴か※なければ-2
        self.threshold=None#(ndarray):i番目のノードの分割における閾値は何か※なければ-2？
        self.children_left=None #(ndarray):i番目のノードの子ノード(左)は何番目のノードか※なければ-1
        self.children_right=None#(ndarray):i番目のノードの子ノード(右)は何番目のノードか※なければ-1
        self.mother_node=None   #(ndarray):i番目のノードの親ノードは何番目のノードか※親がなければ-1
        self.values=None        #(ndarray):i番目のノードに分割されてきたデータのクラスごとの数
        self.node_depth=None    #(ndarray):i番目のノードの深さ
        self.is_leaves=None     #(ndarray(TorF))i番目のノードは葉ノードか
        self.xn=None#(list)データの特徴量名※特徴量削減で決定木を作製した場合は対応する特徴量名のみを残しほかを消すこと
        self.yn=None#(list)データのクラス名
        
    def memo_from_clf(self,clf,xn=None,yn=None):
        """fit済みclfから決定木情報を抽出

        Args:
            clf (desiciontreeclassfier): fit済みclf
            xn(list):clfの作成に用いた特徴量名リスト
            yn(list):clfの作成に用いたクラス名リスト
        """
        self.xn=xn
        self.yn=yn
        
        self.n_nodes = clf.tree_.node_count
        self.feature = clf.tree_.feature
        self.threshold = clf.tree_.threshold
        self.children_left = clf.tree_.children_left
        self.children_right = clf.tree_.children_right
        self.values = np.around(clf.tree_.value, decimals=4)
        
        self.node_depth = np.zeros(shape=self.n_nodes, dtype=np.int64)
        self.is_leaves = np.zeros(shape=self.n_nodes, dtype=bool)
        
        stack = [(0, 0)]  # start with the root node id (0) and its depth (0)
        while len(stack) > 0:
            # `pop` ensures each node is only visited once
            node_id, depth = stack.pop()
            self.node_depth[node_id] = depth

            # If the left and right child of a node is not the same we have a split
            # node
            is_split_node = self.children_left[node_id] != self.children_right[node_id]
            # If a split node, append left and right children and depth to `stack`
            # so we can loop through them
            if is_split_node:
                stack.append((self.children_left[node_id], depth + 1))
                stack.append((self.children_right[node_id], depth + 1))
            else:
                self.is_leaves[node_id] = True
    
        self.mother_node = np.zeros(shape=self.n_nodes, dtype=np.int64)#親ノード情報
        self.mother_node[0]=-1#根ノードの親ノードはなし
        for i in range(self.n_nodes):#i番目のノードの子ノードに親が誰か記録させる
            if self.children_left[i]!=-1:
                self.mother_node[self.children_left[i]]=i
            if self.children_right[i]!=-1:
                self.mother_node[self.children_right[i]]=i
    
        self.fave=self.calculate_usef_ave()
                  
    def fwrite_info(self,fname):
        """csv形式で決定木情報をファイルに書き込む
        一行目に採用する特徴量名
        二行目から順に1.ノード番号 2.ノードの深さ 3.分割に採用する特徴量 4.分割の閾値 
        5.左子ノードのノード番号 6.右子ノードのノード番号 7.親ノードの番号、8．ノードにおけるクラスごとのデータ量
        
        Args:
        fname(str):書き込むファイルのディレクトリ
        """  
        
        #file書き込みにxn、決定木情報は必須
        if self.xn!=None:
            f = open(fname, "w")
            #特徴量情報の書き込み
            xname=','.join(map(str,self.xn))     
            f.write(xname+'\n')
            fave=str(self.avef)
            f.write(fave+'\n')
            #決定木情報の書き込み
            for i in range(self.n_nodes):
                nodeinfo =str(i)+','+str(self.node_depth[i])
                nodeinfo+=','+str(self.feature[i])+','+str("{:.4g}".format(self.threshold[i]))
                nodeinfo+=','+str(self.children_left[i])+','+str(self.children_right[i])
                nodeinfo+=','+str(self.mother_node[i])
                nodeinfo+=','+' '.join(map(str,self.values[i][0]))
                f.write(nodeinfo+'\n')
            f.close()
        else:
            print("please input xn infomation")
    
    def fread_info(self,fname):
        """決定木情報をcsvファイルから読み込む

        Args:
            fname (str): 読み込むファイルのディレクトリ
        """
        df_xn= pd.read_csv(fname,header=None,nrows=1)
        self.xn=df_xn.values.ravel().tolist()
        
        df_fave=pd.read_csv(fname,header=None,skiprows=lambda x: x not in [1])
        self.avef=float(df_fave.values[0,0])
        
        df_DT = pd.read_csv(fname,header=None,skiprows=2)
        df_DT=df_DT.values
        
        self.n_nodes = len(df_DT[:,0])
        self.feature = df_DT[:,2].astype(np.int64)
        self.threshold = df_DT[:,3].astype(np.float64)
        self.children_left = df_DT[:,4].astype(np.int64)
        self.children_right = df_DT[:,5].astype(np.int64)
        self.mother_node = df_DT[:,6].astype(np.int64)
        self.values = np.zeros((self.n_nodes,1,len(df_DT[:,7][1].split())))
        self.node_depth = df_DT[:,1].astype(np.int64)
        self.is_leaves = np.zeros(shape=self.n_nodes, dtype=bool)
        
        values = df_DT[:,7]
        for i in range(self.n_nodes):  
            strlist = values[i].split()
            self.values[i]=np.array(strlist).astype(np.float64)   
            if self.feature[i]==-2 and self.children_left[i]==-1:
                self.is_leaves[i]=True
            else:
                self.is_leaves[i]=False
            
    def script_info(self,columns=True):
        """決定木情報を出力：
        順に1.ノード番号 2.ノードの深さ 3.分割に採用する特徴量 4.分割の閾値
        5.左子ノードのノード番号 6.右子ノードのノード番号 7.ノードにおけるクラスごとのデータ量
        
        Args:
        columns(bool):情報タイトルを出すか否か
        """
        if columns:#情報タイトルを出すか否か
            print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}".format("node_i","depth","feature","threhld","c_left","c_right","mother","value"))
        
        for i in range(self.n_nodes):
            if self.is_leaves[i]:
                print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}"
                      .format(i,self.node_depth[i],"leaf","leaf","none","none",self.mother_node[i],str(self.values[i])))
            else:
                print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}"
                      .format(i,self.node_depth[i],self.feature[i],str("{:.4g}".format(self.threshold[i])),
                              self.children_left[i],self.children_right[i],self.mother_node[i],str(self.values[i])))

    def plot_DT(self,title,pas="../output/Nsgaii/DTplot",type="pdf",view=False):
        """決定木の可視化

        Args:
            title (str): 決定木グラフのタイトル
            pas (str, optional): 決定木グラフを保存するフォルダまでのパス. Defaults to "../output/Nsgaii/DTplot".
            type (str, optional):ファイルの保存形式. Defaults to "pdf".
            view (bool, optional): グラフをすぐ見るか. Defaults to False.
        """
        
        # 有向グラフのインスタンス化
        g = Digraph()
        # 属性の指定
        g.attr('node', shape='square')
        for i in range(self.n_nodes):
            if self.is_leaves[i]==False:
                mother= 'node='+str(i)+'\n'+str(self.xn[self.feature[i]])+"<="+str(self.threshold[i])+'\n'+str(self.values[i])
                if self.yn==None:
                    leaf_left  = 'node='+str(self.children_left[i])+'\n' +'class='+str(np.argmax(self.values[self.children_left[i]]))+'\n'+str(self.values[self.children_left[i]])
                    leaf_right = 'node='+str(self.children_right[i])+'\n'+'class='+str(np.argmax(self.values[self.children_right[i]]))+'\n'+str(self.values[self.children_right[i]])
                else:
                    leaf_left  = 'node='+str(self.children_left[i])+'\n' +'class='+str(self.yn[np.argmax(self.values[self.children_left[i]])])+'\n'+str(self.values[self.children_left[i]])
                    leaf_right = 'node='+str(self.children_right[i])+'\n'+'class='+str(self.yn[np.argmax(self.values[self.children_right[i]])])+'\n'+str(self.values[self.children_right[i]])
                left  = 'node='+str(self.children_left[i])+'\n'+str(self.xn[self.feature[self.children_left[i]]])+"<="+str(self.threshold[self.children_left[i]])+'\n'+str(self.values[self.children_left[i]])
                right = 'node='+str(self.children_right[i])+'\n'+str(self.xn[self.feature[self.children_right[i]]])+"<="+str(self.threshold[self.children_right[i]])+'\n'+str(self.values[self.children_right[i]])
                if self.is_leaves[self.children_left[i]]==False:
                    g.edge(mother,left)
                else:
                    g.edge(mother,leaf_left)
                if self.is_leaves[self.children_right[i]]==False:
                    g.edge(mother,right)
                else:
                    g.edge(mother,leaf_right)
        g.render(pas+"/"+title, format=type, view=view)


    def predict(self,testx,output=True):
        """DT情報を基にテストデータに対するクラスを予測、予測に用いる条件を表示
        Args:
            testx (ndarray): テストデータ
        Returns:
            pred:テストデータに対する予測クラス
        """
        #testxを葉ノードまで分類しその分類過程を記録する
        node=0
        nodelist=[0]#testxが通ったノードの番号
        directlist=[]#testxの分割に際し、左(閾値以下)に通るか右(閾値以上)に通るか、左:-1 右:1
        while self.feature[node]!=-2:#葉ノードかどうかの判定
            if testx[self.feature[node]] <= self.threshold[node]:
                #nodeで指定される特徴量においてtestxの値が閾値を下回れば左へ下がる
                #print("{:<15} <= {:<10}".
                #      format(self.xn[self.feature[node]],self.threshold[node]))
                node=self.children_left[node]#左子ノードに移動
                nodelist.append(node)#ノード情報の記録
                directlist.append(-1)#通る道が左か右かの記録
            else:
                #print("{:<15} >  {:<10}".
                #      format(self.xn[self.feature[node]],self.threshold[node]))
                node=self.children_right[node]
                nodelist.append(node)
                directlist.append(1)
        
        #nodelist,directlistを基に使用する特徴量、閾値の整理
        featurelist=[]#使用する特徴量、重複はなし
        morelist=[]#testxを上回った閾値 上の特徴量リストに要素が対応
        lesslist=[]#testxを下回った閾値
        # ex)   featurelist  1  2  5  6  8
        #       morelist     10 ×　×　3　7
        #       lesslist     3　6　5　×　2
        for i in range(len(nodelist)-1):
            if self.feature[nodelist[i]] not in featurelist:
                #使う条件の特徴量が重複してなかったら新たに書き込み
                featurelist.append(self.feature[nodelist[i]])
                if directlist[i]==-1:
                    lesslist.append(None)
                    morelist.append(self.threshold[nodelist[i]])
                else:
                    lesslist.append(self.threshold[nodelist[i]])
                    morelist.append(None)
            else:#重複且つ閾値の範囲がより近づいたら上書き
                same=find_elements(featurelist,self.feature[nodelist[i]])
                if directlist[i]==-1: 
                    if morelist[same] is None or self.threshold[nodelist[i]]<morelist[same]:
                        morelist[same]=self.threshold[nodelist[i]]
                else:
                    if lesslist[same] is None or self.threshold[nodelist[i]]>lesslist[same]:
                        lesslist[same]=self.threshold[nodelist[i]]
        
        #表示
        if output==True:       
            for i in range(len(featurelist)):
                if morelist[i] is None:
                    print("{:<10} < {:<15}    {:<10}".
                        format(lesslist[i],self.xn[featurelist[i]]," "))
                elif lesslist[i] is None:
                    print("{:<10}   {:<15} <= {:<10}".
                        format(" ",self.xn[featurelist[i]],morelist[i]))
                else:
                    print("{:<10} < {:<15} <= {:<10}".
                        format(lesslist[i],self.xn[featurelist[i]],morelist[i]))
                
        
        pred=np.argmax(self.values[node])
        
        if output==True:
            if self.yn is None:
                print("class {}".format(pred))
            else:
                print("class {}".format(self.yn[pred]))
        
        return pred
                      

    def track_from_i_node(self,i):
        """指定ノードから根ノードまで追跡し各ノードで使われる特徴量を取得
        ※重複は省略

        Args:
            i (int): 追跡を始めるノード番号

        Returns:
            use_feature(set):使われる特徴量番号
        """
        use_feature=set()
        while self.mother_node[i]!=-1:
            i=self.mother_node[i]
            use_feature.add(self.feature[i])
        return use_feature
    
    def calculate_usef_ave(self,output=False):
        """決定木のある予測に対し使われる特徴量数の平均を求める

        Returns:
            self.avef: 特徴量数平均（葉ノードまでの特徴量数の平均）
        """
        n_feature_leaf_to_root=[]
        for i in range(self.n_nodes):
            if self.is_leaves[i]==True:
                f=self.track_from_i_node(i)
                n_feature_leaf_to_root.append(len(f))
        self.avef=sum(n_feature_leaf_to_root)/len(n_feature_leaf_to_root)
        if output==True:
            print("use_feature_num_average={}".format(self.avef))
        return self.avef
    
    def calculate_usef_all(self,output=False):
        """決定木全体で使われる特徴量とその数を返す

        Args:
            output (bool, optional): 結果を出力するか否か. Defaults to False.
        """
        feature=set(self.feature)
        feature.remove(np.int64(-2))
        print(feature)