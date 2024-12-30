import pandas as pd

def read_1gen(pas,run,gen,front1=False):
    """遺伝子に関するcsvデータを読み込みデータフレームを返す
    Args:
        pas (str):    参照するフォルダのパス
        run (integer):参照する実行回       
        gen (integer):参照する世代集団 
        front1 (bool):フロント0のデータ以外を消すか，否か
    Returns:
        df:全体の情報 para:遺伝子のパラメータf gene:遺伝子の入力x(list)
    """
    pas= pas + '/' + 'run' + str(run) + '/pop_g' + str(gen) + '.csv'
    df = pd.read_csv(pas)
    if front1==True:
        df=df[df["front"] == 0]
    para=df.loc[:,:"gene"]#parameter情報のみのデータフレーム
    gene=df.loc[:,"gene[0]":]
    df['gen']=gen
    df['run']=run 
    para['gen']=gen
    para['run']=run
    gene=gene.values.tolist()
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
        df,para,gene=read_1gen(pas,run,gen,front1)
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
        df,para,gene=read_1gen(pas,run,gen,front1)
        df_list.append(df)
        para_list.append(para)
        gene_list.append(gene)
    df=pd.concat(df_list)
    para=pd.concat(para_list)
    return df,para,gene_list

def read_rungenlist(pas,runlist,genlist):
    """指定したフォルダの指定した複数runにおける複数世代の解集団情報を参照，データフレームに直し結合
    Args:
        pas (str):              参照するフォルダのパス
        runlist (list(int)):    参照する実行回       
        genlist (list(int)):    参照する世代集団のリスト  
    Return:
        df,para(pddataframe):世代ごとの情報,末尾にrun,gen情報が追加
    """
    
    df_list=[]
    para_list=[]
    gene_list=[]
    for run in runlist:
        df,para,gene=read_genlist(pas,run,genlist)
        df_list.append(df)
        para_list.append(para)
    df=pd.concat(df_list)
    para=pd.concat(para_list)
    return df,para