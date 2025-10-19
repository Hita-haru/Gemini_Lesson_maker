from google import genai
import json
import os
import re

client = genai.Client()

def main():
    print("AIプログラミングレッスンメーカー")
    lang = input("言語を入力 >")
    print(f"言語: {lang}で作成を開始します....\nファイル構造を作成しています....")
    responce_1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="あなたは経験豊富かつ優秀なプログラミングの講師です。これから" + lang + "（プログラミング言語）についての実際にプログラミングして勉強できるデジタル教材を作成してもらいます。初心者が基本をマスターできるレベルをゴールとし、学習者が挫折しないよう最適な章の構成を考え、各章に分けてファイルの名前と拡張子を.で区切った文字列を「filename」キーに（ファイル名と拡張子の区切り以外にピリオドを用いてはいけません。）、どのような内容にするかを書いた指示（指示のみ出力し、本文は出力しない）を「config」キーに入れ出力してください。それ以外は出力しないでください。もし言語がプログラミング言語ではなければERRORと返してください。",
        config={
            "response_mime_type": "application/json"
        }
    )
    if (responce_1.text == "ERROR"):
        print("ファイルの作成に失敗しました。\n予想される問題: >言語がプログラミング言語ではない<\n強制終了します....")
        exit()
    
    response_text = responce_1.text

    start_index = response_text.find('[')
    end_index = response_text.rfind(']')

    json_text = response_text[start_index:end_index+1]
    chapters = json.loads(json_text)

    file_number = 1

    os.makedirs("lessons", exist_ok=True)
    for chapter in chapters:
        filename = os.path.splitext(chapter["filename"])[1]
        file_path = os.path.join("lessons", str(file_number) + filename)
        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(chapter["config"])
        print(f"作成が完了しました: {file_path}\n{file_number}個目のファイルを作成しました")
        file_number += 1

    print("ファイル構成を作成しました。ファイルの内容を作成します。\nこの作業には時間がかかります。少々お待ち下さい....")

    # Supported MIME types by the API
    supported_mime_types = {
        ".json": "application/json",
        ".xml": "application/xml",
        ".yaml": "application/yaml",
    }

    for i in range(1, file_number):
        extension = os.path.splitext(chapters[i-1]["filename"])[1]
        file_path = os.path.join("lessons", str(i) + extension)
        
        with open(file_path, "r", encoding = "utf-8") as f:
            instruction = f.read()
        
        # Use the supported mime type if available, otherwise default to text/plain
        mime_type = supported_mime_types.get(extension.lower(), "text/plain")

        # Create a new, more explicit prompt with examples
        new_prompt = f'''あなたは経験豊富かつ優秀なプログラミングの講師です。
ファイル名「{file_path}」のレッスン内容を以下の指示に従って作成してください。

【最重要指示】出力形式は必ずファイル拡張子に合わせてください。

- `.html` ファイルには、HTMLのみを出力してください。
- `.md` ファイルには、マークダウンのみを出力してください。
- ソースコードのファイル（例: `.js`, `.py`, `.java`）には、その言語で実行可能な有効なコード「のみ」を出力してください。
- コードファイル内の説明は、その言語の標準的なコメント（例: JavaScriptなら `//`、Pythonなら `#`）を使い、ごく簡潔にしてください。

【悪い例（.jsファイルの場合）】
```javascript
/*
 * ## 第2章: 変数
 * この章では変数について学びます。変数とは、データを格納するための箱のようなものです...
 * （ここに長文の説明が続く）
 */
let x = 10;
console.log("これが変数です:", x);
```

【良い例（.jsファイルの場合）】
```javascript
// 第2章: 変数

// `let` は再代入が可能な変数を宣言します。
let x = 10;
x = 20; // 再代入

// `const` は値が変更できない定数を宣言します。
const y = 5;

// コンソールに値を出力します。
console.log("xの値:", x);
console.log("yの値:", y);
```

では、この指示に従って内容を生成してください。
指示：
{instruction}
'''

        responce_2 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=new_prompt,
            config={
                "response_mime_type": mime_type
            }
        )
        
        generated_text = responce_2.text
        # Check if the output contains a markdown code block and the file is not a markdown file
        match = re.search(r"```(?:[a-zA-Z]*)?\s*\n(.*?)```", generated_text, re.DOTALL)
        
        content_to_write = generated_text
        if match and extension.lower() != ".md":
            # If a code block is found, extract the code from the first group
            print(f"コードブロックを検出しました。内容を抽出します。 file: {file_path}")
            content_to_write = match.group(1)
        else:
            # This is for debugging to see what the model is returning
            print(f"コードブロックが見つかりませんでした。そのまま書き込みます。 file: {file_path}")

        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(content_to_write)
        print(f"作成が完了しました: {file_path}\n{i}個目のファイルの内容を作成しました")

if __name__ == "__main__":
    main()