
# 基本仕様書：シンプルオセロゲーム (ロジック解説)

1. はじめに

このドキュメントは、提供されたPythonコードで実装されたシンプルオセロゲームの基本的な構造とロジックを解説するものです。コードは主に定数定義、Boardクラス（盤面の状態管理）、OthelloGameクラス（ゲーム全体の制御）、およびメイン実行部分から構成されます。
Gemini2.5Pro を利用してプログラムも仕様書も作成しています。

2. 定数定義 (# --- 定数 ---)

プログラム全体で使用される固定値を定義しています。

    WIDTH, HEIGHT: ゲームウィンドウの幅と高さをピクセル単位で定義します。HEIGHTがWIDTHより大きいのは、盤面の下にスコアなどを表示するスペースを確保するためです。　
    ROWS, COLS: 盤面の行数と列数（8x8）を定義します。　
    SQUARE_SIZE: 盤面の1マスの辺の長さを計算します。ウィンドウ幅を列数+1（左右の余白分）で割ることで、左右に少し余白ができるように調整しています。　
    BOARD_OFFSET_X, BOARD_OFFSET_Y: 盤面を描画する際の左上の座標オフセット（余白）を定義します。　
    WHITE, BLACK, GREEN, GRAY, GOLD, RED: ゲーム内で使用する色をRGBタプルで定義します。GOLDは有効な手を示すマーカーの色、REDは結果表示などに使われます。　
    EMPTY, BLACK_PLAYER, WHITE_PLAYER: 盤面の各マスの状態を表す整数値を定義します。0は空きマス、1は黒石、2は白石を示します。

3. Boardクラス (# --- ゲーム盤クラス ---)

ゲーム盤の状態管理と、盤面に関連する基本的な操作を担当します。

    __init__(self) (コンストラクタ)
        ロジック: Boardオブジェクトが生成される際に呼び出されます。
        self.board: 8x8の2次元リストを作成し、すべてのマスをEMPTY (0) で初期化します。これがゲーム盤の状態を表します。
        初期配置: 盤面中央の4マス (インデックス[3][3], [3][4], [4][3], [4][4]) に白石 (WHITE_PLAYER) と黒石 (BLACK_PLAYER) を交互に配置します。
        self.black_score, self.white_score: 初期状態（各2個）のスコアを初期化します。
    draw_squares(self, screen)
        ロジック: Pygameの描画機能を使って、ゲーム盤の背景と格子線を描画します。
        screen.fill(GREEN): 画面全体を緑色で塗りつぶします。
        forループ: ROWSとCOLSを使い、8x8のすべてのマスに対して処理を行います。
        pygame.draw.rect(): 各マスの位置に、黒色(BLACK)で枠線 (width=1) の四角形を描画します。座標計算にはBOARD_OFFSET_X, BOARD_OFFSET_Y, SQUARE_SIZEを使用します。
    draw_pieces(self, screen)
        ロジック: self.boardの現在の状態に基づいて、盤面上の石を描画します。
        radius: 石（円）の半径を計算します（マスサイズより少し小さい）。
        forループ: 8x8のすべてのマスをチェックします。
        center_x, center_y: 各マスの中心座標を計算します。
        if self.board[row][col] == ...: マスの状態がBLACK_PLAYERまたはWHITE_PLAYERの場合、対応する色 (BLACKまたはWHITE) でpygame.draw.circle()を使い円を描画します。
    is_valid_move(self, player, row, col)
        ロジック: 指定された(row, col)が、指定されたplayerにとって石を置ける有効な手かどうかを判定し、もし有効な手であればひっくり返せる相手の石の座標リストを返します。有効でない場合は空のリストを返します。
        初期チェック:
            指定された(row, col)が盤面の範囲内 (0 <= row < ROWS and 0 <= col < COLS) かどうか。
            指定されたマスが空きマス (self.board[row][col] == EMPTY) かどうか。
            どちらかの条件を満たさない場合は、空リスト[]を返して終了します。
        opponent: playerに応じて相手プレイヤーの色を決定します。
        tiles_to_flip: この手に置いた場合にひっくり返る石の座標を格納するリスト。
        8方向探索: for dr, dc in [...]: 現在のマス(row, col)から見て、上下左右斜めの8方向についてチェックを行います。(dr, dc)は各方向への移動量（例: (0, 1)は右、(1, -1)は右下）。
            temp_flip: 各方向で一時的にひっくり返せる可能性のある石を格納するリスト。
            r, c = row + dr, col + dc: チェックする方向の隣のマス座標を計算。
            条件1: 隣が相手の石か？
                隣のマス(r, c)が盤面内で、かつ相手(opponent)の石であるかチェック。
                条件を満たせば、その座標をtemp_flipに追加し、さらにその方向に進みます (r += dr, c += dc)。
            条件2: その先に相手の石が続くか？
                whileループ: 盤面内で、かつ相手の石が続く限り、その座標をtemp_flipに追加し、さらにその方向に進みます。
            条件3: 最後に自分の石があるか？
                whileループを抜けた後、最後に到達したマス(r, c)が盤面内で、かつ自分(player)の石であるかチェック。
                この条件を満たせば、temp_flipに格納された石（挟まれた相手の石）はすべてひっくり返せることが確定します。tiles_to_flip.extend(temp_flip)で、確定したリストを最終的なリストに追加します。
        戻り値: 8方向すべてをチェックした後、最終的にtiles_to_flipリストを返します。有効な手であれば1つ以上の座標が、そうでなければ空のリストが返ります。
    get_valid_moves(self, player)
        ロジック: 指定されたplayerが現在打つことができるすべての有効な手の座標と、それぞれの手に置いた場合にひっくり返る石のリストを辞書形式で返します。
        valid_moves = {}: 結果を格納する空の辞書を初期化します。キーが(row, col)、値がtiles_to_flipリストです。
        forループ: 盤面のすべてのマス (r, c) について繰り返し処理を行います。
        flip_list = self.is_valid_move(player, r, c): 各マスについて、有効な手かどうか、ひっくり返せる石は何かをis_valid_moveでチェックします。
        if flip_list:: is_valid_moveが空でないリスト（つまり有効な手）を返した場合、その座標(r, c)とひっくり返る石のリストflip_listをvalid_moves辞書に追加します。
        戻り値: valid_moves辞書を返します。
    make_move(self, player, row, col, tiles_to_flip)
        ロジック: プレイヤーが指定したマスに石を置き、tiles_to_flipリストに基づいて相手の石をひっくり返します。
        入力チェック(念のため): tiles_to_flipが空でなく、かつ置くマスが空であることを確認します（通常はhandle_clickでvalid_movesを元に呼び出されるため不要なはずですが、安全のためのチェック）。問題があればエラーメッセージを表示しFalseを返します。
        self.board[row][col] = player: 指定されたマス(row, col)にplayerの石を置きます（盤面データを更新）。
        for r_flip, c_flip in tiles_to_flip:: ひっくり返す石のリストtiles_to_flipをループ処理します。
        self.board[r_flip][c_flip] = player: リスト内の各座標の石をplayerの色に更新（ひっくり返す）します。
        self.update_score(): 石の配置と反転が完了した後、現在の盤面に基づいてスコアを再計算します。
        戻り値: 処理が正常に完了したことを示すTrueを返します。
    update_score(self)
        ロジック: 現在の盤面 (self.board) 上のすべての石を数え、黒と白それぞれのスコア (self.black_score, self.white_score) を更新します。
        スコアを一旦0にリセットします。
        forループ: 8x8のすべてのマスをチェックします。
        if/elif: マスの状態がBLACK_PLAYERならself.black_scoreを、WHITE_PLAYERならself.white_scoreを1増やします。
    get_score(self)
        ロジック: 現在の黒と白のスコアをタプル (black_score, white_score) として返します。

4. OthelloGameクラス (# --- ゲーム管理クラス ---)

ゲーム全体の流れ、イベント処理、画面描画の統合を担当します。

    __init__(self, screen) (コンストラクタ)
        ロジック: OthelloGameオブジェクトが生成される際に呼び出され、ゲーム全体を初期化します。
        self.screen: 描画対象となるPygameの画面オブジェクトを保持します。
        self.board = Board(): Boardクラスのインスタンスを作成し、ゲーム盤を初期化します。
        self.current_player = BLACK_PLAYER: ゲームの最初のプレイヤーを黒に設定します。
        self.valid_moves = self.board.get_valid_moves(self.current_player): 開始時のプレイヤー（黒）が打てる有効な手のリストを計算して保持します。
        self.game_over = False: ゲームが進行中であることを示すフラグを初期化します。
        self.winner = None: 勝者を格納する変数を初期化します (None: 未定, BLACK_PLAYER: 黒の勝ち, WHITE_PLAYER: 白の勝ち, EMPTY: 引き分け)。
        フォント初期化:
            pygame.font.init(): Pygameのフォントモジュールを初期化します。
            pygame.font.SysFont(): スコアやメッセージ表示用のフォントオブジェクトを準備します。日本語表示のために "Noto Serif CJK JP" を試み、失敗した場合はデフォルトフォントを使用するフォールバック処理が含まれています（文字化けの可能性あり）。
    switch_player(self)
        ロジック: 現在のプレイヤーを交代し、交代後のプレイヤーの有効な手を確認します。パスやゲーム終了の判定もここで行います。
        self.current_player = ...: 三項演算子を使ってプレイヤーを交代します（黒なら白へ、白なら黒へ）。
        self.valid_moves = self.board.get_valid_moves(self.current_player): 交代後のプレイヤーの有効な手を再計算します。
        パス・ゲーム終了判定:
            if not self.valid_moves:: 交代後のプレイヤーに有効な手がない場合。
                opponent = ...: 相手プレイヤー（元のプレイヤー）を特定します。
                opponent_valid_moves = self.board.get_valid_moves(opponent): 相手プレイヤーに有効な手があるか調べます。
                if not opponent_valid_moves:: 相手プレイヤーにも有効な手がない場合、両者とも打てないのでゲーム終了です。
                    self.game_over = True: ゲーム終了フラグを立てます。
                    b_score, w_score = self.board.get_score(): 最終スコアを取得します。
                    スコアを比較し、self.winnerに勝者（または引き分けEMPTY）を設定します。
                else:: 相手プレイヤーには有効な手がある場合（現在のプレイヤーのみパス）。
                    コンソールにパスが発生したことを示すメッセージを出力します。
                    重要: このコードでは、パスの場合、自動的に相手にターンが渡るのではなく、self.current_playerを相手に戻し、self.valid_movesを相手のものに更新しています。これにより、次のクリックイベントはパスしなかった相手プレイヤーの操作として扱われます（画面上のターン表示は一時的にパスしたプレイヤーのままですが、内部的には相手のターンになっています）。
    handle_click(self, pos)
        ロジック: プレイヤーがマウスをクリックした際の処理を行います。
        if self.game_over:: ゲームが終了していれば、何も処理しません。
        座標変換: pos（クリックされた画面上のXY座標）を、盤面の行(row)と列(col)のインデックスに変換します。BOARD_OFFSET_X, BOARD_OFFSET_Y, SQUARE_SIZE を使って計算します。
        if (row, col) in self.valid_moves:: 変換した盤面座標 (row, col) が、現在のプレイヤーの有効な手のリスト self.valid_moves に含まれているか確認します。
            含まれている場合（有効な手がクリックされた場合）:
                tiles_to_flip = self.valid_moves[(row, col)]: その手でひっくり返る石のリストを取得します。
                self.board.make_move(...): Boardオブジェクトのmake_moveメソッドを呼び出し、石を置き、相手の石をひっくり返します。
                if self.board.make_move(...): make_moveが成功したら（通常は成功するはず）、self.switch_player()を呼び出してプレイヤーを交代し、次のターンの準備をします。
    draw_valid_moves(self)
        ロジック: 現在のプレイヤーが打てる有効な手のマスに、目印となる小さな金色の円を描画します。
        radius: マーカー（円）の半径を定義します。
        for r, c in self.valid_moves.keys():: 有効な手の座標リスト（辞書のキー）をループ処理します。
        center_x, center_y: 各有効な手のマスの中心座標を計算します。
        pygame.draw.circle(): 計算した中心座標に、金色(GOLD)で小さな円を描画します。
    draw_status(self)
        ロジック: 画面下部にゲームのステータス情報（スコア、現在のターン、ゲーム結果など）を描画します。
        b_score, w_score = self.board.get_score(): 現在のスコアを取得します。
        score_text = ...: スコア表示用の文字列を作成します。
        self.font.render(): フォントオブジェクトを使って、文字列を画像（Surfaceオブジェクト）に変換します。Trueはアンチエイリアスを有効にします。
        get_rect(): 作成したテキスト画像の矩形情報を取得し、center=を使って表示位置（画面中央下部）を調整します。
        self.screen.blit(): テキスト画像を画面に描画します。
        ターン表示 (ゲーム進行中のみ):
            if not self.game_over:: ゲームが終了していない場合にのみ実行します。
            ターン表示用の文字列を作成し、上記と同様の手順で描画します。
            pygame.draw.rect(..., GRAY, ...): ターン表示テキストの背景に灰色の矩形を描画し、文字を見やすくしています（オプション）。
            パスに関する注意書き（コメントアウトされています）も同様に描画できます。
        結果表示 (ゲーム終了後のみ):
            else:: ゲームが終了している場合に実行します。
            self.winnerの値に応じて結果表示用の文字列を作成します。
            上記と同様の手順で、結果文字列を赤色(RED)で画面に描画します。
    run(self)
        ロジック: ゲームのメインループを管理します。このループ内でイベント処理、ゲーム状態の更新、画面描画が繰り返されます。
        running = True: ループを継続するためのフラグ。
        clock = pygame.time.Clock(): フレームレートを制御するためのClockオブジェクトを作成します。
        while running: (メインループ):
            イベント処理: for event in pygame.event.get():
                if event.type == pygame.QUIT:: ウィンドウの閉じるボタンがクリックされたら、runningフラグをFalseにしてループを終了させます。
                if event.type == pygame.MOUSEBUTTONDOWN:: マウスボタンがクリックされたら、self.handle_click(event.pos)を呼び出してクリック処理を行います。event.posにはクリックされた座標が格納されています。
            描画処理:
                self.board.draw_squares(self.screen): 盤面の格子線を描画します。
                self.board.draw_pieces(self.screen): 盤面の石を描画します。
                if not self.game_over: self.draw_valid_moves(): ゲームが進行中なら、有効な手のマーカーを描画します。
                self.draw_status(): スコアやターンなどのステータス情報を描画します。
            画面更新:
                pygame.display.flip(): これまでに行われた全ての描画処理の結果を実際の画面に反映させます。
                clock.tick(60): ループの実行速度を最大60フレーム/秒に制限します。これにより、CPU負荷を抑え、アニメーションなどが適切な速度で表示されます。
        ループ終了後:
            pygame.quit(): Pygameのモジュールを終了します。
            sys.exit(): Pythonプログラムを終了します。

5. メイン処理 (if __name__ == '__main__':)

このブロックは、このスクリプトが直接実行された場合にのみ実行されます。

    pygame.init(): Pygameライブラリ全体を初期化します。
    screen = pygame.display.set_mode((WIDTH, HEIGHT)): 定義された幅と高さでゲームウィンドウ（画面Surface）を作成します。
    pygame.display.set_caption("シンプルオセロ"): ウィンドウのタイトルバーに表示されるテキストを設定します。
    game = OthelloGame(screen): OthelloGameクラスのインスタンスを作成し、ゲームオブジェクトを初期化します。作成したscreenオブジェクトを渡します。
    game.run(): ゲームオブジェクトのrunメソッドを呼び出し、ゲームのメインループを開始します。

6. 処理フローの概要

    初期化: Pygameとゲームオブジェクト(OthelloGame)を初期化。盤面(Board)も初期化され、初期配置とスコアが設定される。最初のプレイヤー（黒）の有効な手が計算される。　
    メインループ開始 (game.run()): 
        イベント待機: ユーザーからの入力（マウスクリック、閉じるボタン）を待つ。 
        イベント処理: 
            閉じるボタン → ループ終了へ。 
            マウスクリック → handle_click実行。 
                クリック座標を盤面座標に変換。 
                有効な手か判定 (valid_movesをチェック)。 
                有効なら board.make_move で石を置き、反転。 
                switch_player でプレイヤー交代、次の手の有効手計算、パス/終了判定。 
        画面描画: 盤面、石、有効な手（ゲーム中のみ）、ステータス（スコア、ターン/結果）を描画バッファに書き込む。 
        画面更新: 描画バッファの内容を実際のウィンドウに表示 (pygame.display.flip())。 
        フレームレート制御: clock.tick() でループ速度を調整。 
        ループの先頭に戻る。 
    ループ終了: runningフラグがFalseになるとループを抜ける。 
    終了処理: Pygameを終了し、プログラムを終了する。 