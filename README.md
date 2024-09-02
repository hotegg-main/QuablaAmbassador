Quabla Ambassador
==
Support Tool for execution of Quabla

# Features
* 安全審査書のエクセル形式の諸元表をもとに，Quablaで使用するjson形式のconfigファイルの算出
* 入力された空力的安定微係数のBarrowman Methodとの比較

# Execution
`gui.py`を故マインドライン引数なしで実行する。
```
$ python gui.py
```
GUIツールの入力項目を全て埋めたのち，`create`ボタンを押すと，
Result Directoryで指定したフォルダにconfigファイルなどが出力される。

# Caution
* 以下の諸量は大まかなきめうちの値で推算した。
    * 酸化剤質量（$=800\ \mathrm{kg/m^3}$），酸化剤タンク容量
    * グレイン密度（$=1.00\times10^3\ \mathrm{ kg/m^3}$）；グレイン直径，酸化剤タンク直径

# Future Work
* エクセルを読み込んだと同時にモデル名などの表示
* プロセスバーの表示
* 推力履歴解析
* varをinitに移動
* 諸元エラーチェック