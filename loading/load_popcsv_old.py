import pandas as pd

def rename_columns(para):#特徴量の名前変更はここから
    """遺伝子に関するテキストデータ、特にパラメータに関するデータについて
    各要素における特徴量の名前を定義する
    Args:
        para (pddataframe): 遺伝子のパラメータのみの情報があるデータフレーム
    Returns:
        repara:特徴量名を変更したデータフレーム
    """
    col=["AC","size","AC3","tr(i)","tr_per","te(j)","te_per","trust","match"]
    #problem3のwriteに書かれていること+遺伝子一致率採用可否を参照
    col2=["rank","CD"]
    #非支配ランク、混雑距離
    repara=para.set_axis(col+col2,axis='columns')
    return repara
    
def find_gene_index(g_df):
    """遺伝子データのテキストからパラメータと遺伝子の区切りである'gene'がある列を返す

    Args:
        g_df (pddataframe): 遺伝子データ

    Returns:
        i 区切りの列番号
    """
    sample=g_df.iloc[0]
    list=sample.tolist()
    i=0
    while list[i]!="gene":
        i+=1
    return i

def read_1gen(pas,run,gen,front1=False):
    """遺伝子に関するテキストデータを読み込みデータフレームを返す
    Args:
        pas (str):    参照するフォルダのパス
        run (integer):参照する実行回       
        gen (integer):参照する世代集団 
        front1 (bool):フロント0のデータ以外を消すか，否か
    Returns:
        df:全体の情報 para:遺伝子のパラメータf gene:遺伝子の入力x(list)
    """
    pas= pas + '/' + 'run' + str(run) + '/'
    file="pop_g" + str(gen) + ".txt"
    df = pd.read_csv(pas+file,header=None,sep=' ')
    i=find_gene_index(df)#遺伝子に関するtxtはパラメータ→遺伝子構成で書き込まれており、その境界となる行を探す
    if front1:
        df=df[df[i-2] == 0]#front0を抽出
    para=df.iloc[:,:i]#parameter情報のみのデータフレーム
    gene=df.iloc[:,i+1:]#遺伝子情報のみのデータフレーム
    para=rename_columns(para)
    df['gen']=gen
    df['run']=run 
    para['gen']=gen
    para['run']=run
    gene=gene.values.tolist()#リストに変換
    return df,para,gene

def read_runlist(pas,runlist,gen,front1=False):
    """指定したフォルダにおいて指定した世代のrunごとの解集団情報を参照、データフレームに直し結合
    Args:
        pas (str):                  参照するフォルダのパス
        runlist (list(int)):        参照する実行回のリスト      
        gen (int):                  参照する世代集団 
        front1 (bool):              フロント0のデータ以外を消すか，否か
    Return:
        df,para,gene(pddataframe):runごとの情報、末尾にrun,gen情報を追加(genlistはgeneごとlist)
    """
    df_list=[]
    para_list=[]
    gene_list=[]
    for run in runlist:
        p=pas
        df,para,gene=read_1gen(p,run,gen,front1)
        df_list.append(df)
        para_list.append(para)
        gene_list.append(gene)
    df=pd.concat(df_list)
    para=pd.concat(para_list)
    return df,para,gene_list

def read_genlist(pas,run,genlist,front1=False):
    """指定したフォルダの指定したrunにおける複数世代の解集団情報を参照，データフレームに直し結合
    Args:
        pas (str):              参照するフォルダのパス
        run (integer):          参照する実行回       
        genlist (list(int)):    参照する世代集団のリスト  
        front1 (bool):          フロント0のデータ以外を消すか，否か
    Return:
        df,para,gene(pddataframe):世代ごとの情報,末尾にrun,gen情報が追加
    """
    df_list=[]
    para_list=[]
    gene_list=[]
    for gen in genlist:
        p=pas
        df,para,gene=read_1gen(p,run,gen,front1)
        df_list.append(df)
        para_list.append(para)
        gene_list.append(gene)
    df=pd.concat(df_list)
    para=pd.concat(para_list)
    return df,para,gene_list

#df=read_1gen("../output/basic/test9_(digits_tr1300_seed1)_run[1, 2, 3, 4, 5]",1,0)
#print(df)