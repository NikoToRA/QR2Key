# QR2Key - UTM Windows 実行ガイド

このガイドでは、Mac上のUTM仮想環境でQR2Keyアプリケーションを実行する方法を説明します。

## 前提条件

- Mac上にUTM（仮想マシンマネージャー）がインストールされていること
- UTM上でWindowsが既に実行されていること
- Windowsに以下がインストールされていること：
  - Python 3.10以上
  - Git（オプション）

## 手順

### 1. QR2Keyリポジトリの取得

**オプション1: GitHubからダウンロード**

1. UTM上のWindowsでブラウザを開き、以下のURLにアクセスします：
   ```
   https://github.com/NikoToRA/QR2Key/tree/devin/1746521018-fix-ci-workflow
   ```

2. 緑色の「Code」ボタンをクリックし、「Download ZIP」を選択します。

3. ダウンロードしたZIPファイルを任意の場所に展開します。

**オプション2: Gitを使用（Gitがインストールされている場合）**

1. コマンドプロンプトまたはPowerShellを開きます。

2. 以下のコマンドを実行してリポジトリをクローンします：
   ```
   git clone https://github.com/NikoToRA/QR2Key.git
   cd QR2Key
   git checkout devin/1746521018-fix-ci-workflow
   ```

### 2. 必要なパッケージのインストール

1. コマンドプロンプトまたはPowerShellを開き、QR2Keyフォルダに移動します。

2. 以下のコマンドを実行して必要なパッケージをインストールします：
   ```
   pip install -r requirements.txt
   pip install -r requirements-win.txt
   ```

### 3. アプリケーションの実行

**方法1: 直接実行**

1. QR2Keyフォルダ内で以下のコマンドを実行します：
   ```
   python run_qr2key.py
   ```

2. アプリケーションが起動し、暗号鍵とQRコードが生成されます。

**方法2: 実行ファイルの作成と実行（オプション）**

1. 以下のコマンドを実行してPyInstallerをインストールします：
   ```
   pip install pyinstaller
   ```

2. QR2Keyフォルダ内で以下のコマンドを実行して実行ファイルを作成します：
   ```
   pyinstaller --clean --add-data "README.md;." --onefile --name "QR2Key" qr2key/main.py
   ```

3. 作成された実行ファイル（`dist\QR2Key.exe`）を実行します。

## トラブルシューティング

- **依存関係のエラー**: `pip install -r requirements.txt` と `pip install -r requirements-win.txt` を実行して必要なパッケージがすべてインストールされていることを確認してください。

- **pywin32のエラー**: Windowsでpywin32のインストールに問題がある場合は、以下のコマンドを試してください：
  ```
  pip install --upgrade pywin32
  ```

- **実行時のエラー**: アプリケーションが起動しない場合は、Pythonのバージョンが3.10以上であることを確認してください。

## 機能

- 暗号鍵の生成
- QRコードへの変換
- クリップボードへのコピー（Windows専用機能）

## 注意事項

- このアプリケーションはWindows環境で最適に動作します。
- クリップボード機能はWindows専用です。
