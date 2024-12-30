import numpy as np

def accuracy_DTinfo(DTinfo,Xte,yte,Xname):
    """DTinfoにおける決定木精度計測

    Args:
        DTinfo (DTinfo): パラメータフィット済みDTinfo
        Xte (ndarray): 入力テストデータ
        yte (ndarray): 出力テストデータ
        Xname (list): 特徴量名リスト

    Returns:
            accuracy: 精度
    """
    adoption=search_match_xn(Xname,DTinfo.xn)
    sXte=delete_x(Xte,adoption)#DTinfoに合わせテストデータの特徴量削除
    count=0
    for i in range(len(sXte)):
        pred = DTinfo.predict(sXte[i],output=False)#DTinfoの予測
        if pred==yte[i]:#答えとの照らし合わせ
            count+=1#正解したらカウント
    accuracy=count/len(yte)
    return accuracy 

def search_match_xn(xn,sxn):
    """リストxnに対しリストsxnと同じ値があればその要素の値を1なければ0のリストを返す
    *もし重複する特徴量名があれば使えない
    Args:
        xn (list): リストxn 全特徴量名を想定
        sxn (list): リストsxn 削減特徴量名を想定

    Returns:
        match_list: バイナリの一致1or不一致0リスト
    """
    match_list=[]
    for i in range(len(xn)):
        if xn[i] in sxn:
            match_list.append(1)
        else:
            match_list.append(0)
    return match_list

def delete_x(Xdata,adoption):
    """adoptionで0となっているインデックスに対応するXdataの特徴量列を削除

    Args:
        Xdata (ndarray): 入力データセット
        adoption (list): 0、1で示されるリスト

    Returns:
        sXdata: 特徴量削減データ
    """
    notadx_index=[]
    for i in range(len(adoption)):
        if adoption[i]==0:
            notadx_index.append(i)
    sXdata=np.delete(Xdata,notadx_index,1)
    return sXdata