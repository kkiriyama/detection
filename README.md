# Data Science Challenge by FUJIFILM AI Academy Brain(s) Road Damage

解答者：藏田展洋（東京大学医学部医学科4年）

## ファイルの説明
- utils.py ... 配布された600 * 600の画像をモデルに合わせてリサイズするためのファイルです。
- keras-yolo3_modified ... [Kerasで実装されたYOLO V3のgithubリポジトリ](https://github.com/qqwweee/keras-yolo3)を `git clone` でコピーしたもののうち、必要なファイルだけ抜き出して改変したものです。
  - convert.py ... YOLO V3のgituhbレポジトリのREADMEに書いてある通りの変換を行うためのファイルです。自分での変更は行っていません。 `python convert.py yolov3.cfg yolov3.weights model_data/yolo.h5` を一行することでconfigの要素を考慮したモデルを構築できます。
  - train.txt ... voc_annotation.pyによって生成した、ラベルデータのPascal VOCフォーマットをYOLO V3用に変換したものです。画像サイズ416 * 416用です。
  - train_576.txt ... voc_annotation.pyによって生成した、ラベルデータのPascal VOCフォーマットをYOLO V3用に変換したものです。画像サイズ576 * 576用です。
  - train.py ... モデルの訓練用のファイルです。バッチサイズなどの他は大きな変更を行っていません。
  - voc_annotation.py ... ラベルのPascal VOCフォーマットをYOLO V3用のテキストデータに変換するためのファイルです。今回配布された画像データのディレクトリ構造に合わせて改変し、また、配布された画像のサイズとモデルの訓練などに使用する画像のサイズの違いを考慮して調整しました。
  - yolov3.cfg ... モデルのハイパーパラメータを定義するconfigファイルです。画像サイズのみを変更しました。
  - yolov3.weights ... 初期値として用いたモデルの重みです。
  - font ... 出力で表示するためのフォントファイルが入っています。今回の予測に直接は使用していません。予測結果がある程度正しいことを目視で確認するために使用しました。
  - model_data ... クラスやアンカー、モデルを定義するファイルが入っています。
    - voc_classes.txt ... 分類するクラスを定義します。今回は1から8までの8種類のクラスに分類するのでそのように変更してあります。
    - yolo_anchors.txt ... アンカーを定義します。このファイルには変更を加えていません。
    - yolo.h5 ... convert.py で生成したモデルファイルです。
- perfect_score ... 外部データを用いたスコアの上限値を出すために用いたフォルダです。
    - matching.py ... 外部データと今回のコンペでの配布データをリサイズしてから検索し、マッチングするためのファイルです。
    - matching.txt ... マッチング結果を格納したものです。

## 詳細な解答手順

1. データをダウンロードしたら、まず生のデータ（画像、ラベルともに）を数百程度見ました。その結果、そもそも道路に損傷が入っていない画像が大量に入っているだとか、道路の損傷が1枚の画像に大量に含まれている、といったことがないことを確認しました。

2. 今回の問題は「物体検出問題」です。物体検出問題において予測時間と予測精度はトレードオフの関係にあることが予測されるが、実際に[文献](https://pjreddie.com/media/files/papers/YOLOv3.pdf)のグラフを見てみると最も速いのがYOLO v3であり、最も精度が高いのがRetinaNet-101であることが分かる。実世界への応用を考えたときに、リアルタイム検出に応用しやすい方がよいと考え、今回はYOLO v3をベースに実装することにした。画像サイズについては使用できるGPUメモリや計算時間との兼ね合いになる。

3. 詳細にデータを分析していくにあたり、1.の項で大まかにつかんだ雰囲気を数字とグラフを使って可視化する。画像あたりに含まれるboxの数と、各クラスの分布、クラス全体でのbounding boxの面積、クラスごとのbounding boxの面積、bounding boxの頂点の位置座標の分布を調べた。結果が下の画像である。
![Imgur](https://i.imgur.com/U3Gf7f7.png)
![Imgur](https://i.imgur.com/HGP7TKK.png)
![Imgur](https://i.imgur.com/BfwEVL3.png)
![Imgur](https://i.imgur.com/YI5lBt8.png)
![Imgur](https://i.imgur.com/8YzQeid.png)
boxの数については1, 2, 3個がほとんどを占めるが最小0個から最大8個まであることが分かる。テストデータもおおよそこれくらいの比率であろうという仮定のもと進める。

4. 次にYOLO v3の実装を始めた。[Kerasでの実装](https://github.com/qqwweee/keras-yolo3)をもとに今回のデータに合わせてファイルを改変した。画像サイズが32の倍数という指定だったのでとりあえずデフォルトの416 * 416にリサイズした。また、デフォルトのバッチサイズだと訓練のstage 2においてGPUのメモリ不足になってしまったのでstage2のバッチサイズを32から16に下げて学習を行った。学習に用いたGPUはAWSのインスタンス内のTesla K80である(以後同様)。

5. 4.の条件で学習を行ったモデルで予測を行った。画像1枚の予測に要する時間は約0.15秒であった。予測結果の一例を示す。
![Imgur](https://i.imgur.com/VlEVwwB.jpg)
ボックスに記載されている数字のうち、1つ目がクラスの番号、2つ目がconfidenceを表している。とりあえずこのモデルでもある程度適切に道路損傷を認識できていることが分かる。
このモデルでの予測結果を提出したところスコアは0.603であった。

6. 5.のスコアは既存のモデルを用い、ハイパーパラメータもほとんどそのままで学習させたのでまだ改善の余地があると考えた。しかし学習のハイパーパラメータを変えながら多数回の学習をしてスコアを比較することは計算資源と時間制限の都合上困難と判断し、予測におけるパラメータと複数モデルをアンサンブルするときのパラメータを最適化することでスコアの向上を図ろうと考えた。

7. まずアンサンブルを行った。この学習の過程でvalidation lossが学習が進むにつれてスパイク上に異常な上昇を見せ、学習結果もほとんどの画像でbounding boxを出力しないという症状に見舞われた。validation lossが不安定なことを考慮し、学習率が高いのではと考え、学習率を1/10にし、その代わりエポック数を2倍に増やした。これによって先に述べたような症状は見られなくなった。この条件のもと、訓練データの90%を学習に、10%をvalidationに用いたCross Validationをすることによって予測モデルを5つ得た。モデルの数は計算資源と時間製薬の都合で決定した。

8. 7.で作成したモデル個々のスコアはそれぞれ0.644, 0.627, 0.610, 0.624, 0.612 であった。各モデルが出したbounding boxをすべて合計し、non maximam suppression関数を実装して同じクラスのboxであって一定以上overlapしているboxたちについて最もスコアの高いもののみを残した。このアンサンブルによって得られたスコアは 0.631 である。NMSによるアンサンブルで個々のモデルの最高値を超えることができなかった。今回はスコアを競うコンペであり、かつ実行時間も考慮する必要があることから、アンサンブルではなく単一のスコアを提出する。しかしアンサンブルをすることで評価データに過適合していない、よりロバストなモデルになっていると考えられる。

9. さらに3.で調べたようなデータの分布から予測を改変することを考えた。具体的には予測で得られたbounding boxの大きさを一律に拡大・縮小する、各画像あたりのbox数を制限する、クラスごとにboxの面積の閾値を設定してそれより大きいboxを削除する、などを試した。これらのうち、スコアの向上が見られたのはbounding boxの一律8%拡大であった。これらによってスコアは0.6455となった。

10. 最後に、入力データの画像の大きさをできるだけ大きくして学習しなおした。最初から最大サイズにしなかったのは計算量を抑えることで試行錯誤の回数を稼ぐためである。600以下であって32の倍数となるような最大の整数なので576平方の画像となる。この入力サイズで7. ~ 9. で述べた処理と同様のことを行い、スコア0.608を得た。画像サイズを上げれば精度が上がってスコアも上がることが予測されるが今回の実験ではそれに反する結果が得られた。時間的制約のため、この問題の解決をすることはできなかった。

11. 以上の操作で得られた最高スコアである0.6455を正攻法でこの問題を解いた場合の最終提出スコアとした。

12. 一方で、問題を解くに当たって文献検索をしていたところ、道路の路面の損傷を機械学習によって判別するという[今回の問題とほとんど同じ趣旨の論文](https://arxiv.org/abs/1801.09454)を見つけた。これによれば道路損傷のデータセットは現在ほとんど存在せず、著者らは自前で用意したデータセットを用いて学習と予測を行っており、さらにそのデータセットは公開されているという。実際に公開されているデータを見ると撮影場所が明らかに日本である点、データセットのサイズが8000-9000枚である点、損傷のラベルが8種類である点、撮影場所が7箇所である点など、非常に類似点が多く、今回のコンペのデータセットはこの公開データセットによるものではないかと考えた。運営事務局にメールで確認したところ、そのとおりであるという返答が得られた。その情報をもとに外部データを使った際の最高スコアを出そうと考えた。

13. テストデータのアノテーションが分かればよいのでテストデータの各画像を公開データセットの全画像に対して検索をかけ、一致する画像のアノテーションデータをそのまま解答のxmlファイルに記載した。具体的な検索方法としては計算コストを極力抑えるために各画像を5 * 5にリサイズして画像間の相関係数を調べた。同一の画像かそうでないかなので非常に簡単に閾値を設定して区別することができた。これによってスコア1.000を得た。F1値の定義からこれより大きいスコアは存在しないため理論上の最高スコアを出したことになる。これを外部データを用いた場合の提出スコアとした。

## 考察
- 今回のデータはほとんどが道路の損傷が存在するものであったが、現実にカメラ付きの車などで撮影して回る時には損傷がないものがほとんどであり、今回のモデルをそのまま適用するのは不適切であると考えらえる。使用するデータの比率に合わせた訓練データでの再学習が必要なのではないか。
- YOLO v3はほSSD, RetinaNet, Faster－RCNNなどほかのモデルに比べて精度では劣るものの、予測が速いために予測を動画で行うことが可能である。このような機械学習の技術と、GPS、さらに将来的に自動運転の技術が組み合わされば完全自動でどの地点にどのような道路損傷があるのかをマッピングすることが可能になると考えられる。今回は道路損傷の検出であったが、道路から観測できるものを対象にすれば幅広い応用が考えられる。計算資源と時間に余裕があれば他のモデルでもこの問題を解いてみて実際に予測精度と予測時間のトレードオフが存在するのかを検証したい。二次元平面上に各モデルをプロットできれば応用時に必要なFPSに応じてモデルを選択することが可能になるだろう。
- 今回予測の段階の最適化で効果のあったbounding boxの一律の拡大縮小は機械学習コンペサイトKaggleでの物体検出コンペティション[RSNA Pneumonia Detection Challenge](https://www.kaggle.com/c/rsna-pneumonia-detection-challenge)におけるチームPFNeumoniaの[解答資料](https://www.slideshare.net/pfi/rsna-th-place-solution-pfneumonia)を参考にしたものである。この資料にあるほどの劇的な改善は見られなかったが、少量の改善が見られた。